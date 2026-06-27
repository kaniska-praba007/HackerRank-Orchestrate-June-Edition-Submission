"""Temporary mock parser – replace with real LLM after billing is active."""
from code.models.schemas import ClaimIntent, IssueType

MOCK_INTENTS = {
    "user_001": ClaimIntent(issue_type=IssueType.dent, object_part="rear_bumper", summary="Dent on rear bumper"),
    "user_002": ClaimIntent(issue_type=IssueType.broken_part, object_part="front_bumper", summary="Broken front bumper"),
    "user_004": ClaimIntent(issue_type=IssueType.crack, object_part="windshield", summary="Crack on windshield"),
    "user_007": ClaimIntent(issue_type=IssueType.broken_part, object_part="side_mirror", summary="Broken side mirror"),
    "user_005": ClaimIntent(issue_type=IssueType.scratch, object_part="rear_bumper", summary="Scratch on rear bumper"),
    "user_006": ClaimIntent(issue_type=IssueType.crack, object_part="headlight", summary="Cracked headlight"),
    "user_003": ClaimIntent(issue_type=IssueType.dent, object_part="door", summary="Dent on door"),
    "user_008": ClaimIntent(issue_type=IssueType.scratch, object_part="hood", summary="Scratch on hood"),
    "user_009": ClaimIntent(issue_type=IssueType.crack, object_part="screen", summary="Cracked laptop screen"),
    "user_010": ClaimIntent(issue_type=IssueType.broken_part, object_part="hinge", summary="Broken laptop hinge"),
    "user_011": ClaimIntent(issue_type=IssueType.stain, object_part="keyboard", summary="Stain on keyboard"),
    "user_012": ClaimIntent(issue_type=IssueType.dent, object_part="corner", summary="Dent on laptop corner"),
    "user_018": ClaimIntent(issue_type=IssueType.crack, object_part="screen", summary="Cracked laptop screen"),
    "user_020": ClaimIntent(issue_type=IssueType.none, object_part="trackpad", summary="Trackpad physical damage"),
    "user_015": ClaimIntent(issue_type=IssueType.crushed_packaging, object_part="package_corner", summary="Crushed package corner"),
    "user_030": ClaimIntent(issue_type=IssueType.torn_packaging, object_part="seal", summary="Torn seal on package"),
    "user_031": ClaimIntent(issue_type=IssueType.water_damage, object_part="package_side", summary="Water damage on package"),
    "user_032": ClaimIntent(issue_type=IssueType.missing_part, object_part="contents", summary="Missing contents from package"),
    "user_033": ClaimIntent(issue_type=IssueType.crushed_packaging, object_part="unknown", summary="Crushed shipping box"),
    "user_034": ClaimIntent(issue_type=IssueType.torn_packaging, object_part="seal", summary="Torn seal on package"),
}

def parse_claim_mock(user_id: str) -> ClaimIntent:
    return MOCK_INTENTS.get(user_id, ClaimIntent())