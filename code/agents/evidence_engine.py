"""Deterministic evidence sufficiency checker."""
import logging
from typing import List
from code.models.schemas import (
    ClaimIntent,
    VisualFinding,
    EvidenceRequirement,
    EvidenceAssessment,
)
from code.agents.part_matcher import part_matches

logger = logging.getLogger("evidence_review")

def _match_requirement(claim_object: str, issue_type: str, requirements: List[EvidenceRequirement]) -> EvidenceRequirement:
    """Find the most specific requirement for this claim."""
    best = None
    for req in requirements:
        if req.claim_object not in (claim_object, "all"):
            continue
        if issue_type in req.applies_to.lower() or issue_type == req.applies_to.lower():
            best = req
            break
    if best is None:
        for req in requirements:
            if req.requirement_id == "REQ_REVIEW_TRUST":
                best = req
                break
    return best

def check_evidence_sufficiency(
    claim_intent: ClaimIntent,
    findings: VisualFinding,
    requirements: List[EvidenceRequirement],
    claim_object: str = "unknown",
) -> EvidenceAssessment:
    """Determine if evidence standard is met based on visual findings."""
    obj = claim_object or "unknown"
    issue = claim_intent.issue_type.value if claim_intent.issue_type else "unknown"
    part = claim_intent.object_part

    req = _match_requirement(obj, issue, requirements)
    if not req:
        return EvidenceAssessment(met=False, reason="No applicable evidence requirement found.")

    # Check if any image shows the part (synonym-aware fuzzy match)
    images_with_part = [
        f for f in findings.per_image_findings
        if part_matches(part, f.visible_parts)
    ]

    if not images_with_part:
        return EvidenceAssessment(
            met=False,
            reason=f"None of the submitted images clearly show the {part}. Requirement: {req.minimum_image_evidence}"
        )

    return EvidenceAssessment(
        met=True,
        reason=f"At least one image ({images_with_part[0].image_id}) shows the {part} and allows assessment. Requirement: {req.minimum_image_evidence}"
    )