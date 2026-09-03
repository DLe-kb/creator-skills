#!/usr/bin/env python3
"""Self-test the analysis-result validator without third-party packages."""

from copy import deepcopy

from validate_analysis_result import ValidationError, validate


def valid_result() -> dict:
    return {
        "analysis_status": "complete",
        "media_type": "image_post",
        "analysis_scope": {
            "platform": "xiaohongshu",
            "subject": "sample product category",
            "objective": "identify reusable image-post routes",
            "source_snapshot": "2026-01-01",
            "included_sample_ids": ["S01", "S02"],
            "excluded_samples": [{"sample_id": "S03", "reason": "video post"}],
            "limitations": ["positive samples only"],
        },
        "evidence_records": [
            {"evidence_id": "E01", "sample_id": "S01", "source_type": "title", "locator": "samples/S01/title.txt", "observation": "Title establishes a selection task."},
            {"evidence_id": "E02", "sample_id": "S02", "source_type": "image", "locator": "samples/S02/image-01.jpg", "observation": "The first image presents a comparison frame."},
        ],
        "sample_analyses": [
            {"sample_id": "S01", "user_task": "make a selection", "audience_problem": "choice overload", "product_role": "recommended option", "primary_carrier": "post_body", "component_analysis": {"title": "selection promise", "cover": "product context", "opening_hook": "choice conflict", "body": "selection logic", "image_sequence_and_carrier": "body-led", "decision_close": "recommendation", "evidence_and_risk": "no causal evidence"}, "body_variables": {"opening": "choice conflict", "pain_organization": "too many options", "product_entry": "recommended option", "value_translation": "lower decision cost", "experience_details": "not present", "final_judgment": "conditional recommendation"}, "image_sequence_tasks": ["identify product"], "module_handoffs": ["title to cover"], "persuasion_nodes": ["selection conflict"], "evidence_ids": ["E01"], "limitations": []},
            {"sample_id": "S02", "user_task": "make a selection", "audience_problem": "choice overload", "product_role": "comparison option", "primary_carrier": "image_cards", "component_analysis": {"title": "comparison task", "cover": "comparison frame", "opening_hook": "selection promise", "body": "image cards carry the comparison", "image_sequence_and_carrier": "image-card-led", "decision_close": "trade-off", "evidence_and_risk": "comparison conditions incomplete"}, "body_variables": {"opening": "comparison", "pain_organization": "choice overload", "product_entry": "comparison option", "value_translation": "consistent fields", "experience_details": "not present", "final_judgment": "trade-off"}, "image_sequence_tasks": ["establish comparison"], "module_handoffs": ["cover to image card"], "persuasion_nodes": ["comparison criteria"], "evidence_ids": ["E02"], "limitations": []},
        ],
        "route_findings": [
            {"route_id": "R01", "label": "decision support", "status": "observed", "supporting_sample_ids": ["S01", "S02"], "user_task": "make a selection", "core_tension": "too many options", "primary_carrier": "mixed", "product_position_and_role": "decision option", "use_conditions": ["comparable inputs"], "non_applicable_conditions": ["missing comparison evidence"], "module_handoffs": ["title to cover"], "persuasion_nodes": ["selection conflict", "comparison criteria"], "contrary_evidence": [], "evidence_ids": ["E01", "E02"], "confidence": "medium", "limitations": ["two samples"]}
        ],
        "value_translations": [
            {"user_friction": "choice overload", "feature_or_content_detail": "consistent comparison fields", "user_value": "lower decision cost", "product_role": "decision option", "evidence_ids": ["E02"], "claim_risk": "low"}
        ],
        "cross_sample_findings": [
            {"finding": "Both posts define a selection task before product detail.", "finding_type": "observed_pattern", "scope": "S01 and S02", "evidence_ids": ["E01", "E02"], "confidence": "medium", "limitations": ["positive samples only"]}
        ],
        "claim_boundaries": [
            {"claim": "The structure causes higher conversion.", "classification": "other", "support_status": "unsupported", "evidence_ids": ["E01", "E02"], "reason": "No controlled outcome evidence."}
        ],
        "downstream_handoff": {"usable_for_note_skill": True, "recommended_route_ids": ["R01"], "missing_inputs": ["approved product claims"], "prohibited_assumptions": ["performance causality"]},
    }


def expect_invalid(data: dict, expected_text: str) -> None:
    try:
        validate(data)
    except ValidationError as error:
        if expected_text not in str(error):
            raise AssertionError(f"Unexpected validation error: {error}") from error
        return
    raise AssertionError("Expected validation to fail")


