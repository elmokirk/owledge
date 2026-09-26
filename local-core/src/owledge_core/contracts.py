"""Typed Layer-0 boundary contract primitives and manifest loading."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Literal, Mapping, Protocol, TypeVar, cast


__all__ = (
    "ActiveCoreManifest",
    "BundleResourceBinding",
    "BundleVerification",
    "ContractValidationError",
    "CoreContractBundle",
    "FixtureIntent",
    "ImportEdge",
    "LogicalResourceName",
    "PackageIntent",
    "PolicyAuthority",
    "RoleIntent",
    "SemanticVersion",
    "Sha256Digest",
    "VerifiedBundleResource",
    "build_import_graph",
    "parse_active_core_manifest",
    "parse_core_contract_bundle",
    "validate_import_graph",
    "verify_contract_bundle",
)


class ContractValidationError(ValueError):
    """Raised when a vNext boundary contract fails closed."""


def valid_evidence_value_contract(contract: object) -> bool:
    """Closed, bounded value shapes shared by retrieval and repair previews."""
    if not isinstance(contract, dict):
        return False
    kind = contract.get("type")
    if kind == "authority_id":
        return set(contract) == {"type"}
    if kind == "integer_string":
        low, high = contract.get("minimum"), contract.get("maximum")
        return (set(contract) == {"type", "minimum", "maximum"}
                and type(low) is int and type(high) is int and 0 <= low <= high <= 1000000)
    if kind == "bounded_text":
        limit = contract.get("max_chars")
        return set(contract) == {"type", "max_chars"} and type(limit) is int and 1 <= limit <= 512
    return False


def evidence_value_matches(value: object, contract: object) -> bool:
    if not isinstance(value, str) or not valid_evidence_value_contract(contract):
        return False
    if contract["type"] == "authority_id":
        prefix, sep, suffix = value.partition(":")
        return bool(prefix and sep and suffix)
    if contract["type"] == "integer_string":
        return bool(value and value.isascii() and value.isdecimal()
                    and contract["minimum"] <= int(value) <= contract["maximum"])
    return (bool(value.strip()) and value.splitlines() == [value]
            and len(value) <= contract["max_chars"]
            and len(value.encode("utf-8")) <= 2048
            and not any(ord(char) < 32 or ord(char) == 127 for char in value)
            and "<!--" not in value and "-->" not in value)


class CoverageCaseInvalidError(ContractValidationError):
    """Raised before an evidence-body scan when Coverage authority is invalid."""


class SourceSnapshotError(ContractValidationError):
    """Typed failure from an untrusted read-only source connector."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code


