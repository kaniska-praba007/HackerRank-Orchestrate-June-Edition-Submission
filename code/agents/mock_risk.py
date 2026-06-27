"""Mock risk flags matching sample_claims.csv."""
from code.models.schemas import RiskFlag

MOCK_RISK_FLAGS = {
    "user_001": [RiskFlag.none],
    "user_002": [RiskFlag.wrong_object, RiskFlag.claim_mismatch, RiskFlag.manual_review_required],
    "user_004": [RiskFlag.none],
    "user_007": [RiskFlag.none],
    "user_005": [RiskFlag.claim_mismatch, RiskFlag.user_history_risk, RiskFlag.manual_review_required],
    "user_006": [RiskFlag.wrong_angle, RiskFlag.damage_not_visible],
    "user_003": [RiskFlag.blurry_image],
    "user_008": [RiskFlag.claim_mismatch, RiskFlag.non_original_image, RiskFlag.user_history_risk, RiskFlag.manual_review_required],
    "user_009": [RiskFlag.none],
    "user_010": [RiskFlag.none],
    "user_011": [RiskFlag.none],
    "user_012": [RiskFlag.none],
    "user_018": [RiskFlag.none],
    "user_020": [RiskFlag.damage_not_visible, RiskFlag.user_history_risk, RiskFlag.manual_review_required],
    "user_015": [RiskFlag.none],
    "user_030": [RiskFlag.none],
    "user_031": [RiskFlag.user_history_risk, RiskFlag.manual_review_required],
    "user_032": [RiskFlag.cropped_or_obstructed, RiskFlag.damage_not_visible, RiskFlag.manual_review_required],
    "user_033": [RiskFlag.wrong_object, RiskFlag.claim_mismatch, RiskFlag.user_history_risk, RiskFlag.manual_review_required],
    "user_034": [RiskFlag.damage_not_visible, RiskFlag.text_instruction_present, RiskFlag.user_history_risk, RiskFlag.manual_review_required],
}