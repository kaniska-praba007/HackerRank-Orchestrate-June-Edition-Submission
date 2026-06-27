"""Output writer with schema validation and strict CSV compliance."""
import pandas as pd
from pathlib import Path
from typing import List
from code.models.schemas import (
    OutputRecord,
    RiskFlag,
    IssueType,
    Severity,
    ClaimStatus,
)

# Exact column order required by the spec
OUTPUT_COLUMNS = [
    "user_id",
    "image_paths",
    "user_claim",
    "claim_object",
    "evidence_standard_met",
    "evidence_standard_met_reason",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "claim_status_justification",
    "supporting_image_ids",
    "valid_image",
    "severity",
]

ALLOWED_RISK_FLAGS = {f.value for f in RiskFlag}
ALLOWED_ISSUE_TYPES = {t.value for t in IssueType}
ALLOWED_SEVERITIES = {s.value for s in Severity}
ALLOWED_CLAIM_STATUSES = {cs.value for cs in ClaimStatus}
ALLOWED_BOOLS = {"true", "false"}

def _validate_row(row: dict) -> dict:
    """Check each field against allowed values and fix if necessary."""
    # evidence_standard_met must be "true" or "false"
    if row["evidence_standard_met"] not in ALLOWED_BOOLS:
        row["evidence_standard_met"] = "false"
    # valid_image must be "true" or "false"
    if row["valid_image"] not in ALLOWED_BOOLS:
        row["valid_image"] = "false"
    # issue_type
    if row["issue_type"] not in ALLOWED_ISSUE_TYPES:
        row["issue_type"] = "unknown"
    # severity
    if row["severity"] not in ALLOWED_SEVERITIES:
        row["severity"] = "unknown"
    # claim_status
    if row["claim_status"] not in ALLOWED_CLAIM_STATUSES:
        row["claim_status"] = "not_enough_information"
    # risk_flags: split by semicolon and validate each flag, remove invalid ones
    flags = [f.strip() for f in row["risk_flags"].split(";") if f.strip()]
    clean_flags = [f for f in flags if f in ALLOWED_RISK_FLAGS]
    if not clean_flags:
        clean_flags = ["none"]
    row["risk_flags"] = ";".join(clean_flags)
    # supporting_image_ids: must be "none" or a semicolon-separated list of image IDs
    if not row["supporting_image_ids"] or row["supporting_image_ids"].strip() == "":
        row["supporting_image_ids"] = "none"
    return row

def write_output(records: List[OutputRecord], output_path: Path) -> None:
    """
    Convert a list of OutputRecord to a DataFrame, validate, and save as CSV.
    """
    rows = []
    for rec in records:
        row_dict = {
            "user_id": rec.user_id,
            "image_paths": rec.image_paths,
            "user_claim": rec.user_claim,
            "claim_object": rec.claim_object,
            "evidence_standard_met": rec.evidence_standard_met,
            "evidence_standard_met_reason": rec.evidence_standard_met_reason,
            "risk_flags": rec.risk_flags,
            "issue_type": rec.issue_type,
            "object_part": rec.object_part,
            "claim_status": rec.claim_status,
            "claim_status_justification": rec.claim_status_justification,
            "supporting_image_ids": rec.supporting_image_ids,
            "valid_image": rec.valid_image,
            "severity": rec.severity,
        }
        row_dict = _validate_row(row_dict)
        rows.append(row_dict)

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(records)} records to {output_path}")