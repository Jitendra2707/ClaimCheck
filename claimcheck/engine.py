"""Deterministic verification engine for synthetic claim data.

This module checks a synthetic document checklist and selected extracted fields.
It does not authenticate documents, determine legal entitlement, approve claims,
or authorise payments.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class PolicyError(Exception):
    """Raised when a policy file cannot be loaded or is malformed."""


def load_policy(path: str | Path | None = None) -> dict[str, Any]:
    policy_path = Path(path) if path else Path(__file__).with_name("policies.json")
    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"Could not load policy: {exc}") from exc
    if not isinstance(policy.get("claim_types"), dict):
        raise PolicyError("Policy must contain a claim_types object")
    if not isinstance(policy.get("recognised_document_types"), list):
        raise PolicyError("Policy must contain recognised_document_types")
    return policy


def _normalise_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).casefold().strip().split())


def _normalise_date(value: Any) -> str:
    """Normalise supported date formats; leave unparseable values unchanged."""
    raw = _normalise_text(value)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return raw


def _normalise_field(field_name: str, value: Any) -> str:
    if field_name == "date_of_death":
        return _normalise_date(value)
    return _normalise_text(value)


def verify_claim(case: dict[str, Any], policy: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return an explainable checklist and consistency report for one case."""
    if not isinstance(case, dict):
        raise ValueError("Case must be a JSON object")
    policy = policy or load_policy()
    claim_id = case.get("claim_id", "UNKNOWN")
    claim_type = case.get("claim_type")
    claim_types = policy.get("claim_types", {})

    report: dict[str, Any] = {
        "claim_id": claim_id,
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("version"),
        "status": None,
        "missing_documents": [],
        "unrecognised_document_types": [],
        "duplicate_document_types": [],
        "field_mismatches": [],
        "low_confidence_fields": [],
        "invalid_confidence_metadata": [],
        "missing_or_unreadable_fields": [],
        "warnings": [],
        "scope_notice": "Document checks only. This is not legal verification, claim approval, or payment authorisation.",
    }

    if claim_type not in claim_types:
        report["status"] = "REVIEW_REQUIRED"
        report["warnings"].append(f"Unsupported or unspecified claim type: {claim_type!r}")
        return report

    documents = case.get("documents", [])
    if not isinstance(documents, list) or any(not isinstance(doc, dict) for doc in documents):
        raise ValueError("documents must be a list of document objects")

    recognised = set(policy["recognised_document_types"])
    doc_types = [doc.get("document_type") for doc in documents if doc.get("document_type")]
    present = set(doc_types)
    required = set(claim_types[claim_type].get("required_documents", []))

    report["missing_documents"] = sorted(required - present)
    report["unrecognised_document_types"] = sorted(
        {doc_type for doc_type in doc_types if doc_type not in recognised}
    )
    if report["unrecognised_document_types"]:
        report["warnings"].append("One or more uploaded documents could not be classified against the configured document list.")

    report["duplicate_document_types"] = sorted(
        doc_type for doc_type in set(doc_types) if doc_types.count(doc_type) > 1
    )
    if report["duplicate_document_types"]:
        report["warnings"].append("Duplicate document types were uploaded; duplicates do not satisfy additional requirements.")

    required_fields_by_document = policy.get("required_fields_by_document", {})
    for doc in documents:
        doc_type = doc.get("document_type")
        fields = doc.get("fields", {})
        if not isinstance(fields, dict):
            report["missing_or_unreadable_fields"].append({
                "document_id": doc.get("document_id", "UNKNOWN"),
                "document_type": doc_type,
                "field": "*",
                "reason": "Extracted fields are not a valid object; inspect the original document.",
            })
            continue
        for field_name in required_fields_by_document.get(doc_type, []):
            if fields.get(field_name) in (None, ""):
                report["missing_or_unreadable_fields"].append({
                    "document_id": doc.get("document_id", "UNKNOWN"),
                    "document_type": doc_type,
                    "field": field_name,
                    "reason": "Required field was not extracted; inspect the original document.",
                })

    threshold = float(policy.get("minimum_ocr_confidence", 0.85))
    for doc in documents:
        fields = doc.get("fields", {})
        confidences = doc.get("field_confidence", {})
        if not isinstance(fields, dict) or not isinstance(confidences, dict):
            continue
        for field_name, raw_confidence in confidences.items():
            try:
                confidence = float(raw_confidence)
            except (TypeError, ValueError):
                confidence = None
            if confidence is None or not 0.0 <= confidence <= 1.0:
                report["invalid_confidence_metadata"].append({
                    "document_id": doc.get("document_id", "UNKNOWN"),
                    "field": field_name,
                    "value": raw_confidence,
                })
            elif fields.get(field_name) not in (None, "") and confidence < threshold:
                report["low_confidence_fields"].append({
                    "document_id": doc.get("document_id", "UNKNOWN"),
                    "field": field_name,
                    "confidence": confidence,
                    "threshold": threshold,
                })

    for field_name in policy.get("comparison_fields", []):
        observations = []
        for doc in documents:
            fields = doc.get("fields", {})
            if not isinstance(fields, dict):
                continue
            value = fields.get(field_name)
            if value not in (None, ""):
                observations.append({
                    "document_id": doc.get("document_id", "UNKNOWN"),
                    "document_type": doc.get("document_type", "UNKNOWN"),
                    "value": str(value),
                })
        distinct = {_normalise_field(field_name, item["value"]) for item in observations}
        if len(distinct) > 1:
            report["field_mismatches"].append({
                "field": field_name,
                "observations": observations,
                "reason": "Different extracted values were found across submitted documents.",
            })

    if report["missing_documents"]:
        report["status"] = "INCOMPLETE"
    elif any(report[key] for key in (
        "unrecognised_document_types", "field_mismatches", "low_confidence_fields",
        "invalid_confidence_metadata", "missing_or_unreadable_fields",
    )):
        report["status"] = "REVIEW_REQUIRED"
    else:
        report["status"] = "CHECKS_PASSED"
    return report
