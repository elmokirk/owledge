from __future__ import annotations
import pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "tools"))
import owledge_context_profiles as profiles  # noqa: E402

class ProgressiveDisclosureTests(unittest.TestCase):
 def test_synopsis_is_noncanonical_and_detects_body_drift(self):
  item=profiles.synopsis("body v1", "short", source_revision="r1")
  self.assertEqual(item["authority"], "non_canonical")
  self.assertTrue(profiles.validate_synopsis(item, "body v1")["fresh"])
  self.assertEqual(profiles.validate_synopsis(item, "body v2")["reason"], "stale_body")
 def test_tool_profiles_leave_unused_tools_inactive_and_reject_unknown(self):
  available={"owledge_read_entrypoint","owledge_doctor","owledge_search_memory","owledge_context_synopsis","owledge_build_context_pack","owledge_list_tasks","owledge_list_reviews"}
  selected=profiles.active_tools("retrieval", available)
  self.assertEqual(selected["active_tools"], ["owledge_search_memory","owledge_context_synopsis","owledge_build_context_pack"])
  self.assertIn("owledge_doctor", selected["inactive_tools"])
  with self.assertRaisesRegex(ValueError, "unknown_task_class"): profiles.active_tools("unsafe", available)

if __name__ == "__main__": unittest.main()
