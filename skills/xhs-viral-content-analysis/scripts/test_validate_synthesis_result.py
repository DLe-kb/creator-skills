#!/usr/bin/env python3
"""Self-test the cross-report synthesis JSON validator."""

from copy import deepcopy

from validate_synthesis_result import ValidationError, validate


def valid_result() -> dict:
    return {
        "synthesis_status": "complete",
        "platform": "xiaohongshu",
        "synthesis_scope": {"subject": "洗护内容", "objective": "提炼跨报告共性", "included_report_ids": ["R01", "R02"], "limitations": ["仅有正样本"]},
        "report_records": [
            {"report_id": "R01", "subject": "产品甲", "media_type": "image_post", "analysis_status": "complete", "source_class": "enterprise", "included_sample_count": 1, "sample_ids": ["S01"], "locator": "reports/R01.json", "limitations": []},
            {"report_id": "R02", "subject": "产品乙", "media_type": "video_post", "analysis_status": "complete", "source_class": "external_public", "included_sample_count": 1, "sample_ids": ["S02"], "locator": "reports/R02.json", "limitations": ["外部候选"]}
        ],
        "evidence_records": [
            {"evidence_id": "E01", "report_id": "R01", "sample_id": "S01", "source_type": "report_finding", "locator": "reports/R01.json#finding-1", "observation": "先建立用户任务"},
            {"evidence_id": "E02", "report_id": "R02", "sample_id": "S02", "source_type": "frame", "locator": "reports/R02/frame-01.jpg", "observation": "视频先呈现使用问题"}
        ],
        "common_mechanisms": [{"mechanism_id": "M01", "label": "用户任务先于产品", "finding": "两份报告均先建立用户任务", "finding_type": "observed_pattern", "scope": "R01-R02", "supporting_report_ids": ["R01", "R02"], "supporting_sample_ids": ["S01", "S02"], "supporting_evidence_ids": ["E01", "E02"], "representative_evidence_ids": ["E01"], "contrary_evidence": [], "confidence": "medium", "limitations": ["两个报告"]}],
        "route_families": [{"route_family_id": "F01", "label": "问题分型", "status": "cross_report_observed", "user_task": "找到适合选项", "core_tension": "选择困难", "primary_carriers": ["image_cards", "voiceover"], "use_conditions": ["存在明确分型"], "non_applicable_conditions": [], "source_route_labels": ["选购", "导航"], "supporting_report_ids": ["R01", "R02"], "supporting_sample_ids": ["S01", "S02"], "supporting_evidence_ids": ["E01", "E02"], "representative_evidence_ids": ["E01"], "confidence": "medium", "limitations": []}],
        "media_differences": [{"dimension": "主要载体", "finding": "图文便于扫读，视频便于呈现过程", "finding_type": "analysis_inference", "supporting_report_ids": ["R01", "R02"], "evidence_ids": ["E01", "E02"], "confidence": "medium", "limitations": []}],
        "subject_differences": [],
        "applicability_levels": [{"level": "direct_supported", "label": "本批共性", "statement": "可回溯到两份报告", "support_status": "supported", "evidence_ids": ["E01", "E02"]}],
        "diagnostic_questions": [{"question": "用户能认出自己的问题吗？", "judgment": "先建立真实处境", "mechanism_ids": ["M01"]}],
        "claim_boundaries": [{"claim": "该机制导致高转化", "support_status": "unsupported", "evidence_ids": ["E01", "E02"], "reason": "缺少转化数据"}]
    }


def expect_invalid(data: dict, message: str) -> None:
    try:
        validate(data)
    except ValidationError as error:
        if message not in str(error):
            raise AssertionError(f"Unexpected error: {error}") from error
        return
    raise AssertionError("Expected validation to fail")


def main() -> None:
    validate(valid_result())
    one_report = deepcopy(valid_result())
    one_report["synthesis_scope"]["included_report_ids"] = ["R01"]
    expect_invalid(one_report, "at least two reports")
    one_source = deepcopy(valid_result())
    one_source["common_mechanisms"][0]["supporting_evidence_ids"] = ["E01"]
    one_source["common_mechanisms"][0]["representative_evidence_ids"] = ["E01"]
    expect_invalid(one_source, "at least two reports")
    bad_route = deepcopy(valid_result())
    bad_route["route_families"][0]["supporting_report_ids"] = ["R01"]
    expect_invalid(bad_route, "at least two reports")
    local_path = deepcopy(valid_result())
    local_path["report_records"][0]["locator"] = "/" + "Users/example/report.json"
    expect_invalid(local_path, "relative path")
    print("PASS: synthesis result validator enforces report count, cross-report support, references, and portable paths")


if __name__ == "__main__":
    main()
