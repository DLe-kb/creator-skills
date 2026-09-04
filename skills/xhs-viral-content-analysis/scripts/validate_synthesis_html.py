#!/usr/bin/env python3
"""Validate the portable cross-report synthesis HTML contract."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ABSOLUTE_LOCAL_PATH = re.compile(r"(?:file://|/(?:Users|home|private)/|(?<![A-Za-z])[A-Za-z]:[\\/])", re.IGNORECASE)
EXTERNAL_RESOURCE = re.compile(r"^(?:https?:|//|file:)", re.IGNORECASE)
PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
FORBIDDEN_TEXT = {
    "internal version language": re.compile(r"\bV\d+(?:\.\d+)*\b|内部版本|版本计划", re.IGNORECASE),
    "stage or gate language": re.compile(r"\bGate\b|阶段门|阶段状态", re.IGNORECASE),
    "production explanation": re.compile(r"制作说明|制作过程|修改记录|解释说明|排版说明|阅读说明"),
    "agent or skill internals": re.compile(r"SKILL\.md|技能自证|脚本调用|校验器|Schema|Agent\s*解释|模型解释", re.IGNORECASE),
    "unverified outcome formula": re.compile(r"高转化(?:种草内容)?公式|爆款公式|保证爆款|保证转化|必然提升|导致成交"),
}
REQUIRED_PARTS = {"navigation", "synthesis-hero", "synthesis-meta", "executive-summary", "report-gallery", "lightbox"}
REQUIRED_SECTIONS = {"scope", "applicability", "mechanisms", "routes", "media", "subjects", "diagnosis"}
REQUIRED_CLASSES = {
    "wrap", "section", "section-heading", "report-gallery", "scope-ladder", "finding-list",
    "mechanism-evidence", "route-list", "route-proof", "media-compare", "subject-grid", "diagnostic-grid",
}


class ValidationError(Exception):
    pass


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang: str | None = None
        self.charset: str | None = None
        self.template: str | None = None
        self.parts: set[str] = set()
        self.sections: set[str] = set()
        self.classes: set[str] = set()
        self.resources: list[str] = []
        self.images: list[dict[str, str]] = []
        self.text_parts: list[str] = []
        self.has_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        self.classes.update(values.get("class", "").split())
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "meta" and values.get("charset"):
            self.charset = values["charset"]
        elif tag == "title":
            self.has_title = True
        elif tag == "body":
            self.template = values.get("data-report-template")
        if values.get("data-report-part"):
            self.parts.add(values["data-report-part"])
        if values.get("data-section"):
            self.sections.add(values["data-section"])
        if tag in {"img", "script", "iframe", "video", "audio", "source"} and values.get("src"):
            self.resources.append(values["src"])
        if tag == "link" and values.get("href"):
            self.resources.append(values["href"])
        if tag == "img":
            self.images.append(values)

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_parts.append(data)


def validate_text(text: str) -> None:
    if "<!doctype html>" not in text.lower():
        raise ValidationError("missing HTML doctype")
    parser = Parser()
    parser.feed(text)
    if parser.lang != "zh-CN":
        raise ValidationError("html lang must be zh-CN")
    if not parser.charset or parser.charset.lower() != "utf-8":
        raise ValidationError("missing UTF-8 charset")
    if not parser.has_title:
        raise ValidationError("missing title")
    if parser.template != "xhs-cross-report-synthesis":
        raise ValidationError("body data-report-template must be xhs-cross-report-synthesis")
    missing_parts = REQUIRED_PARTS - parser.parts
    if missing_parts:
        raise ValidationError(f"missing data-report-part: {', '.join(sorted(missing_parts))}")
    missing_sections = REQUIRED_SECTIONS - parser.sections
    if missing_sections:
        raise ValidationError(f"missing data-section: {', '.join(sorted(missing_sections))}")
    missing_classes = REQUIRED_CLASSES - parser.classes
    if missing_classes:
        raise ValidationError(f"missing synthesis components: {', '.join(sorted(missing_classes))}")
    if PLACEHOLDER.search(text):
        raise ValidationError("unreplaced template placeholder")
    if ABSOLUTE_LOCAL_PATH.search(text):
        raise ValidationError("absolute local path found")
    for resource in parser.resources:
        if EXTERNAL_RESOURCE.search(resource):
            raise ValidationError(f"external resource is not portable: {resource[:80]}")
    for index, image in enumerate(parser.images):
        source = image.get("src", "")
        if not source.startswith("data:image/"):
            raise ValidationError(f"img[{index}] must use an embedded data URI")
        if not image.get("alt", "").strip():
            raise ValidationError(f"img[{index}] must have non-empty alt text")
    visible_text = " ".join(parser.text_parts)
    for label, pattern in FORBIDDEN_TEXT.items():
        if pattern.search(visible_text):
            raise ValidationError(f"forbidden {label}")
    required_css = {
        "fluid wrap": re.compile(r"\.wrap\s*\{[^}]*width\s*:\s*min\(", re.DOTALL),
        "heading width": re.compile(r"\.section-heading\s*\{[^}]*width\s*:\s*100%", re.DOTALL),
        "wrapping": re.compile(r"overflow-wrap\s*:\s*anywhere"),
        "mobile breakpoint": re.compile(r"@media\s*\([^)]*max-width\s*:\s*(?:680|768)px"),
        "mobile single column": re.compile(r"grid-template-columns\s*:\s*1fr"),
    }
    for label, pattern in required_css.items():
        if not pattern.search(text):
            raise ValidationError(f"missing responsive CSS: {label}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_synthesis_html.py PATH", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        validate_text(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
