"""Build only the standalone governance plugin, using the Python standard library."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

PLUGIN = Path("plugins/owledge-governance")
FILES = (
    ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "plugin.json",
    "LICENSE", "README.md", "PRIVACY.md", "PUBLISHING.md", "VALIDATION.md",
    "skills/governance/SKILL.md", "hooks/hooks.example.json", "hooks/session-start.cjs",
)
CATALOGS = (".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json")
NAME = "owledge-governance"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def safe_file(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or "\\" in relative:
        raise ValueError("Unsafe package path")
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Linked package path")
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError("Missing or escaping package file")
    return current


def validate(root: Path) -> str:
    plugin = root / PLUGIN
    actual = {p.relative_to(plugin).as_posix() for p in plugin.rglob("*") if p.is_file() or p.is_symlink()}
    if actual != set(FILES):
        raise ValueError("Distribution inventory differs from the explicit allowlist")
    for file in FILES:
        safe_file(root, (PLUGIN / file).as_posix())
    portable = load_json(plugin / "plugin.json")
    version = portable.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-z0-9.-]+)?", version):
        raise ValueError("Invalid version")
    if portable.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        raise ValueError("Unexpected portable schema declaration")
    for file in ("plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        doc = load_json(plugin / file)
        if doc.get("name") != NAME or doc.get("version") != version:
            raise ValueError("Manifest identity mismatch")
        if any(key in doc for key in ("hooks", "mcpServers", "apps", "dependencies")):
            raise ValueError("Default package must remain skills-only")
    if load_json(plugin / ".codex-plugin/plugin.json").get("skills") != "./skills/":
        raise ValueError("Invalid Codex skills path")
    for catalog in CATALOGS:
        doc = load_json(safe_file(root, catalog))
        if doc.get("name") != "owledge-labs" or len(doc.get("plugins", [])) != 1:
            raise ValueError("Invalid marketplace")
        item = doc["plugins"][0]
        src = item.get("source")
        if isinstance(src, dict):
            if src.get("source") != "local":
                raise ValueError("Unexpected source kind")
            src = src.get("path")
            if item.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
                raise ValueError("Invalid Codex catalog policy")
        if item.get("name") != NAME or src != "./plugins/owledge-governance":
            raise ValueError("Marketplace target mismatch")
    skill = (plugin / "skills/governance/SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: governance\n") or f'version: "{version}"' not in skill:
        raise ValueError("Skill identity mismatch")
    if re.findall(r"\| (W\d{2}) \|", skill) != [f"W{i:02}" for i in range(1, 9)]:
        raise ValueError("Missing or duplicated governance rules")
    hook = load_json(plugin / "hooks/hooks.example.json")
    command = hook["hooks"]["SessionStart"][0]["hooks"][0]
    if command != {"type": "command", "command": 'node "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.cjs"', "timeout": 5}:
        raise ValueError("Unexpected example hook")
    return version


def archive(target: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            stream.writestr(info, content, compresslevel=9)


def build(root: Path, output: Path) -> list[Path]:
    version = validate(root)
    if output.resolve().is_relative_to((root / PLUGIN).resolve()):
        raise ValueError("Artifact output must stay outside the plugin")
    output.mkdir(parents=True, exist_ok=True)
    entries = {name: safe_file(root, (PLUGIN / name).as_posix()).read_bytes() for name in FILES}
    plugin_zip = output / f"owledge-governance-{version}.zip"
    market_zip = output / f"owledge-marketplace-{version}.zip"
    targets = [plugin_zip, market_zip, output / "SHA256SUMS.txt"]
    if any(p.exists() or p.is_symlink() for p in targets):
        raise ValueError("Refusing to overwrite existing artifacts")
    archive(plugin_zip, entries)
    marketplace = {f"{PLUGIN.as_posix()}/{name}": data for name, data in entries.items()}
    marketplace.update({name: safe_file(root, name).read_bytes() for name in CATALOGS})
    archive(market_zip, marketplace)
    sums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in targets[:2])
    targets[2].write_text(sums, encoding="utf-8", newline="\n")
    return targets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        for artifact in build(Path(__file__).resolve().parents[1], args.output):
            print(artifact)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Build failed: {exc}\n")