def valid_video_result() -> dict:
    result = valid_result()
    result["media_type"] = "video_post"
    result["analysis_scope"]["included_sample_ids"] = ["S01"]
    result["analysis_scope"]["excluded_samples"] = []
    result["evidence_records"] = [
        {"evidence_id": "E01", "sample_id": "S01", "source_type": "frame", "locator": "samples/S01/frame-000.jpg", "observation": "Opening frame names the audience problem."},
        {"evidence_id": "E02", "sample_id": "S01", "source_type": "transcript", "locator": "samples/S01/transcript.txt#t=0,5", "observation": "Voiceover defines the selection task."},
    ]
    result["sample_analyses"] = [{
        "sample_id": "S01", "user_task": "choose an option", "audience_problem": "unclear fit", "product_role": "decision option", "primary_carrier": "mixed_video",
        "video_analysis": {
            "content_promise": "help the viewer identify a suitable option",
            "timeline_segments": [{"start": 0, "end": 5, "information_task": "name the problem and qualify the audience", "spoken_copy": "selection prompt", "on_screen_copy": "audience label", "visual": "problem state followed by product", "audio_visual_relation": "complement", "viewer_state_before": "uncertain relevance", "viewer_state_after": "recognizes a relevant choice task", "evidence_ids": ["E01", "E02"], "limitations": []}],
            "opening_analysis": [{"time": 0, "observation": "problem is visible", "viewer_reason_to_continue": "expects a selection answer", "evidence_ids": ["E01"]}],
            "on_screen_copy_analysis": [{"start": 0, "end": 2, "copy_summary": "audience problem", "copy_task": "qualify audience", "viewer_effect": "creates relevance", "viewer_shift": "from browsing to self-identification", "evidence_status": "source_fact", "risk": "none observed", "evidence_ids": ["E01"]}],
            "voiceover_copy_analysis": [{"start": 0, "end": 5, "copy_summary": "selection promise", "copy_task": "define the decision", "viewer_effect": "sets expected payoff", "viewer_shift": "from problem recognition to comparison", "evidence_status": "source_fact", "risk": "result not verified", "evidence_ids": ["E02"]}],
            "persuasion_chain": [{"node": "problem recognition", "function": "establish relevance", "viewer_shift": "recognizes the problem", "evidence_ids": ["E01"]}],
            "audio_visual_summary": "Visual identifies the situation while voiceover defines the decision task.",
            "comment_signals": [],
        },
        "module_handoffs": ["problem to selection"], "persuasion_nodes": ["problem recognition"], "evidence_ids": ["E01", "E02"], "limitations": ["no retention data"],
    }]
    result["route_findings"] = [{"route_id": "R01", "label": "guided selection", "status": "single_sample", "supporting_sample_ids": ["S01"], "user_task": "choose an option", "core_tension": "unclear fit", "primary_carrier": "mixed_video", "product_position_and_role": "decision option", "use_conditions": ["clear audience problem"], "non_applicable_conditions": ["no evidence"], "module_handoffs": ["problem to selection"], "persuasion_nodes": ["problem recognition"], "contrary_evidence": [], "evidence_ids": ["E01", "E02"], "confidence": "low", "limitations": ["single sample"]}]
    result["value_translations"] = []
    result["cross_sample_findings"] = [{"finding": "The opening defines a choice task.", "finding_type": "analysis_inference", "scope": "S01", "evidence_ids": ["E01", "E02"], "confidence": "low", "limitations": ["single sample"]}]
    result["claim_boundaries"] = [{"claim": "The structure causes conversion.", "classification": "other", "support_status": "unsupported", "evidence_ids": ["E01", "E02"], "reason": "No conversion data."}]
    result["replication_blueprints"] = [{"route_id": "R01", "audience_and_task": "viewer with unclear fit", "opening_fields": ["problem", "promise"], "timeline_tasks": ["qualify", "compare"], "on_screen_copy_fields": ["audience label"], "voiceover_fields": ["decision promise"], "shot_responsibilities": ["show the problem"], "product_entry": "after relevance is established", "objections_and_close": ["fit"], "success_conditions": ["credible evidence"], "failure_conditions": ["generic claims"], "evidence_ids": ["E01", "E02"], "limitations": ["structure candidate"]}]
    result["downstream_handoff"]["recommended_route_ids"] = ["R01"]
    return result


def main() -> None:
    validate(valid_result())
    validate(valid_video_result())

    independent = deepcopy(valid_result())
    del independent["downstream_handoff"]
    validate(independent)

    research_only_recommended = deepcopy(valid_result())
    research_only_recommended["route_findings"][0]["replication_readiness"] = "research_only"
    expect_invalid(research_only_recommended, "is research_only")

    conditional_without_inputs = deepcopy(valid_result())
    conditional_without_inputs["route_findings"][0]["replication_readiness"] = "conditional"
    expect_invalid(conditional_without_inputs, "blocking_inputs")

    research_only_blueprint = deepcopy(valid_video_result())
    research_only_blueprint["route_findings"][0]["replication_readiness"] = "research_only"
    research_only_blueprint["downstream_handoff"]["recommended_route_ids"] = []
    expect_invalid(research_only_blueprint, "cannot have replication blueprints")

    dangling = deepcopy(valid_result())
    dangling["route_findings"][0]["evidence_ids"] = ["E404"]
    expect_invalid(dangling, "unknown evidence ID")

    local_path = deepcopy(valid_result())
    local_path["evidence_records"][0]["locator"] = "/private/source/title.txt"
    expect_invalid(local_path, "use a relative path")

    extra_metadata = deepcopy(valid_result())
    extra_metadata["build_metadata"] = "not part of the public contract"
    expect_invalid(extra_metadata, "unexpected keys")

    missing_video = deepcopy(valid_video_result())
    del missing_video["sample_analyses"][0]["video_analysis"]
    expect_invalid(missing_video, "missing keys: video_analysis")

    no_copy = deepcopy(valid_video_result())
    no_copy["sample_analyses"][0]["video_analysis"]["on_screen_copy_analysis"] = []
    no_copy["sample_analyses"][0]["video_analysis"]["voiceover_copy_analysis"] = []
    expect_invalid(no_copy, "cannot both be empty")

    bad_timeline_reference = deepcopy(valid_video_result())
    bad_timeline_reference["sample_analyses"][0]["video_analysis"]["timeline_segments"][0]["evidence_ids"] = ["E404"]
    expect_invalid(bad_timeline_reference, "unknown evidence ID")

    bad_media = deepcopy(valid_result())
    bad_media["media_type"] = "carousel_video"
    expect_invalid(bad_media, "media_type: invalid value")

    print("PASS: validator accepts independent image and video results and rejects broken media or downstream contracts")


if __name__ == "__main__":
    main()
