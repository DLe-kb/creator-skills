#!/usr/bin/env python3
"""Validate cross-report synthesis JSON without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ABSOLUTE_PATH = re.compile(r"^(?:file://|/(?:Users|home|private)/|[A-Za-z]:[\\/])", re.IGNORECASE)
ROOT_KEYS = {
    "synthesis_status", "platform", "synthesis_scope", "report_records", "evidence_records",
    "common_mechanisms", "route_families", "media_differences", "subject_differences",
    "applicability_levels", "diagnostic_questions", "claim_boundaries",
}
FINDING_TYPES = {"source_fact", "observed_pattern", "analysis_inference", "hypothesis", "human_confirmed"}
CONFIDENCE = {"high", "medium", "low"}


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def require_keys(value: dict, required: set[str], location: str, allowed: set[str] | None = None) -> None:
    require(isinstance(value, dict), f"{location}: expected an object")
    missing = required - set(value)
    require(not missing, f"{location}: missing keys: {', '.join(sorted(missing))}")
    if allowed is not None:
        extra = set(value) - allowed
        require(not extra, f"{location}: unexpected keys: {', '.join(sorted(extra))}")


def require_ids(value: object, location: str, allow_empty: bool = True) -> list[str]:
    require(isinstance(value, list), f"{location}: expected an array")
    require(allow_empty or bool(value), f"{location}: must not be empty")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{location}: IDs must be non-empty strings")
    require(len(value) == len(set(value)), f"{location}: duplicate IDs")
    return value


def validate(data: dict) -> None:
    required_root = ROOT_KEYS - {"diagnostic_questions"}
    require_keys(data, required_root, "root", ROOT_KEYS)
    require(data["synthesis_status"] in {"complete", "partial", "blocked"}, "synthesis_status: invalid value")
    require(data["platform"] == "xiaohongshu", "platform: expected xiaohongshu")

    scope = data["synthesis_scope"]
    require_keys(scope, {"subject", "objective", "included_report_ids", "limitations"}, "synthesis_scope", {"subject", "objective", "source_snapshot", "included_report_ids", "limitations"})
    included_report_ids = require_ids(scope["included_report_ids"], "synthesis_scope.included_report_ids", allow_empty=False)
    require(len(included_report_ids) >= 2, "synthesis_scope.included_report_ids: at least two reports required")

    report_ids: list[str] = []
    report_sample_ids: set[str] = set()
    report_fields = {"report_id", "subject", "media_type", "analysis_status", "source_class", "included_sample_count", "sample_ids", "locator", "limitations"}
    require(isinstance(data["report_records"], list) and len(data["report_records"]) >= 2, "report_records: at least two reports required")
    for index, report in enumerate(data["report_records"]):
        location = f"report_records[{index}]"
        require_keys(report, report_fields - {"locator"}, location, report_fields)
        report_id = report["report_id"]
        require(isinstance(report_id, str) and report_id.strip(), f"{location}.report_id: expected a non-empty string")
        report_ids.append(report_id)
        sample_ids = require_ids(report["sample_ids"], f"{location}.sample_ids")
        require(report["included_sample_count"] == len(sample_ids), f"{location}.included_sample_count: must equal sample_ids length")
        report_sample_ids.update(sample_ids)
        locator = report.get("locator")
        if locator:
            require(not ABSOLUTE_PATH.search(locator), f"{location}.locator: use a relative path or stable URL")
    require(len(report_ids) == len(set(report_ids)), "report_records: duplicate report IDs")
    require(set(included_report_ids) == set(report_ids), "synthesis_scope.included_report_ids: must match report_records")

    evidence_ids: list[str] = []
    evidence_report: dict[str, str] = {}
    evidence_fields = {"evidence_id", "report_id", "sample_id", "source_type", "locator", "observation"}
    for index, record in enumerate(data["evidence_records"]):
        location = f"evidence_records[{index}]"
        require_keys(record, evidence_fields - {"sample_id"}, location, evidence_fields)
        evidence_id = record["evidence_id"]
        require(isinstance(evidence_id, str) and evidence_id.strip(), f"{location}.evidence_id: expected a non-empty string")
        require(record["report_id"] in report_ids, f"{location}.report_id: unknown report ID")
        if record.get("sample_id") is not None:
            require(record["sample_id"] in report_sample_ids, f"{location}.sample_id: unknown sample ID")
        require(not ABSOLUTE_PATH.search(record["locator"]), f"{location}.locator: use a relative path or stable URL")
        evidence_ids.append(evidence_id)
        evidence_report[evidence_id] = record["report_id"]
    require(len(evidence_ids) == len(set(evidence_ids)), "evidence_records: duplicate evidence IDs")
    evidence_set = set(evidence_ids)

    mechanism_ids: list[str] = []
    mechanism_fields = {"mechanism_id", "label", "finding", "finding_type", "scope", "supporting_report_ids", "supporting_sample_ids", "supporting_evidence_ids", "representative_evidence_ids", "contrary_evidence", "confidence", "limitations"}
    for index, item in enumerate(data["common_mechanisms"]):
        location = f"common_mechanisms[{index}]"
        require_keys(item, mechanism_fields, location, mechanism_fields)
        mechanism_ids.append(item["mechanism_id"])
        reports = require_ids(item["supporting_report_ids"], f"{location}.supporting_report_ids", allow_empty=False)
        require(set(reports) <= set(report_ids), f"{location}.supporting_report_ids: unknown report ID")
        supporting = require_ids(item["supporting_evidence_ids"], f"{location}.supporting_evidence_ids", allow_empty=False)
        representative = require_ids(item["representative_evidence_ids"], f"{location}.representative_evidence_ids")
        require(set(supporting) <= evidence_set, f"{location}.supporting_evidence_ids: unknown evidence ID")
        require(set(representative) <= set(supporting), f"{location}.representative_evidence_ids: must be a subset of supporting evidence")
        require(item["finding_type"] in FINDING_TYPES, f"{location}.finding_type: invalid value")
        require(item["confidence"] in CONFIDENCE, f"{location}.confidence: invalid value")
        if item["finding_type"] == "observed_pattern":
            require(len(set(reports)) >= 2, f"{location}: observed_pattern requires at least two reports")
            covered = {evidence_report[evidence_id] for evidence_id in supporting}
            require(len(covered) >= 2, f"{location}: supporting evidence must cover at least two reports")
    require(len(mechanism_ids) == len(set(mechanism_ids)), "common_mechanisms: duplicate mechanism IDs")

    route_ids: list[str] = []
    route_fields = {"route_family_id", "label", "status", "user_task", "core_tension", "primary_carriers", "use_conditions", "non_applicable_conditions", "source_route_labels", "supporting_report_ids", "supporting_sample_ids", "supporting_evidence_ids", "representative_evidence_ids", "confidence", "limitations"}
    for index, item in enumerate(data["route_families"]):
        location = f"route_families[{index}]"
        require_keys(item, route_fields, location, route_fields)
        route_ids.append(item["route_family_id"])
        reports = require_ids(item["supporting_report_ids"], f"{location}.supporting_report_ids", allow_empty=False)
        supporting = require_ids(item["supporting_evidence_ids"], f"{location}.supporting_evidence_ids", allow_empty=False)
        representative = require_ids(item["representative_evidence_ids"], f"{location}.representative_evidence_ids")
        require(set(reports) <= set(report_ids), f"{location}.supporting_report_ids: unknown report ID")
        require(set(supporting) <= evidence_set, f"{location}.supporting_evidence_ids: unknown evidence ID")
        require(set(representative) <= set(supporting), f"{location}.representative_evidence_ids: must be a subset of supporting evidence")
        require(item["status"] in {"cross_report_observed", "single_report", "hypothesis"}, f"{location}.status: invalid value")
        require(item["confidence"] in CONFIDENCE, f"{location}.confidence: invalid value")
        if item["status"] == "cross_report_observed":
            require(len(set(reports)) >= 2, f"{location}: cross_report_observed requires at least two reports")
        if item["status"] == "single_report":
            require(len(set(reports)) == 1, f"{location}: single_report requires exactly one report")
    require(len(route_ids) == len(set(route_ids)), "route_families: duplicate route family IDs")

    for collection_name in ("media_differences", "subject_differences"):
        for index, item in enumerate(data[collection_name]):
            location = f"{collection_name}[{index}]"
            required = {"dimension", "finding", "finding_type", "supporting_report_ids", "evidence_ids", "confidence", "limitations"}
            require_keys(item, required, location, required)
            require(set(require_ids(item["supporting_report_ids"], f"{location}.supporting_report_ids")) <= set(report_ids), f"{location}.supporting_report_ids: unknown report ID")
            require(set(require_ids(item["evidence_ids"], f"{location}.evidence_ids")) <= evidence_set, f"{location}.evidence_ids: unknown evidence ID")
            require(item["finding_type"] in FINDING_TYPES, f"{location}.finding_type: invalid value")
            require(item["confidence"] in CONFIDENCE, f"{location}.confidence: invalid value")

    for index, item in enumerate(data["applicability_levels"]):
        location = f"applicability_levels[{index}]"
        required = {"level", "label", "statement", "support_status", "evidence_ids"}
        require_keys(item, required, location, required)
        require(item["level"] in {"direct_supported", "migration_candidate", "platform_hypothesis", "outcome_unverified"}, f"{location}.level: invalid value")
        require(set(require_ids(item["evidence_ids"], f"{location}.evidence_ids")) <= evidence_set, f"{location}.evidence_ids: unknown evidence ID")

    for index, item in enumerate(data.get("diagnostic_questions", [])):
        location = f"diagnostic_questions[{index}]"
        required = {"question", "judgment", "mechanism_ids"}
        require_keys(item, required, location, required)
        require(set(require_ids(item["mechanism_ids"], f"{location}.mechanism_ids", allow_empty=False)) <= set(mechanism_ids), f"{location}.mechanism_ids: unknown mechanism ID")

    for index, item in enumerate(data["claim_boundaries"]):
        location = f"claim_boundaries[{index}]"
        required = {"claim", "support_status", "evidence_ids", "reason"}
        require_keys(item, required, location, required)
        require(set(require_ids(item["evidence_ids"], f"{location}.evidence_ids")) <= evidence_set, f"{location}.evidence_ids: unknown evidence ID")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_synthesis_result.py PATH", file=sys.stderr)
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
