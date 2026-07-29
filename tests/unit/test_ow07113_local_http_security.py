"""OW-071-13 negative security tests for the local HTTP control plane."""

from __future__ import annotations

import http.client
import json
import pathlib
import tempfile
import threading
import unittest

from tools import owledge_core as core


class LocalHttpSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        core.init_project(self.root)
        self.admin_token = core.admin_token_path(self.root).read_text(encoding="utf-8").strip()
        self.tokens: dict[str, str] = {}
        agents = [
            ("planner-a", "planner", "tenant-a", "customer-a", "project-a"),
            ("planner-a2", "planner", "tenant-a", "customer-other", "project-other"),
            ("worker-a", "worker", "tenant-a", "customer-a", "project-a"),
            ("qa-a", "qa-agent", "tenant-a", "customer-a", "project-a"),
            ("curator-a", "memory-curator", "tenant-a", "customer-a", "project-a"),
            ("planner-b", "planner", "tenant-b", "customer-b", "project-b"),
            ("worker-b", "worker", "tenant-b", "customer-b", "project-b"),
        ]
        with core.contextlib.closing(core.connect(self.root)) as conn, conn:
            core.init_db(conn)
            for agent_id, role, tenant, customer, project in agents:
                result = core.register_agent(
                    conn,
                    {
                        "agent_id": agent_id,
                        "role": role,
                        "tenant_id": tenant,
                        "customer_id": customer,
                        "project_id": project,
                    },
                )
                self.tokens[agent_id] = result["token"]
        self.server = core.ThreadedHTTPServer(("127.0.0.1", 0), core.make_handler(self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self._tmp.cleanup()

    def request(
        self,
        method: str,
        path: str,
        body: dict | list | bytes | None = None,
        token: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict]:
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        payload = None
        request_headers = dict(headers or {})
        if body is not None:
            payload = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/json")
        if token:
            request_headers["Authorization"] = f"Bearer {token}"
        conn.request(method, path, body=payload, headers=request_headers)
        response = conn.getresponse()
        raw = response.read()
        conn.close()
        return response.status, json.loads(raw or b"{}")

    def create_task(self, task_id: str = "task-a", token_name: str = "planner-a") -> tuple[int, dict]:
        return self.request(
            "POST",
            "/tasks",
            {"task_id": task_id, "status": "ready", "qa_gate_ids": ["gate-a"]},
            self.tokens[token_name],
        )

    def test_contract_matches_runtime_policy(self) -> None:
        contract = json.loads(
            (pathlib.Path(__file__).parents[2] / "contracts" / "local-http-control-plane-v1.json").read_text(
                encoding="utf-8"
            )
        )
        endpoint_policy = [
            (entry["method"], entry["path"], tuple(entry["roles"])) for entry in contract["endpoints"]
        ]
        self.assertEqual(contract["maturity"], core.LOCAL_HTTP_PROFILE)
        self.assertEqual(contract["bounds"], core.LOCAL_HTTP_BOUNDS)
        self.assertEqual(endpoint_policy, list(core.LOCAL_HTTP_ENDPOINT_POLICY))

    def test_non_loopback_is_rejected_before_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = pathlib.Path(raw)
            with self.assertRaises(SystemExit):
                core.serve(target, "0.0.0.0", 0)
            self.assertFalse((target / ".agent-control").exists())
        self.assertIn("::1", core.LOCAL_HTTP_LOOPBACK_HOSTS)

    def test_health_is_sanitized_and_metrics_are_admin_only(self) -> None:
        status, health = self.request("GET", "/health")
        self.assertEqual((status, set(health)), (200, {"status", "profile", "api_version"}))
        status, payload = self.request("GET", "/metrics", token=self.tokens["planner-a"])
        self.assertEqual((status, payload["error"]), (403, "administrator_required"))
        status, payload = self.request("GET", "/metrics", token=self.admin_token)
        self.assertEqual(status, 200)
        self.assertIn("total_agents", payload)

    def test_role_matrix_and_administrator_scope_boundary(self) -> None:
        status, payload = self.create_task(token_name="worker-a")
        self.assertEqual((status, payload["error"]), (403, "role_not_authorized"))
        status, payload = self.create_task()
        self.assertEqual((status, payload["task_id"]), (200, "task-a"))
        status, payload = self.request("POST", "/tasks", {"task_id": "admin-task"}, self.admin_token)
        self.assertEqual((status, payload["error"]), (403, "administrator_scope_forbidden"))

    def test_authenticated_identity_cannot_be_spoofed(self) -> None:
        self.create_task()
        status, payload = self.request(
            "POST",
            "/tasks/task-a/claim",
            {"agent_id": "worker-b"},
            self.tokens["worker-a"],
        )
        self.assertEqual((status, payload["error"]), (403, "actor_identity_mismatch"))
        status, _ = self.request("POST", "/tasks/task-a/claim", {}, self.tokens["worker-a"])
        self.assertEqual(status, 200)
        status, payload = self.request(
            "PATCH",
            "/tasks/task-a",
            {"status": "in_progress", "agent_id": "worker-b"},
            self.tokens["worker-a"],
        )
        self.assertEqual((status, payload["error"]), (403, "actor_identity_mismatch"))

    def test_full_scope_blocks_same_tenant_cross_project_access(self) -> None:
        self.create_task()
        status, payload = self.request(
            "POST",
            "/context-pack/build",
            {"task_id": "task-a"},
            self.tokens["planner-a2"],
        )
        self.assertEqual((status, payload["error"]), (403, "scope_boundary_violation"))
        status, payload = self.request(
            "POST",
            "/tasks",
            {"task_id": "task-a"},
            self.tokens["planner-b"],
        )
        self.assertEqual((status, payload["error"]), (403, "scope_boundary_violation"))

    def test_resource_identifier_collisions_fail_closed(self) -> None:
        self.create_task()
        self.request("POST", "/tasks/task-a/claim", {}, self.tokens["worker-a"])
        status, _ = self.request(
            "POST",
            "/gates/gate-shared/run",
            {"task_id": "task-a", "final_verdict": "pass"},
            self.tokens["qa-a"],
        )
        self.assertEqual(status, 200)
        self.create_task("task-b")
        status, payload = self.request(
            "POST",
            "/gates/gate-shared/run",
            {"task_id": "task-b", "final_verdict": "pass"},
            self.tokens["qa-a"],
        )
        self.assertEqual((status, payload["error"]), (409, "resource_conflict"))
        with core.contextlib.closing(core.connect(self.root)) as conn, conn:
            conn.execute(
                """INSERT INTO promotions(
                    promotion_id, tenant_id, customer_id, project_id,
                    source_path, target_path, review_path, status, created_at
                ) VALUES (?, ?, ?, ?, '', '', '', 'promoted', ?)""",
                ("promo-shared", "tenant-b", "customer-b", "project-b", core.utc_now()),
            )
            with self.assertRaisesRegex(PermissionError, "scope_boundary_violation"):
                core.promote_memory(
                    conn,
                    self.root,
                    {
                        "promotion_id": "promo-shared",
                        "tenant_id": "tenant-a",
                        "customer_id": "customer-a",
                        "project_id": "project-a",
                    },
                )

    def test_body_boundary_and_unsupported_method_are_stable_json(self) -> None:
        oversized = b"{" + b" " * core.LOCAL_HTTP_BOUNDS["max_body_bytes"]
        status, payload = self.request(
            "POST",
            "/tasks",
            oversized,
            self.tokens["planner-a"],
            {"Content-Length": str(len(oversized))},
        )
        self.assertEqual((status, payload["error"]), (413, "payload_too_large"))
        status, payload = self.request("PUT", "/health")
        self.assertEqual((status, payload["error"]), (405, "method_not_allowed"))

    def test_rate_and_concurrency_limits_are_explicit(self) -> None:
        isolated = core.ThreadedHTTPServer(("127.0.0.1", 0), core.make_handler(self.root))
        try:
            for _ in range(core.LOCAL_HTTP_BOUNDS["rate_limit_requests"]):
                self.assertTrue(isolated.allow_client_request("fixture"))
            self.assertFalse(isolated.allow_client_request("fixture"))
            acquired = 0
            while isolated._request_slots.acquire(blocking=False):
                acquired += 1
            self.assertEqual(acquired, core.LOCAL_HTTP_BOUNDS["max_concurrent_requests"])
            for _ in range(acquired):
                isolated._request_slots.release()
            self.assertEqual(isolated.request_timeout, core.LOCAL_HTTP_BOUNDS["request_timeout_seconds"])
        finally:
            isolated.server_close()


if __name__ == "__main__":
    unittest.main()
