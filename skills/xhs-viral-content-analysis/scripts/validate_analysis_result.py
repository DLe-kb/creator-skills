#!/usr/bin/env python3
"""Validate the JSON contract for xhs-viral-content-analysis."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


TOP_LEVEL_KEYS = {"analysis_status", "media_type", "analysis_scope", "evidence_records", "sample_analyses", "route_findings", "cross_sample_findings", "claim_boundaries"}
TOP_LEVEL_ALLOWED_KEYS = TOP_LEVEL_KEYS | {"value_translations", "replication_blueprints", "downstream_handoff"}
MEDIA_TYPES = {"image_post", "video_post"}
STATUS_VALUES = {"complete", "partial", "blocked"}
ROUTE_STATUS_VALUES = {"observed", "single_sample", "hypothesis"}
REPLICATION_READINESS_VALUES = {"ready", "conditional", "research_only"}
CARRIER_VALUES = {"post_body", "image_cards", "scene_images", "mixed", "on_screen_text", "voiceover", "synced_subtitles", "visual_sequence", "mixed_video", "unclear"}
VIDEO_CARRIERS = {"on_screen_text", "voiceover", "synced_subtitles", "visual_sequence", "mixed_video", "unclear"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
FINDING_TYPES = {"source_fact", "observed_pattern", "analysis_inference", "hypothesis", "human_confirmed"}
SOURCE_TYPES = {"title", "cover", "body", "image", "video", "frame", "transcript", "subtitle", "audio", "comment", "metric", "metadata", "other"}
AV_RELATIONS = {"repeat", "complement", "prove", "contrast", "advance", "decorative"}
CLAIM_CLASSES = {"observable", "product_fact", "personal_experience", "health_effect", "mechanism", "comparison", "other"}
SUPPORT_VALUES = {"supported", "conditional", "unsupported", "unknown"}
RISK_VALUES = {"low", "medium", "high", "unknown"}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def require_keys(value: dict[str, Any], keys: set[str], location: str) -> None:
    missing = sorted(keys - value.keys())
    require(not missing, f"{location}: missing keys: {', '.join(missing)}")


def require_string_list(value: Any, location: str, allow_empty: bool = True) -> list[str]:
    require(isinstance(value, list), f"{location}: expected an array")
    require(all(isinstance(item, str) and item for item in value), f"{location}: expected non-empty strings")
    require(allow_empty or bool(value), f"{location}: expected at least one item")
    return value


def require_non_empty_string(value: Any, location: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{location}: expected a non-empty string")
    return value


def require_string_fields(value: Any, fields: set[str], location: str) -> None:
    require(isinstance(value, dict), f"{location}: expected an object")
    require_keys(value, fields, location)
    for field in fields:
        require(isinstance(value[field], str), f"{location}.{field}: expected a string")


def is_absolute_local_path(value: str) -> bool:
    return value.startswith(("/", "~/", "file://")) or bool(re.match(r"^[A-Za-z]:[\\/]", value))


def collect_evidence_references(value: Any, location: str = "root") -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if key == "evidence_ids":
                for evidence_id in require_string_list(child, child_location):
                    references.append((child_location, evidence_id))
            else:
                references.extend(collect_evidence_references(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            references.extend(collect_evidence_references(child, f"{location}[{index}]"))
    return references


def validate_copy_segments(items: Any, location: str) -> None:
    require(isinstance(items, list), f"{location}: expected an array")
    fields = {"start", "end", "copy_summary", "copy_task", "viewer_effect", "viewer_shift", "evidence_status", "risk", "evidence_ids"}
    for index, item in enumerate(items):
        item_location = f"{location}[{index}]"
        require(isinstance(item, dict), f"{item_location}: expected an object")
        require_keys(item, fields, item_location)
        require(isinstance(item["start"], (int, float)) and item["start"] >= 0, f"{item_location}.start: invalid time")
        require(isinstance(item["end"], (int, float)) and item["end"] > item["start"], f"{item_location}.end: must be after start")
        for field in ("copy_summary", "copy_task", "viewer_effect", "viewer_shift", "risk"):
            require_non_empty_string(item[field], f"{item_location}.{field}")
        require(item["evidence_status"] in FINDING_TYPES, f"{item_location}.evidence_status: invalid value")
        require_string_list(item["evidence_ids"], f"{item_location}.evidence_ids", allow_empty=False)


def validate_video_analysis(video: Any, location: str) -> None:
    fields = {"content_promise", "timeline_segments", "opening_analysis", "on_screen_copy_analysis", "voiceover_copy_analysis", "persuasion_chain", "audio_visual_summary", "comment_signals"}
    require(isinstance(video, dict), f"{location}: expected an object")
    require_keys(video, fields, location)
    require_non_empty_string(video["content_promise"], f"{location}.content_promise")
    require_non_empty_string(video["audio_visual_summary"], f"{location}.audio_visual_summary")

    timeline = video["timeline_segments"]
    require(isinstance(timeline, list) and timeline, f"{location}.timeline_segments: expected at least one segment")
    timeline_fields = {"start", "end", "information_task", "spoken_copy", "on_screen_copy", "visual", "audio_visual_relation", "viewer_state_before", "viewer_state_after", "evidence_ids", "limitations"}
    for index, segment in enumerate(timeline):
        item_location = f"{location}.timeline_segments[{index}]"
        require(isinstance(segment, dict), f"{item_location}: expected an object")
        require_keys(segment, timeline_fields, item_location)
        require(isinstance(segment["start"], (int, float)) and segment["start"] >= 0, f"{item_location}.start: invalid time")
        require(isinstance(segment["end"], (int, float)) and segment["end"] > segment["start"], f"{item_location}.end: must be after start")
        for field in ("information_task", "visual", "viewer_state_before", "viewer_state_after"):
            require_non_empty_string(segment[field], f"{item_location}.{field}")
        require(isinstance(segment["spoken_copy"], str), f"{item_location}.spoken_copy: expected a string")
        require(isinstance(segment["on_screen_copy"], str), f"{item_location}.on_screen_copy: expected a string")
        require(segment["audio_visual_relation"] in AV_RELATIONS, f"{item_location}.audio_visual_relation: invalid value")
        require_string_list(segment["evidence_ids"], f"{item_location}.evidence_ids", allow_empty=False)
        require(isinstance(segment["limitations"], list), f"{item_location}.limitations: expected an array")

    opening = video["opening_analysis"]
    require(isinstance(opening, list) and opening, f"{location}.opening_analysis: expected at least one point")
    for index, point in enumerate(opening):
        item_location = f"{location}.opening_analysis[{index}]"
        require(isinstance(point, dict), f"{item_location}: expected an object")
        require_keys(point, {"time", "observation", "viewer_reason_to_continue", "evidence_ids"}, item_location)
        require(isinstance(point["time"], (int, float)) and 0 <= point["time"] <= 5, f"{item_location}.time: expected 0 to 5 seconds")
        require_non_empty_string(point["observation"], f"{item_location}.observation")
        require_non_empty_string(point["viewer_reason_to_continue"], f"{item_location}.viewer_reason_to_continue")
        require_string_list(point["evidence_ids"], f"{item_location}.evidence_ids", allow_empty=False)

    validate_copy_segments(video["on_screen_copy_analysis"], f"{location}.on_screen_copy_analysis")
    validate_copy_segments(video["voiceover_copy_analysis"], f"{location}.voiceover_copy_analysis")
    require(video["on_screen_copy_analysis"] or video["voiceover_copy_analysis"], f"{location}: on-screen copy and voiceover cannot both be empty")

    chain = video["persuasion_chain"]
    require(isinstance(chain, list), f"{location}.persuasion_chain: expected an array")
    for index, node in enumerate(chain):
        item_location = f"{location}.persuasion_chain[{index}]"
        require(isinstance(node, dict), f"{item_location}: expected an object")
        require_keys(node, {"node", "function", "viewer_shift", "evidence_ids"}, item_location)
        for field in ("node", "function", "viewer_shift"):
            require_non_empty_string(node[field], f"{item_location}.{field}")
        require_string_list(node["evidence_ids"], f"{item_location}.evidence_ids", allow_empty=False)
    require_string_list(video["comment_signals"], f"{location}.comment_signals")


def validate(data: Any) -> None:
    require(isinstance(data, dict), "root: expected a JSON object")
    require_keys(data, TOP_LEVEL_KEYS, "root")
    unexpected = sorted(data.keys() - TOP_LEVEL_ALLOWED_KEYS)
    require(not unexpected, f"root: unexpected keys: {', '.join(unexpected)}")
    require(data["analysis_status"] in STATUS_VALUES, "analysis_status: invalid value")
    require(data["media_type"] in MEDIA_TYPES, "media_type: invalid value")
    media_type = data["media_type"]

    scope = data["analysis_scope"]
    require(isinstance(scope, dict), "analysis_scope: expected an object")
    require_keys(scope, {"platform", "subject", "objective", "included_sample_ids", "excluded_samples", "limitations"}, "analysis_scope")
    require(scope["platform"] == "xiaohongshu", "analysis_scope.platform: expected xiaohongshu")
    require_non_empty_string(scope["subject"], "analysis_scope.subject")
    require_non_empty_string(scope["objective"], "analysis_scope.objective")
    included_ids = require_string_list(scope["included_sample_ids"], "analysis_scope.included_sample_ids")
    require(len(included_ids) == len(set(included_ids)), "analysis_scope.included_sample_ids: duplicate sample IDs")
    require(isinstance(scope["excluded_samples"], list), "analysis_scope.excluded_samples: expected an array")
    for index, record in enumerate(scope["excluded_samples"]):
        require(isinstance(record, dict), f"analysis_scope.excluded_samples[{index}]: expected an object")
        require_keys(record, {"sample_id", "reason"}, f"analysis_scope.excluded_samples[{index}]")
    require(isinstance(scope["limitations"], list), "analysis_scope.limitations: expected an array")

    evidence_ids: list[str] = []
    require(isinstance(data["evidence_records"], list), "evidence_records: expected an array")
    for index, record in enumerate(data["evidence_records"]):
        location = f"evidence_records[{index}]"
        require(isinstance(record, dict), f"{location}: expected an object")
        require_keys(record, {"evidence_id", "sample_id", "source_type", "locator", "observation"}, location)
        evidence_ids.append(require_non_empty_string(record["evidence_id"], f"{location}.evidence_id"))
        require(record["sample_id"] in included_ids, f"{location}.sample_id: not in included samples")
        require(record["source_type"] in SOURCE_TYPES, f"{location}.source_type: invalid value")
        locator = require_non_empty_string(record["locator"], f"{location}.locator")
        require(not is_absolute_local_path(locator), f"{location}.locator: use a relative path, stable ID, or URL")
        require_non_empty_string(record["observation"], f"{location}.observation")
    require(len(evidence_ids) == len(set(evidence_ids)), "evidence_records: duplicate evidence IDs")

    analyzed_ids: list[str] = []
    require(isinstance(data["sample_analyses"], list), "sample_analyses: expected an array")
    common_fields = {"sample_id", "user_task", "audience_problem", "product_role", "primary_carrier", "module_handoffs", "persuasion_nodes", "evidence_ids", "limitations"}
    for index, record in enumerate(data["sample_analyses"]):
        location = f"sample_analyses[{index}]"
        require(isinstance(record, dict), f"{location}: expected an object")
        require_keys(record, common_fields, location)
        analyzed_ids.append(record["sample_id"])
        require(record["sample_id"] in included_ids, f"{location}.sample_id: not in included samples")
        require(record["primary_carrier"] in CARRIER_VALUES, f"{location}.primary_carrier: invalid value")
        if media_type == "image_post":
            require_keys(record, {"component_analysis", "body_variables", "image_sequence_tasks"}, location)
            require_string_fields(record["component_analysis"], {"title", "cover", "opening_hook", "body", "image_sequence_and_carrier", "decision_close", "evidence_and_risk"}, f"{location}.component_analysis")
            require_string_fields(record["body_variables"], {"opening", "pain_organization", "product_entry", "value_translation", "experience_details", "final_judgment"}, f"{location}.body_variables")
            require_string_list(record["image_sequence_tasks"], f"{location}.image_sequence_tasks", allow_empty=False)
        else:
            require(record["primary_carrier"] in VIDEO_CARRIERS, f"{location}.primary_carrier: expected a video carrier")
            require_keys(record, {"video_analysis"}, location)
            validate_video_analysis(record["video_analysis"], f"{location}.video_analysis")
        require_string_list(record["module_handoffs"], f"{location}.module_handoffs")
        require_string_list(record["persuasion_nodes"], f"{location}.persuasion_nodes")
        require_string_list(record["evidence_ids"], f"{location}.evidence_ids", allow_empty=False)
        require(isinstance(record["limitations"], list), f"{location}.limitations: expected an array")
    require(set(analyzed_ids) == set(included_ids), "sample_analyses: must cover every included sample exactly once")
    require(len(analyzed_ids) == len(set(analyzed_ids)), "sample_analyses: duplicate sample IDs")

    route_ids: list[str] = []
    route_readiness: dict[str, str] = {}
    route_fields = {"route_id", "label", "status", "supporting_sample_ids", "user_task", "core_tension", "primary_carrier", "product_position_and_role", "use_conditions", "non_applicable_conditions", "module_handoffs", "persuasion_nodes", "contrary_evidence", "evidence_ids", "confidence", "limitations"}
    require(isinstance(data["route_findings"], list), "route_findings: expected an array")
    for index, route in enumerate(data["route_findings"]):
        location = f"route_findings[{index}]"
        require(isinstance(route, dict), f"{location}: expected an object")
        require_keys(route, route_fields, location)
        route_ids.append(require_non_empty_string(route["route_id"], f"{location}.route_id"))
        require(route["status"] in ROUTE_STATUS_VALUES, f"{location}.status: invalid value")
        require(route["primary_carrier"] in CARRIER_VALUES, f"{location}.primary_carrier: invalid value")
        require(route["confidence"] in CONFIDENCE_VALUES, f"{location}.confidence: invalid value")
        if "replication_readiness" in route:
            readiness = route["replication_readiness"]
            require(readiness in REPLICATION_READINESS_VALUES, f"{location}.replication_readiness: invalid value")
            route_readiness[route["route_id"]] = readiness
            if readiness == "conditional":
                require_string_list(route.get("blocking_inputs"), f"{location}.blocking_inputs", allow_empty=False)
        if "blocking_inputs" in route:
            require_string_list(route["blocking_inputs"], f"{location}.blocking_inputs")
        supporting = require_string_list(route["supporting_sample_ids"], f"{location}.supporting_sample_ids")
        require(set(supporting) <= set(included_ids), f"{location}.supporting_sample_ids: unknown sample ID")
        if route["status"] == "observed": require(len(set(supporting)) >= 2, f"{location}: observed routes require at least two samples")
        if route["status"] == "single_sample": require(len(set(supporting)) == 1, f"{location}: single_sample requires one sample")
    require(len(route_ids) == len(set(route_ids)), "route_findings: duplicate route IDs")

    for index, finding in enumerate(data["cross_sample_findings"]):
        require_keys(finding, {"finding", "finding_type", "scope", "evidence_ids", "confidence", "limitations"}, f"cross_sample_findings[{index}]")
        require(finding["finding_type"] in FINDING_TYPES, f"cross_sample_findings[{index}].finding_type: invalid value")
        require(finding["confidence"] in CONFIDENCE_VALUES, f"cross_sample_findings[{index}].confidence: invalid value")
    for index, boundary in enumerate(data["claim_boundaries"]):
        require_keys(boundary, {"claim", "classification", "support_status", "evidence_ids", "reason"}, f"claim_boundaries[{index}]")
        require(boundary["classification"] in CLAIM_CLASSES, f"claim_boundaries[{index}].classification: invalid value")
        require(boundary["support_status"] in SUPPORT_VALUES, f"claim_boundaries[{index}].support_status: invalid value")
    for index, item in enumerate(data.get("value_translations", [])):
        require_keys(item, {"user_friction", "feature_or_content_detail", "user_value", "product_role", "evidence_ids", "claim_risk"}, f"value_translations[{index}]")
        require(item["claim_risk"] in RISK_VALUES, f"value_translations[{index}].claim_risk: invalid value")
    for index, item in enumerate(data.get("replication_blueprints", [])):
        require_keys(item, {"route_id", "audience_and_task", "opening_fields", "timeline_tasks", "on_screen_copy_fields", "voiceover_fields", "shot_responsibilities", "product_entry", "objections_and_close", "success_conditions", "failure_conditions", "evidence_ids", "limitations"}, f"replication_blueprints[{index}]")
        require(item["route_id"] in route_ids, f"replication_blueprints[{index}].route_id: unknown route ID")
        require(route_readiness.get(item["route_id"]) != "research_only", f"replication_blueprints[{index}].route_id: research_only routes cannot have replication blueprints")

    evidence_id_set = set(evidence_ids)
    for location, evidence_id in collect_evidence_references({key: value for key, value in data.items() if key != "evidence_records"}):
        require(evidence_id in evidence_id_set, f"{location}: unknown evidence ID {evidence_id}")

    if "downstream_handoff" in data:
        handoff = data["downstream_handoff"]
        require(isinstance(handoff, dict), "downstream_handoff: expected an object")
        require_keys(handoff, {"usable_for_note_skill", "recommended_route_ids", "missing_inputs", "prohibited_assumptions"}, "downstream_handoff")
        require(isinstance(handoff["usable_for_note_skill"], bool), "downstream_handoff.usable_for_note_skill: expected boolean")
        recommended = require_string_list(handoff["recommended_route_ids"], "downstream_handoff.recommended_route_ids")
        require(set(recommended) <= set(route_ids), "downstream_handoff.recommended_route_ids: unknown route ID")
        require_string_list(handoff["missing_inputs"], "downstream_handoff.missing_inputs")
        require_string_list(handoff["prohibited_assumptions"], "downstream_handoff.prohibited_assumptions")
        for route_id in recommended:
            require(route_readiness.get(route_id) != "research_only", f"downstream_handoff.recommended_route_ids: {route_id} is research_only")
            if route_readiness.get(route_id) == "conditional":
                route = next(item for item in data["route_findings"] if item["route_id"] == route_id)
                require_string_list(route.get("blocking_inputs"), f"route_findings[{route_id}].blocking_inputs", allow_empty=False)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_analysis_result.py PATH", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
