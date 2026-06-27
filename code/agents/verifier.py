"""Claim verification agent – decides supported/contradicted/not_enough_information."""
import logging
from typing import List, Optional
from code.models.schemas import (
    ClaimIntent,
    VisualFinding,
    EvidenceAssessment,
    ClaimDecision,
    ClaimStatus,
    IssueType,
)

from code.agents.part_matcher import part_matches

logger = logging.getLogger("evidence_review")

# Damage types that should be treated as equivalent for verification
DAMAGE_EQUIVALENCE = {
    IssueType.crack: {IssueType.crack, IssueType.glass_shatter},
    IssueType.glass_shatter: {IssueType.glass_shatter, IssueType.crack},
    IssueType.dent: {IssueType.dent, IssueType.broken_part, IssueType.crushed_packaging},
    IssueType.broken_part: {IssueType.broken_part, IssueType.dent, IssueType.missing_part},
    IssueType.torn_packaging: {IssueType.torn_packaging, IssueType.broken_part},
    IssueType.crushed_packaging: {IssueType.crushed_packaging, IssueType.dent},
}

def _damage_matches(claimed: IssueType, observed: IssueType) -> bool:
    """Check if observed damage type matches claimed, including equivalence."""
    if claimed == observed:
        return True
    equiv = DAMAGE_EQUIVALENCE.get(claimed, set())
    return observed in equiv

def verify_claim(
    intent: ClaimIntent,
    findings: VisualFinding,
    evidence: EvidenceAssessment,
) -> ClaimDecision:
    """Compare the claim intent with the visual findings."""
    if not evidence.met:
        return ClaimDecision(
            status=ClaimStatus.not_enough_information,
            justification=evidence.reason,
            supporting_image_ids=[],
        )

    claimed_issue = intent.issue_type
    claimed_part = intent.object_part

    # Identify images that show the claimed part (synonym-aware fuzzy matching)
    images_with_part = [
        f for f in findings.per_image_findings
        if part_matches(claimed_part, f.visible_parts)
    ]
    if not images_with_part:
        return ClaimDecision(
            status=ClaimStatus.not_enough_information,
            justification=f"The claimed part '{claimed_part}' is not visible in any submitted image.",
            supporting_image_ids=[],
        )

    # Check if any of those images show an equivalent damage type
    matching_damage = [
        f for f in images_with_part
        if _damage_matches(claimed_issue, f.damage_type) and f.severity != "none"
    ]
    if matching_damage:
        ids = [f.image_id for f in matching_damage]
        justification = (
            f"The claimed {claimed_issue.value} on {claimed_part} is visible in "
            f"image(s): {', '.join(ids)}."
        )
        return ClaimDecision(
            status=ClaimStatus.supported,
            justification=justification,
            supporting_image_ids=ids,
        )

    # Relevant part visible but no matching damage → contradicted
    ids = [f.image_id for f in images_with_part]
    justification = (
        f"The {claimed_part} is visible in image(s): {', '.join(ids)}, "
        f"but no {claimed_issue.value} is observed. "
        f"Visible damage does not support the claim."
    )
    return ClaimDecision(
        status=ClaimStatus.contradicted,
        justification=justification,
        supporting_image_ids=ids,
    )