@dataclass(frozen=True, slots=True)
class SourceFileSnapshot:
    """One byte-exact untrusted Markdown entry with a safe relative identity."""

    relative_path: str
    content: bytes
    content_sha256: str
    size_bytes: int

    @classmethod
    def from_bytes(cls, relative_path: str, content: bytes) -> "SourceFileSnapshot":
        if not isinstance(relative_path, str) or not isinstance(content, bytes):
            raise SourceSnapshotError("source_ambiguous", "source entry is incomplete")
        if "\\" in relative_path or ":" in relative_path:
            raise SourceSnapshotError("path_escape", "source path is not portable")
        candidate = PurePosixPath(relative_path)
        if (
            candidate.is_absolute()
            or relative_path.startswith("//")
            or not candidate.parts
            or any(part in {"", ".", ".."} for part in candidate.parts)
            or candidate.suffix.casefold() != ".md"
        ):
            raise SourceSnapshotError("path_escape", "source path escapes its root")
        canonical_path = candidate.as_posix()
        return cls(
            relative_path=canonical_path,
            content=content,
            content_sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
        )

    @property
    def normalized_path(self) -> str:
        return unicodedata.normalize("NFC", self.relative_path).casefold()


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    """Deterministic source observation; its live path is never rendered."""

    source_id: str
    source_root: Path
    snapshot_sha256: str
    files: tuple[SourceFileSnapshot, ...]

    @classmethod
    def create(
        cls,
        source_id: str,
        source_root: Path,
        files: Iterable[SourceFileSnapshot],
    ) -> "SourceSnapshot":
        if not re.fullmatch(r"source:[a-z0-9][a-z0-9-]*", source_id):
            raise SourceSnapshotError("source_ambiguous", "source identity is invalid")
        ordered = tuple(sorted(files, key=lambda item: item.normalized_path))
        normalized = [item.normalized_path for item in ordered]
        if len(normalized) != len(set(normalized)):
            raise SourceSnapshotError("source_ambiguous", "source paths collide")
        records = [
            {
                "relative_path": item.relative_path,
                "size_bytes": item.size_bytes,
                "content_sha256": item.content_sha256,
            }
            for item in ordered
        ]
        encoded = json.dumps(
            records,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return cls(
            source_id=source_id,
            source_root=Path(source_root),
            snapshot_sha256=hashlib.sha256(encoded).hexdigest(),
            files=ordered,
        )

    @property
    def size_bytes(self) -> int:
        return sum(item.size_bytes for item in self.files)


class SourceConnector(Protocol):
    """Private read-only connector port used only by local setup."""

    def scan(self) -> SourceSnapshot: ...


_DocumentT = TypeVar("_DocumentT")
_OutcomeT = TypeVar("_OutcomeT")


class AuthorityRepository(Protocol[_DocumentT]):
    """Private authority persistence seam; not a public extension contract."""

    def bootstrap(self, authority_id: str) -> _DocumentT: ...

    def snapshot(
        self,
        authority_id: str,
        coverage_case_id: str | None = None,
    ) -> tuple[_DocumentT, ...]: ...

    def coverage_snapshot(
        self,
        authority_id: str,
        controls: tuple[_DocumentT, ...],
    ) -> tuple[_DocumentT, ...]: ...

    def progressive_controls(self, authority_id: str) -> tuple[_DocumentT, ...]: ...

    def progressive_stage_snapshot(
        self,
        authority_id: str,
        stage: str,
        *,
        max_documents: int,
        max_bytes: int,
    ) -> Mapping[str, object]: ...

    def maintenance_snapshot(
        self,
        authority_id: str,
        *,
        max_documents: int,
        max_bytes: int,
        max_candidates: int,
        cursor: Mapping[str, object] | None,
        stage: str | None = None,
    ) -> Mapping[str, object]: ...

    def raw_keyword_snapshot(
        self,
        authority_id: str,
        *,
        query: str,
        max_documents: int,
        max_bytes: int,
        max_matches: int = 8,
        source_areas: tuple[str, ...] = (".",),
        cursor: Mapping[str, object] | None = None,
        discover_areas: bool = False,
        area_parent: str = ".",
    ) -> Mapping[str, object]: ...

    def apply(
        self,
        operation: str,
        authority_id: str,
        arguments: Mapping[str, object],
    ) -> object: ...

    def read(
        self,
        operation: str,
        authority_id: str,
        arguments: Mapping[str, object],
    ) -> object: ...


class EvidenceRetriever(Protocol[_DocumentT, _OutcomeT]):
    """Private deterministic evidence-assessment seam."""

    revision: str

    def assess(
        self,
        documents: tuple[_DocumentT, ...],
        coverage_case_id: str,
    ) -> _OutcomeT | None: ...

    def select(
        self,
        documents: tuple[_DocumentT, ...],
        selected_artifact_ids: tuple[str, ...],
    ) -> tuple[_DocumentT, ...]: ...


class Clock(Protocol):
    """Private injected-clock seam."""

    def now(self) -> str | None: ...


_SEMVER_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
_RESOURCE_NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_TICKET04_ROLE_MODULES = (
    ("contracts", "owledge_core.contracts"),
    ("artifacts", "owledge_core.artifacts"),
    ("policy", "owledge_core.policy"),
    ("project_io", "owledge_core.project_io"),
    ("retrieval", "owledge_core.retrieval"),
    ("lifecycle", "owledge_core.lifecycle"),
    ("health", "owledge_core.health"),
    ("api", "owledge_core.api"),
)
_TICKET04_DEPENDENCIES = (
    ("stdlib",),
    ("contracts",),
    ("contracts", "artifacts"),
    ("contracts", "artifacts"),
    ("contracts", "artifacts", "policy", "project_io"),
    ("contracts", "artifacts", "policy", "project_io"),
    ("contracts", "artifacts", "policy", "project_io", "retrieval", "lifecycle"),
    ("contracts", "artifacts", "policy", "project_io", "retrieval", "lifecycle", "health"),
)
_FORBIDDEN_IMPORT_ROOTS = ("dbm", "ftplib", "http", "smtplib", "socket", "sqlite3", "urllib")
_EX01_OWNER = "Kirk Kleinau"
_EX01_GATES = (
    "L0-G01-manifest-owner",
    "L0-G02-import-direction",
    "L0-G03-policy-single-owner",
    "L0-G04-public-typing",
)
_EX01_FIXTURE_PATHS = frozenset(
    {
        "tests/vnext/test_ex01_boundary_manifest.py",
        "tests/vnext/test_ex01_contract_bundle.py",
        "tests/vnext/test_ex01_dependency_graph.py",
        "tests/vnext/test_ex01_packaging_non_exposure.py",
        "tests/vnext/test_ex01_policy_authority.py",
        "tests/vnext/test_ex01_public_typing.py",
    }
)
_TICKET06_RESOURCE_PATHS = {
    "artifact-routing-v1": "contracts/vnext/artifact-routing-v1.json",
    "reason-codes-v1": "contracts/vnext/reason-codes-v1.json",
    "schema-registry-v1": "contracts/vnext/schema-registry-v1.json",
    "settings-registry-v1": "contracts/vnext/settings-registry-v1.json",
}


@dataclass(frozen=True, slots=True)
class SemanticVersion:
    """Strict three-part semantic contract version."""

    value: str

    def __post_init__(self) -> None:
        if _SEMVER_PATTERN.fullmatch(self.value) is None:
            raise ContractValidationError("semantic version must be three numeric parts")


@dataclass(frozen=True, slots=True)
class LogicalResourceName:
    """Path-independent logical name for one bundle resource."""

    value: str

    def __post_init__(self) -> None:
        if _RESOURCE_NAME_PATTERN.fullmatch(self.value) is None:
            raise ContractValidationError("logical resource name must be lower kebab-case")


@dataclass(frozen=True, slots=True)
class Sha256Digest:
    """Canonical lowercase hexadecimal SHA-256 value."""

    value: str

    def __post_init__(self) -> None:
        if _SHA256_PATTERN.fullmatch(self.value) is None:
            raise ContractValidationError("SHA-256 must be 64 lowercase hexadecimal characters")


@dataclass(frozen=True, slots=True)
class BundleResourceBinding:
    """Immutable binding from one logical resource to exact source bytes."""

    logical_name: LogicalResourceName
    relative_path: str
    sha256: Sha256Digest

    def __post_init__(self) -> None:
        path = PurePosixPath(self.relative_path)
        if path.is_absolute() or ".." in path.parts or path.parts[:2] != ("contracts", "vnext"):
            raise ContractValidationError(
                f"bundle resource path must remain under contracts/vnext: {self.relative_path}"
            )


@dataclass(frozen=True, slots=True)
class CoreContractBundle:
    """One immutable Ticket-06 manifest binding all Core contract resources."""

    schema_version: SemanticVersion
    bundle_id: LogicalResourceName
    authority: str
    resources: tuple[BundleResourceBinding, ...]


@dataclass(frozen=True, slots=True)
class VerifiedBundleResource:
    """Verified logical resource identity returned by bundle validation."""

    logical_name: LogicalResourceName
    sha256: Sha256Digest


@dataclass(frozen=True, slots=True)
class BundleVerification:
    """Deterministic result for one exact Core Contract Bundle."""

    bundle_sha256: Sha256Digest
    resources: tuple[VerifiedBundleResource, ...]


@dataclass(frozen=True, slots=True)
class PackageIntent:
    """Non-public package intent bound by the active Core manifest."""

    package: str
    source_root: str
    exposure: str
    include_in_default_artifact: bool
    default_release: str
    entry_points: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoleIntent:
    """One Ticket-04 Layer-0 responsibility declared by the manifest."""

    role_id: str
    module: str
    owner: str
    workpackage: str
    gates: tuple[str, ...]
    allowed_dependencies: tuple[str, ...]
    public_exports: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FixtureIntent:
    """One G01-bound EX-01 fixture with explicit ownership and lifecycle."""

    fixture_id: str
    path: str
    owning_role: str
    owner: str
    workpackage: str
    contract_version: str
    gates: tuple[str, ...]
    lanes: tuple[str, ...]
    mutation_class: str
    expected_terminal: str
    expected_reason_code: str
    retirement_condition: str


@dataclass(frozen=True, slots=True)
class PolicyAuthority:
    """One executable policy rule bound to exactly one admitted role."""

    rule_id: str
    owner_role: str
    module: str


@dataclass(frozen=True, slots=True)
class ActiveCoreManifest:
    """Immutable representation of the sole active-Core intent authority."""

    schema_version: str
    manifest_id: str
    authority: str
    package_intent: PackageIntent
    roles: tuple[RoleIntent, ...]
    fixtures: tuple[FixtureIntent, ...]
    forbidden_import_roots: tuple[str, ...]
    policy_inventory: tuple[PolicyAuthority, ...]


@dataclass(frozen=True, slots=True)
class ImportEdge:
    """One normalized import edge observed outside the Core contract layer."""

    source_role: str
    target: str
    kind: Literal["role", "stdlib", "external", "dynamic"]
    module: str

    def __post_init__(self) -> None:
        if not self.source_role or not self.target or not self.module:
            raise ContractValidationError("import edge fields must be non-empty")


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ContractValidationError(f"{field} must be an object with string keys")
    return cast(dict[str, object], value)


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_json(document: str) -> object:
    return cast(object, json.loads(document, object_pairs_hook=_unique_json_object))


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractValidationError(f"{field} must be a non-empty string")
    return value


def _boolean(value: object, field: str) -> bool:
    if not isinstance(value, bool):
        raise ContractValidationError(f"{field} must be a boolean")
    return value


def _string_tuple(value: object, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ContractValidationError(f"{field} must be an array of non-empty strings")
    return tuple(cast(list[str], value))


def _package_intent(value: object) -> PackageIntent:
    data = _mapping(value, "package_intent")
    expected = {
        "package",
        "source_root",
        "exposure",
        "include_in_default_artifact",
        "default_release",
        "entry_points",
    }
    if set(data) != expected:
        raise ContractValidationError("package_intent has missing or unknown fields")
    intent = PackageIntent(
        package=_string(data["package"], "package_intent.package"),
        source_root=_string(data["source_root"], "package_intent.source_root"),
        exposure=_string(data["exposure"], "package_intent.exposure"),
        include_in_default_artifact=_boolean(
            data["include_in_default_artifact"],
            "package_intent.include_in_default_artifact",
        ),
        default_release=_string(data["default_release"], "package_intent.default_release"),
        entry_points=_string_tuple(data["entry_points"], "package_intent.entry_points"),
    )
    if intent.package != "owledge_core" or intent.source_root != "src":
        raise ContractValidationError("package_intent must identify src/owledge_core")
    if intent.exposure != "not_exposed" or intent.include_in_default_artifact:
        raise ContractValidationError("EX-01 package intent must remain not_exposed and non-default")
    if intent.default_release != "0.8.0" or intent.entry_points:
        raise ContractValidationError("EX-01 cannot change the v0.8.0 default or add entry points")
    return intent


def _roles(value: object) -> tuple[RoleIntent, ...]:
    if not isinstance(value, list):
        raise ContractValidationError("roles must be an array")
    roles: list[RoleIntent] = []
    role_ids: set[str] = set()
    for index, item in enumerate(value):
        data = _mapping(item, f"roles[{index}]")
        expected = {
            "role_id",
            "module",
            "owner",
            "workpackage",
            "gates",
            "allowed_dependencies",
            "public_exports",
        }
        if set(data) != expected:
            raise ContractValidationError(f"roles[{index}] has missing or unknown fields")
        role = RoleIntent(
                role_id=_string(data["role_id"], f"roles[{index}].role_id"),
                module=_string(data["module"], f"roles[{index}].module"),
                owner=_string(data["owner"], f"roles[{index}].owner"),
                workpackage=_string(data["workpackage"], f"roles[{index}].workpackage"),
                gates=_string_tuple(data["gates"], f"roles[{index}].gates"),
                allowed_dependencies=_string_tuple(
                    data["allowed_dependencies"],
                    f"roles[{index}].allowed_dependencies",
                ),
                public_exports=_string_tuple(data["public_exports"], f"roles[{index}].public_exports"),
            )
        if role.role_id in role_ids:
            raise ContractValidationError(f"duplicate role_id: {role.role_id}")
        if role.owner != _EX01_OWNER:
            raise ContractValidationError(f"roles[{index}] must bind the named EX-01 owner")
        if role.workpackage != "EX-01":
            raise ContractValidationError(f"roles[{index}] must bind the bounded EX-01 workpackage")
        if role.gates != _EX01_GATES:
            raise ContractValidationError(f"roles[{index}] gate authority must match EX-01")
        role_ids.add(role.role_id)
        roles.append(role)
    return tuple(roles)


def _fixtures(value: object, roles: tuple[RoleIntent, ...]) -> tuple[FixtureIntent, ...]:
    if not isinstance(value, list):
        raise ContractValidationError("fixtures must be an array")
    expected_fields = {
        "fixture_id", "path", "owning_role", "owner", "workpackage", "contract_version",
        "gates", "lanes", "mutation_class", "expected_terminal", "expected_reason_code",
        "retirement_condition",
    }
    fixtures: list[FixtureIntent] = []
    for index, item in enumerate(value):
        data = _mapping(item, f"fixtures[{index}]")
        if set(data) != expected_fields:
            raise ContractValidationError(f"fixtures[{index}] has missing or unknown fields")
        fixtures.append(_fixture_intent(data, index))
    _validate_fixture_authority(fixtures, roles)
    return tuple(sorted(fixtures, key=lambda fixture: fixture.fixture_id))


def _fixture_intent(data: dict[str, object], index: int) -> FixtureIntent:
    prefix = f"fixtures[{index}]"
    return FixtureIntent(
        fixture_id=_string(data["fixture_id"], f"{prefix}.fixture_id"),
        path=_string(data["path"], f"{prefix}.path"),
        owning_role=_string(data["owning_role"], f"{prefix}.owning_role"),
        owner=_string(data["owner"], f"{prefix}.owner"),
        workpackage=_string(data["workpackage"], f"{prefix}.workpackage"),
        contract_version=_string(data["contract_version"], f"{prefix}.contract_version"),
        gates=_string_tuple(data["gates"], f"{prefix}.gates"),
        lanes=_string_tuple(data["lanes"], f"{prefix}.lanes"),
        mutation_class=_string(data["mutation_class"], f"{prefix}.mutation_class"),
        expected_terminal=_string(data["expected_terminal"], f"{prefix}.expected_terminal"),
        expected_reason_code=_string(data["expected_reason_code"], f"{prefix}.expected_reason_code"),
        retirement_condition=_string(data["retirement_condition"], f"{prefix}.retirement_condition"),
    )


def _validate_fixture_authority(
    fixtures: list[FixtureIntent], roles: tuple[RoleIntent, ...]
) -> None:
    role_gates = {role.role_id: frozenset(role.gates) for role in roles}
    ids = [fixture.fixture_id for fixture in fixtures]
    paths = [fixture.path for fixture in fixtures]
    if len(ids) != len(set(ids)) or len(paths) != len(set(paths)):
        raise ContractValidationError("duplicate fixture authority")
    if frozenset(paths) != _EX01_FIXTURE_PATHS:
        raise ContractValidationError("fixture authority must bind exactly the EX-01 fixture set")
    for fixture in fixtures:
        if fixture.owner != _EX01_OWNER or fixture.workpackage != "EX-01":
            raise ContractValidationError(f"fixture owner/workpackage mismatch: {fixture.fixture_id}")
        if fixture.owning_role not in role_gates:
            raise ContractValidationError(f"fixture owning role is not admitted: {fixture.fixture_id}")
        if not fixture.gates or not set(fixture.gates) <= role_gates[fixture.owning_role]:
            raise ContractValidationError(f"fixture gate authority mismatch: {fixture.fixture_id}")
        if not set(fixture.lanes) <= {"fast-pr", "platform-smoke", "full-release"}:
            raise ContractValidationError(f"fixture lane authority mismatch: {fixture.fixture_id}")


def _policy_inventory(value: object) -> tuple[PolicyAuthority, ...]:
    if not isinstance(value, list):
        raise ContractValidationError("policy_inventory must be an array")
    inventory: list[PolicyAuthority] = []
    rule_ids: set[str] = set()
    for index, item in enumerate(value):
        data = _mapping(item, f"policy_inventory[{index}]")
        if set(data) != {"rule_id", "owner_role", "module"}:
            raise ContractValidationError(
                f"policy_inventory[{index}] has missing or unknown fields"
            )
        authority = PolicyAuthority(
                rule_id=_string(data["rule_id"], f"policy_inventory[{index}].rule_id"),
                owner_role=_string(
                    data["owner_role"],
                    f"policy_inventory[{index}].owner_role",
                ),
                module=_string(data["module"], f"policy_inventory[{index}].module"),
            )
        if authority.rule_id in rule_ids:
            raise ContractValidationError(f"duplicate policy rule: {authority.rule_id}")
        if authority.owner_role != "policy" or authority.module != "owledge_core.policy":
            raise ContractValidationError(
                f"policy owner role must be policy: {authority.rule_id}"
            )
        rule_ids.add(authority.rule_id)
        inventory.append(authority)
    return tuple(inventory)


def _bundle_resources(value: object) -> tuple[BundleResourceBinding, ...]:
    if not isinstance(value, list):
        raise ContractValidationError("resources must be an array")
    resources: list[BundleResourceBinding] = []
    names: set[str] = set()
    paths: set[str] = set()
    for index, item in enumerate(value):
        data = _mapping(item, f"resources[{index}]")
        if set(data) != {"logical_name", "relative_path", "sha256"}:
            raise ContractValidationError(f"resources[{index}] has missing or unknown fields")
        binding = BundleResourceBinding(
            logical_name=LogicalResourceName(
                _string(data["logical_name"], f"resources[{index}].logical_name")
            ),
            relative_path=_string(data["relative_path"], f"resources[{index}].relative_path"),
            sha256=Sha256Digest(_string(data["sha256"], f"resources[{index}].sha256")),
        )
        if binding.logical_name.value in names or binding.relative_path in paths:
            raise ContractValidationError("duplicate bundle resource authority")
        names.add(binding.logical_name.value)
        paths.add(binding.relative_path)
        resources.append(binding)
    if names != set(_TICKET06_RESOURCE_PATHS):
        raise ContractValidationError("bundle must bind exactly the four Ticket-06 resources")
    for binding in resources:
        if binding.relative_path != _TICKET06_RESOURCE_PATHS[binding.logical_name.value]:
            raise ContractValidationError(
                f"logical resource path mismatch: {binding.logical_name.value}"
            )
    return tuple(sorted(resources, key=lambda item: item.logical_name.value))


def parse_active_core_manifest(document: str) -> ActiveCoreManifest:
    """Parse and fail-closed validate an authoritative EX-01 manifest."""
    raw = _parse_json(document)
    data = _mapping(raw, "manifest")
    expected = {
        "schema_version",
        "manifest_id",
        "authority",
        "package_intent",
        "roles",
        "fixtures",
        "forbidden_import_roots",
        "policy_inventory",
    }
    if set(data) != expected:
        raise ContractValidationError("manifest has missing or unknown fields")
    roles = _roles(data["roles"])
    manifest = ActiveCoreManifest(
        schema_version=_string(data["schema_version"], "schema_version"),
        manifest_id=_string(data["manifest_id"], "manifest_id"),
        authority=_string(data["authority"], "authority"),
        package_intent=_package_intent(data["package_intent"]),
        roles=roles,
        fixtures=_fixtures(data["fixtures"], roles),
        forbidden_import_roots=_string_tuple(
            data["forbidden_import_roots"],
            "forbidden_import_roots",
        ),
        policy_inventory=_policy_inventory(data["policy_inventory"]),
    )
    if manifest.authority != "contracts/vnext/active-core-manifest-v1.json":
        raise ContractValidationError("manifest authority path is not canonical")
    if manifest.schema_version != "1.0.0" or manifest.manifest_id != "owledge-active-core-vnext-1":
        raise ContractValidationError("active Core manifest identity does not match EX-01")
    if tuple((role.role_id, role.module) for role in manifest.roles) != _TICKET04_ROLE_MODULES:
        raise ContractValidationError("manifest role topology must match Ticket-04 exactly")
    if tuple(role.allowed_dependencies for role in manifest.roles) != _TICKET04_DEPENDENCIES:
        raise ContractValidationError("manifest dependency authority must match Ticket-04 exactly")
    if manifest.forbidden_import_roots != _FORBIDDEN_IMPORT_ROOTS:
        raise ContractValidationError("manifest forbidden dependency roots cannot be weakened")
    return manifest


def parse_core_contract_bundle(document: str) -> CoreContractBundle:
    """Parse the sole immutable vNext Core Contract Bundle authority."""
    raw = _parse_json(document)
    data = _mapping(raw, "core_contract_bundle")
    if set(data) != {"schema_version", "bundle_id", "authority", "resources"}:
        raise ContractValidationError("core contract bundle has missing or unknown fields")
    bundle = CoreContractBundle(
        schema_version=SemanticVersion(_string(data["schema_version"], "schema_version")),
        bundle_id=LogicalResourceName(_string(data["bundle_id"], "bundle_id")),
        authority=_string(data["authority"], "authority"),
        resources=_bundle_resources(data["resources"]),
    )
    if bundle.authority != "contracts/vnext/core-contract-bundle-v1.json":
        raise ContractValidationError("core contract bundle authority path is not canonical")
    if (
        bundle.schema_version.value != "1.0.0"
        or bundle.bundle_id.value != "owledge-core-contract-bundle-vnext-1"
    ):
        raise ContractValidationError("core contract bundle identity does not match EX-01")
    return bundle


def verify_contract_bundle(
    bundle: CoreContractBundle,
    resource_bytes: Mapping[str, bytes],
) -> BundleVerification:
    """Verify exact resources and return a deterministic semantic bundle hash."""
    expected_paths = {binding.relative_path for binding in bundle.resources}
    supplied_paths = set(resource_bytes)
    if supplied_paths != expected_paths:
        missing = sorted(expected_paths - supplied_paths)
        extra = sorted(supplied_paths - expected_paths)
        raise ContractValidationError(f"bundle resources mismatch: missing={missing}; extra={extra}")
    verified: list[VerifiedBundleResource] = []
    canonical_resources: list[dict[str, str]] = []
    for binding in bundle.resources:
        observed = Sha256Digest(hashlib.sha256(resource_bytes[binding.relative_path]).hexdigest())
        if observed != binding.sha256:
            raise ContractValidationError(f"bundle resource hash mismatch: {binding.relative_path}")
        verified.append(VerifiedBundleResource(binding.logical_name, observed))
        canonical_resources.append(
            {
                "logical_name": binding.logical_name.value,
                "relative_path": binding.relative_path,
                "sha256": binding.sha256.value,
            }
        )
    canonical = json.dumps(
        {
            "authority": bundle.authority,
            "bundle_id": bundle.bundle_id.value,
            "resources": canonical_resources,
            "schema_version": bundle.schema_version.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return BundleVerification(
        bundle_sha256=Sha256Digest(hashlib.sha256(canonical).hexdigest()),
        resources=tuple(verified),
    )


def settings_resource_paths() -> tuple[Path, ...]:
    """Locate the one authored source bundle or its exact installed copy."""
    source = Path(__file__).resolve().parents[2] / "contracts" / "vnext"
    packaged = Path(__file__).resolve().parent / "resources"
    root = (packaged if (packaged / "core-contract-bundle-v1.json").exists() else
            source if (Path(__file__).resolve().parents[1].name == "src"
                       and (source / "core-contract-bundle-v1.json").is_file()) else packaged)
    names = ("core-contract-bundle-v1.json", *(Path(value).name for value in _TICKET06_RESOURCE_PATHS.values()))
    return tuple(root / name for name in names)


def verified_settings_catalog() -> dict[str, object]:
    """Verify bundled contract bytes before interpreting the closed Settings catalog."""
    paths = settings_resource_paths()
    raw: list[bytes] = []
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ContractValidationError("installed Settings resource is unavailable")
        before = path.stat()
        if before.st_size > 262_144:
            raise ContractValidationError("Settings resource exceeds its fixed bound")
        with path.open("rb") as handle:
            if os.fstat(handle.fileno()).st_size != before.st_size:
                raise ContractValidationError("Settings resource changed during inspection")
            body = handle.read(262_145)
        if len(body) != before.st_size or path.stat().st_mtime_ns != before.st_mtime_ns:
            raise ContractValidationError("Settings resource changed during inspection")
        raw.append(body)
    try:
        bundle = parse_core_contract_bundle(raw[0].decode("utf-8"))
        by_name = {path.name: body for path, body in zip(paths[1:], raw[1:])}
        resources = {binding.relative_path: by_name[Path(binding.relative_path).name] for binding in bundle.resources}
        verified = verify_contract_bundle(bundle, resources)
        catalog = json.loads(resources["contracts/vnext/settings-registry-v1.json"].decode("utf-8"),
                             object_pairs_hook=_unique_json_object)
    except (UnicodeError, ValueError, KeyError, IndexError) as error:
        raise ContractValidationError("Settings contract bundle is invalid") from error
    if (not isinstance(catalog, dict) or set(catalog) != {"schema_version", "registry_id", "status", "keys"}
            or not isinstance(catalog.get("schema_version"), str)
            or catalog["schema_version"] != bundle.schema_version.value
            or not isinstance(catalog.get("registry_id"), str)
            or not _RESOURCE_NAME_PATTERN.fullmatch(catalog["registry_id"])
            or catalog.get("status") != "active" or not isinstance(catalog.get("keys"), list)
            or len(catalog["keys"]) != 4):
        raise ContractValidationError("Settings catalog is outside the admitted boundary")
    specs = {}
    for item in catalog["keys"]:
        if (not isinstance(item, dict) or set(item) != {"key", "type", "domain", "scopes", "default",
                "precedence", "meaning", "deprecated", "migration"}
                or not isinstance(item.get("key"), str) or item["key"] in specs
                or item.get("type") != "enum" or not isinstance(item.get("domain"), list)
                or not all(isinstance(value, str) for value in item["domain"])
                or len(item["domain"]) != len(set(item["domain"]))
                or item.get("scopes") != ["user-global", "project"]
                or item.get("default") not in item["domain"]
                or item.get("precedence") != "project_over_global_over_catalog"
                or not isinstance(item.get("meaning"), str) or not item["meaning"]
                or item.get("deprecated") is not False or item.get("migration") != "explicit_owner_repair"):
            raise ContractValidationError("Settings key contract is invalid")
        specs[item["key"]] = item
    if set(specs) != {"recall_default", "recall_max_auto", "research_default", "research_max_auto"}:
        raise ContractValidationError("Settings key catalog is outside the admitted boundary")
    if (specs["recall_default"]["domain"] != ["focused", "expanded", "audit"]
            or specs["recall_max_auto"]["domain"] != specs["recall_default"]["domain"]
            or specs["research_default"]["domain"] != ["none", "targeted", "deep"]
            or specs["research_max_auto"]["domain"] != specs["research_default"]["domain"]):
        raise ContractValidationError("Settings depth domains are invalid")
    return {"registry_id": catalog["registry_id"], "registry_sha256": hashlib.sha256(
        resources["contracts/vnext/settings-registry-v1.json"]).hexdigest(),
        "bundle_sha256": verified.bundle_sha256.value,
        "defaults": {key: value["default"] for key, value in specs.items()}, "specs": specs}


def _relative_import_module(source_module: str, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    package_parts = source_module.split(".")[:-1]
    if node.level > len(package_parts):
        raise ContractValidationError(f"unresolved relative import in {source_module}")
    kept = package_parts[: len(package_parts) - node.level + 1]
    suffix = [] if node.module is None else node.module.split(".")
    return ".".join((*kept, *suffix))


def _static_import_modules(
    source_module: str,
    tree: ast.AST,
) -> tuple[str, ...]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = _relative_import_module(source_module, node)
            if module == "owledge_core":
                modules.extend(f"{module}.{alias.name}" for alias in node.names)
            elif module:
                modules.append(module)
    return tuple(modules)


def _is_dynamic_import_callable(value: ast.expr, names: set[str]) -> bool:
    if isinstance(value, ast.Name):
        return value.id in names
    if isinstance(value, ast.Attribute):
        return value.attr in {"__import__", "import_module"}
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
        return value.func.id == "getattr" and any(
            isinstance(argument, ast.Constant)
            and argument.value in {"__import__", "import_module"}
            for argument in value.args
        )
    return False


def _dynamic_import_names(tree: ast.AST) -> set[str]:
    dynamic_names = {"__import__", "import_module"}
    assignments: list[tuple[tuple[str, ...], ast.expr]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "importlib":
            dynamic_names.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name == "import_module"
            )
        elif isinstance(node, ast.Assign):
            targets = tuple(target.id for target in node.targets if isinstance(target, ast.Name))
            assignments.append((targets, node.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None:
                assignments.append(((node.target.id,), node.value))
    changed = True
    while changed:
        changed = False
        for targets, value in assignments:
            if _is_dynamic_import_callable(value, dynamic_names):
                additions = set(targets) - dynamic_names
                dynamic_names.update(additions)
                changed = changed or bool(additions)
    return dynamic_names


def _dynamic_import_symbols(tree: ast.AST) -> tuple[str, ...]:
    symbols: list[str] = []
    dynamic_names = _dynamic_import_names(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in dynamic_names:
            symbols.append(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in dynamic_names:
            symbols.append(node.func.attr)
        elif isinstance(node.func, ast.Call) and isinstance(node.func.func, ast.Name):
            if node.func.func.id == "getattr" and any(
                isinstance(argument, ast.Constant)
                and argument.value in {"__import__", "import_module"}
                for argument in node.func.args
            ):
                symbols.append("getattr(import-function)")
    return tuple(symbols)


def _classify_import(
    module_roles: Mapping[str, str], source_role: str, module: str
) -> ImportEdge:
    root = module.split(".", 1)[0]
    target_role = module_roles.get(module)
    if target_role is not None:
        return ImportEdge(source_role, target_role, "role", module)
    if root in sys.stdlib_module_names:
        return ImportEdge(source_role, root, "stdlib", module)
    return ImportEdge(source_role, root, "external", module)


def build_import_graph(
    manifest: ActiveCoreManifest,
    module_sources: Mapping[str, str],
) -> tuple[ImportEdge, ...]:
    """Derive and validate the deterministic static graph for admitted sources."""
    module_roles = {role.module: role.role_id for role in manifest.roles}
    if set(module_sources) != set(module_roles):
        missing = sorted(set(module_roles) - set(module_sources))
        extra = sorted(set(module_sources) - set(module_roles))
        raise ContractValidationError(
            f"module sources mismatch: missing={missing}; extra={extra}"
        )
    edges: list[ImportEdge] = []
    for module, source_role in module_roles.items():
        source = module_sources[module]
        if not isinstance(source, str):
            raise ContractValidationError(f"module source must be text: {module}")
        try:
            tree = ast.parse(source, filename=module)
        except SyntaxError as error:
            raise ContractValidationError(f"invalid Python source: {module}") from error
        for imported in _static_import_modules(module, tree):
            edges.append(_classify_import(module_roles, source_role, imported))
        for symbol in _dynamic_import_symbols(tree):
            edges.append(ImportEdge(source_role, symbol, "dynamic", symbol))
    return validate_import_graph(manifest, edges)


def _validate_edge_classification(
    edge: ImportEdge,
    module_roles: Mapping[str, str],
) -> None:
    root = edge.module.split(".", 1)[0]
    if edge.kind == "role":
        if module_roles.get(edge.module) != edge.target:
            raise ContractValidationError(f"role import classification mismatch: {edge.module}")
    elif edge.kind == "stdlib":
        if root not in sys.stdlib_module_names or edge.target != root:
            raise ContractValidationError(f"stdlib import classification mismatch: {edge.module}")
    elif edge.kind == "external":
        if root in sys.stdlib_module_names or edge.module in module_roles or edge.target != root:
            raise ContractValidationError(f"external import classification mismatch: {edge.module}")


def validate_import_graph(
    manifest: ActiveCoreManifest,
    edges: Iterable[ImportEdge],
) -> tuple[ImportEdge, ...]:
    """Validate declared role edges and return one deterministic graph."""
    allowed = {role.role_id: frozenset(role.allowed_dependencies) for role in manifest.roles}
    module_roles = {role.module: role.role_id for role in manifest.roles}
    normalized = tuple(
        sorted(set(edges), key=lambda edge: (edge.source_role, edge.target, edge.kind, edge.module))
    )
    for edge in normalized:
        if edge.source_role not in allowed:
            raise ContractValidationError(f"unknown source role: {edge.source_role}")
        _validate_edge_classification(edge, module_roles)
        if edge.kind == "dynamic":
            raise ContractValidationError(f"unresolved dynamic import: {edge.module}")
        if edge.kind == "external":
            raise ContractValidationError(f"forbidden external dependency: {edge.module}")
        if edge.module.split(".", 1)[0] in manifest.forbidden_import_roots:
            raise ContractValidationError(f"forbidden dependency root: {edge.module}")
        if edge.kind == "role" and edge.target not in allowed:
            raise ContractValidationError(f"unknown target role: {edge.target}")

    adjacency = {role_id: set[str]() for role_id in allowed}
    for edge in normalized:
        if edge.kind == "role":
            adjacency[edge.source_role].add(edge.target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(role_id: str) -> None:
        if role_id in visiting:
            raise ContractValidationError(f"dependency cycle includes role: {role_id}")
        if role_id in visited:
            return
        visiting.add(role_id)
        for dependency in sorted(adjacency[role_id]):
            visit(dependency)
        visiting.remove(role_id)
        visited.add(role_id)

    for role_id in sorted(adjacency):
        visit(role_id)

    for edge in normalized:
        if edge.kind == "role" and edge.target not in allowed[edge.source_role]:
            raise ContractValidationError(
                f"forbidden outward edge: {edge.source_role} -> {edge.target}"
            )
    return normalized
