#!/usr/bin/env python3
"""Self-test the cross-report synthesis HTML validator."""

from validate_synthesis_html import ValidationError, validate_text


PIXEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="


def valid_report() -> str:
    sections = "".join(f'<section class="section" data-section="{name}"><div class="wrap"><div class="section-heading"><h2>{name}</h2><p>正式报告内容</p></div></div></section>' for name in ("scope", "applicability", "mechanisms", "routes", "media", "subjects", "diagnosis"))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>综合分析报告</title>
    <style>.wrap{{width:min(100% - 32px,1280px)}}.section-heading{{width:100%;min-width:0}}p{{overflow-wrap:anywhere}}.grid{{grid-template-columns:1fr}}@media (max-width:680px){{.grid{{grid-template-columns:1fr}}}}</style></head>
    <body data-report-template="xhs-cross-report-synthesis"><header data-report-part="navigation"></header><main>
    <section data-report-part="synthesis-hero"><div data-report-part="synthesis-meta"></div><div data-report-part="executive-summary">核心结论</div></section>
    <div class="report-gallery" data-report-part="report-gallery"><img src="{PIXEL}" alt="报告快照"></div>
    <div class="scope-ladder"></div><div class="finding-list"><div class="mechanism-evidence"></div></div>
    <div class="route-list"><div class="route-proof"></div></div><div class="media-compare"></div><div class="subject-grid"></div><div class="diagnostic-grid"></div>
    {sections}</main><dialog data-report-part="lightbox"></dialog></body></html>'''


def expect_invalid(text: str, message: str) -> None:
    try:
        validate_text(text)
    except ValidationError as error:
        if message not in str(error):
            raise AssertionError(f"Unexpected error: {error}") from error
        return
    raise AssertionError("Expected validation to fail")


def main() -> None:
    validate_text(valid_report())
    expect_invalid(valid_report().replace(' data-section="diagnosis"', ""), "missing data-section")
    expect_invalid(valid_report().replace("正式报告内容", "制作说明", 1), "production explanation")
    expect_invalid(valid_report().replace("综合分析报告", "高转化公式", 1), "outcome formula")
    expect_invalid(valid_report().replace("overflow-wrap:anywhere", "overflow-wrap:normal"), "wrapping")
    expect_invalid(valid_report().replace(PIXEL, "https://example.com/image.jpg"), "external resource")
    expect_invalid(valid_report().replace("核心结论", "{{CORE_FINDING}}"), "placeholder")
    print("PASS: synthesis HTML validator enforces formal copy, portable assets, required sections, and responsive width rules")


if __name__ == "__main__":
    main()
