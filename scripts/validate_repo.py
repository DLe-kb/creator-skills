#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
PLUGIN_FILE = ROOT / ".codex-plugin" / "plugin.json"
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        fail(f"{path.relative_to(ROOT)} has incomplete YAML frontmatter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} frontmatter must be a mapping")
    return data


def validate_skills() -> list[Path]:
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        fail("No skills/*/SKILL.md files found")

    for skill_file in skill_files:
        skill_dir = skill_file.parent
        data = load_frontmatter(skill_file)
        if set(data) != {"name", "description"}:
            fail(f"{skill_file.relative_to(ROOT)} frontmatter must contain only name and description")
        if data["name"] != skill_dir.name:
            fail(f"Skill name must match directory: {skill_dir.relative_to(ROOT)}")
        if not SKILL_NAME_PATTERN.fullmatch(skill_dir.name):
            fail(f"Invalid skill directory name: {skill_dir.name}")
        if not isinstance(data["description"], str) or not data["description"].strip():
            fail(f"Skill description must be non-empty: {skill_file.relative_to(ROOT)}")

        agent_metadata = skill_dir / "agents" / "openai.yaml"
        if not agent_metadata.is_file():
            fail(f"Missing agents/openai.yaml: {skill_dir.relative_to(ROOT)}")

    return skill_files


def validate_project_harness() -> None:
    skill_dir = SKILLS_DIR / "project-harness"
    required = {
        "references/protocol-playbook.md",
        "references/01_AGENTS.md",
        "references/02_PROJECT_STATE.md",
        "references/03_DECISIONS.md",
        "references/04_DISCUSSION_QUEUE.md",
        "references/05_RUNBOOK.md",
        "references/06_REFERENCES.md",
        "references/07_LESSONS_LEARNED.md",
        "references/08_TASK_STATE.md",
    }
    missing = sorted(path for path in required if not (skill_dir / path).is_file())
    if missing:
        fail(f"Missing project-harness files: {', '.join(missing)}")


def validate_plugin() -> None:
    data = json.loads(PLUGIN_FILE.read_text(encoding="utf-8"))
    for key in ("name", "version", "description", "author", "skills", "interface"):
        if key not in data:
            fail(f"plugin.json is missing {key}")
    if data["name"] != "open-creator":
        fail("plugin.json name must be open-creator")
    if data["skills"] != "./skills/":
        fail("plugin.json skills path must be ./skills/")
    if data.get("license") != "MIT":
        fail("plugin.json license must be MIT")
    if data.get("repository") != "https://github.com/DLe-kb/open-creator":
        fail("plugin.json repository URL is incorrect")


def validate_repository_hygiene() -> None:
    forbidden_text = ("/" + "Users/", "[" + "TODO:")
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.name == ".DS_Store":
            fail(f"Finder cache found: {path.relative_to(ROOT)}")
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for marker in forbidden_text:
            if marker in text:
                fail(f"Forbidden marker {marker!r} in {path.relative_to(ROOT)}")


def main() -> None:
    skill_files = validate_skills()
    validate_project_harness()
    validate_plugin()
    validate_repository_hygiene()
    print(f"Open Creator repository validation passed for {len(skill_files)} skill(s).")


if __name__ == "__main__":
    main()
