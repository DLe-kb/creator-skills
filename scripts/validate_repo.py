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
TITLE_PLUGIN_DIR = ROOT / "plugins" / "conversation-title-organizer"
MARKETPLACE_FILE = ROOT / ".agents" / "plugins" / "marketplace.json"
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


def validate_mental_model_info_cards() -> None:
    skill_dir = SKILLS_DIR / "mental-model-info-cards"
    required = {
        "scripts/init_project.py",
        "scripts/validate_project.mjs",
        "references/card-protocol.md",
        "references/content-quality.md",
        "references/tool-guide.md",
        "assets/template/README.md",
        "assets/template/tool-v1/README.md",
        "assets/template/tool-v1/index.html",
        "assets/template/tool-v1/styles.css",
        "assets/template/tool-v1/export.mjs",
        "assets/template/tool-v1/data/models.js",
        "assets/template/tool-v1/data/theme.js",
        "assets/template/tool-v1/data/captions.md",
        "assets/template/tool-v1/src/cards.js",
    }
    missing = sorted(path for path in required if not (skill_dir / path).is_file())
    if missing:
        fail(f"Missing mental-model-info-cards files: {', '.join(missing)}")


def validate_xhs_viral_content_analysis() -> None:
    skill_dir = SKILLS_DIR / "xhs-viral-content-analysis"
    required = {
        "agents/openai.yaml",
        "assets/XHS-Image-Post-Audit-Template.html",
        "assets/XHS-Video-Post-Audit-Template.html",
        "assets/XHS-Cross-Report-Synthesis-Template.html",
        "references/analysis-result-contract.md",
        "references/analysis-result.schema.json",
        "references/cross-report-synthesis.md",
        "references/html-report-contract.md",
        "references/html-report-visual-system.md",
        "references/image-post-analysis.md",
        "references/shared-analysis-core.md",
        "references/synthesis-html-contract.md",
        "references/synthesis-result-contract.md",
        "references/synthesis-result.schema.json",
        "references/video-post-analysis.md",
        "scripts/embed_html_images.py",
        "scripts/test_validate_analysis_result.py",
        "scripts/test_validate_html_report.py",
        "scripts/test_validate_synthesis_html.py",
        "scripts/test_validate_synthesis_result.py",
        "scripts/validate_analysis_result.py",
        "scripts/validate_html_report.py",
        "scripts/validate_synthesis_html.py",
        "scripts/validate_synthesis_result.py",
    }
    missing = sorted(path for path in required if not (skill_dir / path).is_file())
    if missing:
        fail(f"Missing xhs-viral-content-analysis files: {', '.join(missing)}")


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
    if data.get("repository") != "https://github.com/DLe-kb/creator-skills":
        fail("plugin.json repository URL is incorrect")


def validate_conversation_title_plugin() -> None:
    required = {
        ".codex-plugin/plugin.json",
        "hooks.json",
        "config/default-config.json",
        "scripts/normalize_conversation_title.py",
        "scripts/test_normalize_conversation_title.py",
        "skills/conversation-title-organizer/SKILL.md",
        "skills/conversation-title-organizer/agents/openai.yaml",
    }
    missing = sorted(path for path in required if not (TITLE_PLUGIN_DIR / path).is_file())
    if missing:
        fail(f"Missing conversation-title-organizer files: {', '.join(missing)}")

    manifest_path = TITLE_PLUGIN_DIR / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != "conversation-title-organizer":
        fail("conversation-title-organizer manifest name is incorrect")
    if manifest.get("skills") != "./skills/":
        fail("conversation-title-organizer skills path is incorrect")

    hooks = json.loads((TITLE_PLUGIN_DIR / "hooks.json").read_text(encoding="utf-8"))
    if not hooks.get("hooks", {}).get("Stop"):
        fail("conversation-title-organizer Stop hook is missing")

    marketplace = json.loads(MARKETPLACE_FILE.read_text(encoding="utf-8"))
    if marketplace.get("name") != "creator-skills":
        fail("marketplace name must be creator-skills")
    entries = {item.get("name"): item for item in marketplace.get("plugins", [])}
    entry = entries.get("conversation-title-organizer")
    expected_path = "./plugins/conversation-title-organizer"
    if not entry or entry.get("source", {}).get("path") != expected_path:
        fail("conversation-title-organizer marketplace entry is missing or incorrect")


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
    validate_mental_model_info_cards()
    validate_xhs_viral_content_analysis()
    validate_plugin()
    validate_conversation_title_plugin()
    validate_repository_hygiene()
    print(f"Open Creator repository validation passed for {len(skill_files)} skill(s).")


if __name__ == "__main__":
    main()
