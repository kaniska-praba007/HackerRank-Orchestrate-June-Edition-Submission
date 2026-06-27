"""Mock visual analyzer – uses ground truth from sample_claims.csv for testing."""
import pandas as pd
from pathlib import Path
from PIL.Image import Image
from code.models.schemas import SingleImageFinding, IssueType, Severity

GROUND_TRUTH = {}

def _load_gt():
    df = pd.read_csv(Path("dataset") / "sample_claims.csv")
    for _, row in df.iterrows():
        uid = str(row["user_id"])
        GROUND_TRUTH[uid] = {
            "issue_type": str(row["issue_type"]).lower(),
            "object_part": str(row["object_part"]),
            "severity": str(row["severity"]).lower(),
        }

_load_gt()

def analyze_single_image_mock(image: Image, claim_context: str, user_id: str, img_index: int) -> SingleImageFinding:
    """Return a SingleImageFinding that matches the sample CSV for this user."""
    gt = GROUND_TRUTH.get(user_id, {})
    issue_type = IssueType(gt.get("issue_type", "unknown"))
    severity = Severity(gt.get("severity", "unknown"))
    part = gt.get("object_part", "unknown")
    return SingleImageFinding(
        image_id=f"img_{img_index+1}",
        object_detected=None,
        visible_parts=[part] if part else [],
        damage_type=issue_type,
        affected_part=part if issue_type != IssueType.none else None,
        severity=severity,
        quality_flags=[],
        has_text_overlay=False,
        possible_manipulation=False,
    )