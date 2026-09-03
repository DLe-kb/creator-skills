#!/usr/bin/env python3
"""Validate the portable HTML report contract for xhs-viral-content-analysis."""

from __future__ import annotations

import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


MAC_USERS_ROOT = "/" + "Users/"
ABSOLUTE_LOCAL_PATH_PATTERN = re.compile(
    rf"(?:file://|{re.escape(MAC_USERS_ROOT)}|/home/|[A-Za-z]:[\\/])",
    re.IGNORECASE,
)
ABSOLUTE_CSS_RESOURCE_PATTERN = re.compile(
    rf"url\(\s*['\"]?(?:https?:|//|file:|{re.escape(MAC_USERS_ROOT)}|/home/|[A-Za-z]:[\\/])",
    re.IGNORECASE,
)


IMAGE_REQUIRED_SECTIONS = {
    "scope",
    "findings",
    "components",
    "carriers",
    "routes",
    "persuasion",
    "evidence",
    "limits",
}

VIDEO_REQUIRED_SECTIONS = {
    "scope",
    "findings",
    "decision",
    "screen-copy",
    "voiceover",
    "opening",
    "carriers",
    "routes",
    "persuasion",
    "evidence",
    "limits",
}

REQUIRED_REPORT_PARTS = {
    "navigation",
    "audit-hero",
    "audit-meta",
    "executive-summary",
    "evidence-gallery",
    "lightbox",
}

REPORT_TEMPLATES = {"xhs-image-post-audit", "xhs-video-post-audit"}

REQUIRED_COMPONENT_CLASSES = {
    "topbar",
    "topbar-inner",
    "topnav",
    "section",
    "wrap",
    "hero",
    "hero-copy",
    "audit-meta",
    "hero-conclusion",
    "hero-summary-grid",
    "section-heading",
    "finding-grid",
    "finding-copy",
    "finding-points",
    "evidence-stack",
    "route-list",
    "case-list",
    "case-header",
    "case-metrics",
    "case-layout",
    "full-shot",
    "case-analysis",
    "case-line",
    "gallery",
    "limit-grid",
}

FORBIDDEN_PARALLEL_COMPONENTS = {
    "evidence-led",
    "evidence-led-head",
    "evidence-cards",
    "evidence-card",
    "evidence-slot",
    "case-title",
    "case-body",
    "page-shot",
}

FORBIDDEN_PATTERNS = {
    "internal version language": re.compile(r"\bV\d+(?:\.\d+)*\b|内部版本|版本计划", re.IGNORECASE),
    "stage-gate language": re.compile(r"\bGate\b|阶段门|候选阶段", re.IGNORECASE),
    "production notes": re.compile(r"制作说明|修改记录|制作过程|验证路线"),
    "agent explanation": re.compile(r"Agent\s*解释|智能体解释|模型解释", re.IGNORECASE),
    "skill internals": re.compile(r"SKILL\.md|技能自证|脚本调用说明", re.IGNORECASE),
    "local path language": re.compile(r"本机路径|临时目录"),
    "visible executive summary": re.compile(r"执行摘要"),
    "reader-facing production instruction": re.compile(r"先给结论[，,]\s*再给|先给结论[，,]\s*再把"),
}


class ValidationError(Exception):
    pass


class ReportParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.charset: str | None = None
        self.title_parts: list[str] = []
        self.in_title = False
        self.sections: set[str] = set()
        self.report_template: str | None = None
        self.report_parts: set[str] = set()
        self.image_sources: list[str] = []
        self.zoomable_images = 0
        self.evidence_groups = 0
        self.evidence_source_refs: list[str] = []
        self.resource_urls: list[tuple[str, str]] = []
        self.class_counts: Counter[str] = Counter()
        self.tag_stack: list[str] = []
        self.active_evidence_groups: list[dict[str, object]] = []
        self.evidence_group_details: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        self.class_counts.update(classes)
        if "data-evidence-group" in values:
            self.active_evidence_groups.append(
                {
                    "name": values.get("data-evidence-group") or "",
                    "tag": tag,
                    "depth": len(self.tag_stack),
                    "classes": Counter(),
                    "evidence_figures": 0,
                }
            )
        for group in self.active_evidence_groups:
            group_classes = group["classes"]
            assert isinstance(group_classes, Counter)
            group_classes.update(classes)
            if tag == "figure" and "evidence" in classes and (values.get("data-evidence-source") or "").strip():
                group["evidence_figures"] = int(group["evidence_figures"]) + 1
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "body":
            self.report_template = values.get("data-report-template")
        if tag == "meta" and values.get("charset"):
            self.charset = values["charset"]
        if tag == "title":
            self.in_title = True
        if values.get("data-section"):
            self.sections.add(values["data-section"])
        if values.get("data-report-part"):
            self.report_parts.add(values["data-report-part"])
        if "data-evidence-group" in values:
            self.evidence_groups += 1
        if "data-evidence-source" in values:
            self.evidence_source_refs.append(values.get("data-evidence-source") or "")
        if tag == "img":
            self.image_sources.append(values.get("src") or "")
            if "data-zoom" in values:
                self.zoomable_images += 1
        if tag in {"img", "script", "iframe", "video", "audio", "source"} and values.get("src"):
            self.resource_urls.append((f"{tag}.src", values["src"] or ""))
        if tag == "link" and values.get("href"):
            self.resource_urls.append(("link.href", values["href"] or ""))
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.tag_stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        closing_depth = len(self.tag_stack) - 1
        for group in list(reversed(self.active_evidence_groups)):
            if group["tag"] == tag and group["depth"] == closing_depth:
                self.evidence_group_details.append(group)
                self.active_evidence_groups.remove(group)
                break
        if self.tag_stack:
            self.tag_stack.pop()

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def validate_text(text: str) -> None:
    if not re.match(r"^\s*<!doctype\s+html\s*>", text, re.IGNORECASE):
        raise ValidationError("missing <!doctype html>")

    parser = ReportParser()
    parser.feed(text)

    if parser.html_lang != "zh-CN":
        raise ValidationError('html lang must be "zh-CN"')
    if not parser.charset or parser.charset.lower() != "utf-8":
        raise ValidationError("missing UTF-8 charset declaration")
    if not "".join(parser.title_parts).strip():
        raise ValidationError("missing non-empty title")
    if parser.report_template not in REPORT_TEMPLATES:
        raise ValidationError('body data-report-template must identify the image-post or video-post audit template')

    missing_parts = sorted(REQUIRED_REPORT_PARTS - parser.report_parts)
    if missing_parts:
        raise ValidationError(f"missing data-report-part values: {', '.join(missing_parts)}")

    required_sections = VIDEO_REQUIRED_SECTIONS if parser.report_template == "xhs-video-post-audit" else IMAGE_REQUIRED_SECTIONS
    missing_sections = sorted(required_sections - parser.sections)
    if missing_sections:
        raise ValidationError(f"missing data-section values: {', '.join(missing_sections)}")

    missing_components = sorted(REQUIRED_COMPONENT_CLASSES - set(parser.class_counts))
    if missing_components:
        raise ValidationError(f"missing standard template components: {', '.join(missing_components)}")
    forbidden_components = sorted(FORBIDDEN_PARALLEL_COMPONENTS & set(parser.class_counts))
    if forbidden_components:
        raise ValidationError(f"parallel evidence components are not allowed: {', '.join(forbidden_components)}")
    if parser.report_template == "xhs-video-post-audit":
        missing_video_components = sorted({"timeline-wrap", "timeline", "av-grid"} - set(parser.class_counts))
        if missing_video_components:
            raise ValidationError(f"missing video template components: {', '.join(missing_video_components)}")

    case_count = parser.class_counts["case"]
    if case_count < 1:
        raise ValidationError("report must include at least one case in the evidence gallery")
    for component in ("case-header", "case-metrics", "case-layout", "full-shot", "case-analysis", "gallery"):
        if parser.class_counts[component] < case_count:
            raise ValidationError(f"each case must include one {component} component")
    if parser.class_counts["case-line"] < case_count * 4:
        raise ValidationError("each case must include at least 4 case-line analysis rows")

    for location, url in parser.resource_urls:
        lowered = url.strip().lower()
        if lowered.startswith(("http://", "https://", "//", "file://")):
            raise ValidationError(f"{location}: external or local resource is not portable: {url}")
        if url.startswith(("/", "~/")) or re.match(r"^[A-Za-z]:[\\/]", url):
            raise ValidationError(f"{location}: absolute local resource path is not allowed: {url}")

    for source in parser.image_sources:
        if not source.startswith("data:image/"):
            raise ValidationError("all report images must use embedded data:image sources")

    if parser.image_sources and parser.zoomable_images == 0:
        raise ValidationError("report images must include data-zoom for evidence inspection")
    if parser.evidence_groups < 4:
        raise ValidationError("report must include at least 4 data-evidence-group conclusion-evidence pairings")
    if len(parser.evidence_source_refs) < parser.evidence_groups:
        raise ValidationError("each data-evidence-group must include at least one data-evidence-source")
    if any(not source.strip() for source in parser.evidence_source_refs):
        raise ValidationError("data-evidence-source values must be non-empty")
    for group in parser.evidence_group_details:
        classes = group["classes"]
        assert isinstance(classes, Counter)
        required_group_classes = {"finding-grid", "finding-copy", "finding-points", "evidence-stack"}
        missing_group_classes = sorted(required_group_classes - set(classes))
        if missing_group_classes:
            raise ValidationError(
                f'evidence group "{group["name"]}" is missing standard components: {", ".join(missing_group_classes)}'
            )
        if classes["finding-point"] < 2:
            raise ValidationError(f'evidence group "{group["name"]}" must include at least 2 finding-point items')
        if int(group["evidence_figures"]) < 1:
            raise ValidationError(
                f'evidence group "{group["name"]}" must include figure.evidence with non-empty data-evidence-source'
            )

    inspectable_text = re.sub(r"data:image/[^;\s\"']+;base64,[A-Za-z0-9+/=]+", "data:image/...", text, flags=re.IGNORECASE)

    if ABSOLUTE_LOCAL_PATH_PATTERN.search(inspectable_text):
        raise ValidationError("report contains an absolute local path")
    if ABSOLUTE_CSS_RESOURCE_PATTERN.search(inspectable_text):
        raise ValidationError("CSS contains an external or absolute local resource")

    for label, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(inspectable_text):
            raise ValidationError(f"report contains forbidden {label}")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_html_report.py PATH", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        validate_text(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1

    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
