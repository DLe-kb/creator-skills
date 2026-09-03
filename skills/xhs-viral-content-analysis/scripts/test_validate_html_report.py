#!/usr/bin/env python3
"""Self-test the HTML report validator without third-party packages."""

from validate_html_report import ValidationError, validate_text


SECTIONS = ("scope", "findings", "components", "carriers", "routes", "persuasion", "evidence", "limits")


def valid_report() -> str:
    sections = "".join(f'<section class="section"><div class="wrap"><div class="section-heading"></div><div data-section="{name}"><h2>{name}</h2></div></div></section>' for name in SECTIONS)
    evidence_groups = "".join(
        f'''<article class="finding-grid" data-evidence-group="group-{index}">
        <div class="finding-copy"><h3>结论</h3><p>说明</p><div class="finding-points">
        <div class="finding-point"><strong>任务</strong><span>判断</span></div>
        <div class="finding-point"><strong>边界</strong><span>范围</span></div></div></div>
        <div class="evidence-stack"><figure class="evidence" data-evidence-source="sample-{index}-cover">
        <img data-zoom src="data:image/png;base64,iVBORw0KGgo=" alt="证据图"><figcaption>支持判断</figcaption></figure></div></article>'''
        for index in range(1, 5)
    )
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>图文内容分析</title>
<style>body{{font-family:system-ui}} img{{max-width:100%}}</style></head>
<body data-report-template="xhs-image-post-audit">
<div class="topbar" data-report-part="navigation"><div class="topbar-inner"><div></div><nav class="topnav"></nav></div></div>
<main><header class="section hero" data-report-part="audit-hero"><div class="hero-copy"></div>
<dl class="audit-meta" data-report-part="audit-meta"><dt>样本</dt><dd>1</dd></dl>
<div class="hero-conclusion" data-report-part="executive-summary"><div class="hero-summary-grid">核心结论</div></div></header>
{sections}<div class="route-list"><div class="route"></div></div>
<div class="case-list"><article class="case"><div class="case-header"><h3>原帖标题</h3><div class="case-metrics">指标</div></div>
<div class="case-layout"><figure class="full-shot"><img data-zoom src="data:image/png;base64,iVBORw0KGgo=" alt="完整页面"></figure>
<div class="case-analysis"><div class="case-line">标题</div><div class="case-line">正文</div><div class="case-line">图片</div><div class="case-line">风险</div></div></div>
<details class="gallery"><summary>配图</summary></details></article></div><div class="limit-grid"></div>
{evidence_groups}<div data-report-part="evidence-gallery"></div></main>
<dialog data-report-part="lightbox"></dialog></body></html>'''


def expect_invalid(text: str, expected_text: str) -> None:
    try:
        validate_text(text)
    except ValidationError as error:
        if expected_text not in str(error):
            raise AssertionError(f"Unexpected validation error: {error}") from error
        return
    raise AssertionError("Expected validation to fail")


def valid_video_report() -> str:
    text = valid_report()
    text = text.replace("图文内容分析", "视频内容分析")
    text = text.replace('data-report-template="xhs-image-post-audit"', 'data-report-template="xhs-video-post-audit"')
    text = text.replace('data-section="components"', 'data-section="decision"')
    extra_sections = ''.join(
        f'<section class="section" data-section="{name}"><div class="wrap"><div class="section-heading"><h2>{name}</h2></div></div></section>'
        for name in ("screen-copy", "voiceover", "opening")
    )
    return text.replace("</main>", f'{extra_sections}<div class="timeline-wrap"><div class="timeline"></div></div><div class="av-grid"></div></main>')


def main() -> None:
    validate_text(valid_report())
    validate_text(valid_video_report())

    expect_invalid(valid_report().replace(' data-section="limits"', ""), "missing data-section")
    expect_invalid(valid_report().replace(' data-report-template="xhs-image-post-audit"', ""), "data-report-template")
    expect_invalid(valid_report().replace(' data-report-part="audit-meta"', ""), "missing data-report-part")
    expect_invalid(valid_report().replace("data:image/png;base64,iVBORw0KGgo=", "https://example.com/evidence.png"), "not portable")
    expect_invalid(valid_report().replace(" data-zoom", ""), "data-zoom")
    expect_invalid(valid_report().replace(' data-evidence-group="group-4"', ""), "at least 4 data-evidence-group")
    expect_invalid(valid_report().replace(' data-evidence-source="sample-1-cover"', ' data-evidence-source=""'), "must be non-empty")
    expect_invalid(valid_report().replace('class="finding-points"', 'class="evidence-cards"', 1), "parallel evidence components")
    expect_invalid(valid_report().replace('class="finding-point"', 'class="other-point"', 1), "at least 2 finding-point")
    expect_invalid(valid_report().replace('class="case-header"', 'class="case-header case-title"', 1), "parallel evidence components")
    expect_invalid(valid_report().replace('class="case-metrics"', 'class="other-metrics"', 1), "missing standard template components")
    expect_invalid(valid_report().replace('<div class="case-line">风险</div>', ''), "at least 4 case-line")
    local_path = "/" + "Users/example/report"
    expect_invalid(valid_report().replace("图文内容分析", local_path), "absolute local path")
    expect_invalid(valid_report().replace("</body>", "<p>制作说明</p></body>"), "production notes")
    expect_invalid(valid_report().replace("核心结论", "执行摘要"), "visible executive summary")
    expect_invalid(valid_video_report().replace(' data-section="voiceover"', ""), "missing data-section")
    expect_invalid(valid_video_report().replace('class="timeline-wrap"', 'class="other-wrap"'), "missing video template components")

    print("PASS: validator enforces the shared image/video audit system, media-specific sections, portable evidence, and content hygiene")


if __name__ == "__main__":
    main()
