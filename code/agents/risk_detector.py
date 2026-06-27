"""Risk detection – image quality, object consistency, user history."""
import logging
from typing import List, Dict
from code.models.schemas import (
    ClaimIntent,
    VisualFinding,
    UserHistory,
    RiskFlag,
    IssueType,
    SingleImageFinding,
)

logger = logging.getLogger("evidence_review")

# Mapping from VLM quality string to RiskFlag
QUALITY_FLAG_MAP = {
    "blurry": RiskFlag.blurry_image,
    "glare": RiskFlag.low_light_or_glare,
    "dark": RiskFlag.low_light_or_glare,
    "cropped": RiskFlag.cropped_or_obstructed,
    "wrong_angle": RiskFlag.wrong_angle,
}

def check_image_quality(findings: List[SingleImageFinding]) -> List[RiskFlag]:
    """Extract risk flags from VLM quality_flags."""
    flags = []
    for f in findings:
        for qf in f.quality_flags:
            if qf in QUALITY_FLAG_MAP:
                flags.append(QUALITY_FLAG_MAP[qf])
    # Deduplicate
    return list(set(flags))

def check_object_consistency(
    intent: ClaimIntent, findings: VisualFinding, claimed_object: str
) -> List[RiskFlag]:
    """Check if the images match the claimed object and part."""
    flags = []

    # Wrong object check: if any image detected an object different from claimed_object
    for f in findings.per_image_findings:
        if f.object_detected and f.object_detected != claimed_object:
            flags.append(RiskFlag.wrong_object)
            break

    # Wrong object part: if claimed part not visible in any image
    claimed_part = intent.object_part
    if claimed_part not in findings.object_parts_visible and claimed_part != "unknown":
        flags.append(RiskFlag.wrong_object_part)

    # Claim mismatch: if visual damage type differs from claimed
    claimed_issue = intent.issue_type
    visual_issue = findings.overall_issue_type
    if (
        claimed_issue not in (IssueType.none, IssueType.unknown)
        and visual_issue not in (IssueType.none, IssueType.unknown)
        and claimed_issue != visual_issue
    ):
        flags.append(RiskFlag.claim_mismatch)

    return flags

def check_user_history(user_id: str, history: Dict[str, UserHistory]) -> List[RiskFlag]:
    """Add flags from user history."""
    flags = []
    uh = history.get(user_id)
    if not uh:
        return flags

    if "user_history_risk" in uh.history_flags:
        flags.append(RiskFlag.user_history_risk)
    if "manual_review_required" in uh.history_flags:
        flags.append(RiskFlag.manual_review_required)

    return flags