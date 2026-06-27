from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import datetime

# ---------- Enums ----------

class IssueType(str, Enum):
    dent = "dent"
    scratch = "scratch"
    crack = "crack"
    glass_shatter = "glass_shatter"
    broken_part = "broken_part"
    missing_part = "missing_part"
    torn_packaging = "torn_packaging"
    crushed_packaging = "crushed_packaging"
    water_damage = "water_damage"
    stain = "stain"
    none = "none"
    unknown = "unknown"

class Severity(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"
    unknown = "unknown"

    @classmethod
    def index(cls, sev: "Severity") -> int:
        """Return a numeric rank for severity comparison."""
        order = [cls.none, cls.unknown, cls.low, cls.medium, cls.high]
        return order.index(sev)

class RiskFlag(str, Enum):
    none = "none"
    blurry_image = "blurry_image"
    cropped_or_obstructed = "cropped_or_obstructed"
    low_light_or_glare = "low_light_or_glare"
    wrong_angle = "wrong_angle"
    wrong_object = "wrong_object"
    wrong_object_part = "wrong_object_part"
    damage_not_visible = "damage_not_visible"
    claim_mismatch = "claim_mismatch"
    possible_manipulation = "possible_manipulation"
    non_original_image = "non_original_image"
    text_instruction_present = "text_instruction_present"
    user_history_risk = "user_history_risk"
    manual_review_required = "manual_review_required"

class ClaimStatus(str, Enum):
    supported = "supported"
    contradicted = "contradicted"
    not_enough_information = "not_enough_information"

class ClaimRecord(BaseModel):
    """Raw input from claims.csv"""
    user_id: str
    image_paths: List[str]          # e.g., ["images/sample/case_001/img_1.jpg"]
    user_claim: str                 # the full conversation
    claim_object: Optional[str] = None  # car/laptop/package (may be empty in test CSV)

class UserHistory(BaseModel):
    """From user_history.csv"""
    user_id: str
    past_claim_count: int
    accept_claim: int
    manual_review_claim: int
    rejected_claim: int
    last_90_days_claim_count: int
    history_flags: str              # "none" or "user_history_risk;manual_review_required"
    history_summary: str

class EvidenceRequirement(BaseModel):
    """From evidence_requirements.csv"""
    requirement_id: str
    claim_object: str               # "all", "car", "laptop", "package"
    applies_to: str                 # free text: "dent or scratch", "crack, broken..."
    minimum_image_evidence: str     # description of the requirement

class ImageInfo(BaseModel):
    """Resolved image record"""
    image_id: str                   # filename without extension, e.g., "img_1"
    path: str                       # full path
    pil_image: Optional[object] = None  # PIL Image object, not serialisable by default
    valid: bool = True              # True if image loaded successfully
    error: Optional[str] = None     # reason if invalid

class ClaimIntent(BaseModel):
    """Output of claim parsing agent (Task 10-11)"""
    issue_type: IssueType = IssueType.unknown
    object_part: str = "unknown"
    summary: str = ""               # one-line summary of what user claims

class SingleImageFinding(BaseModel):
    """Per‑image output from VLM (Task 12)"""
    image_id: Optional[str] = None   # assigned later by the orchestrator
    object_detected: Optional[str] = None
    visible_parts: List[str] = Field(default_factory=list)
    damage_type: IssueType = IssueType.none
    affected_part: Optional[str] = None
    severity: Severity = Severity.none
    quality_flags: List[str] = Field(default_factory=list)
    has_text_overlay: bool = False
    possible_manipulation: bool = False

class VisualFinding(BaseModel):
    """Aggregated across all images of a claim (Task 13)"""
    overall_issue_type: IssueType = IssueType.none       # the most confident damage found
    overall_severity: Severity = Severity.none
    object_parts_visible: List[str] = Field(default_factory=list)
    per_image_findings: List[SingleImageFinding] = Field(default_factory=list)

class EvidenceAssessment(BaseModel):
    """Output of evidence sufficiency check (Task 16)"""
    met: bool = False
    reason: str = ""

class RiskAssessment(BaseModel):
    """Collected risk flags (Tasks 17-19)"""
    flags: List[RiskFlag] = Field(default_factory=list)

class ClaimDecision(BaseModel):
    """Final claim verification result (Task 20)"""
    status: ClaimStatus = ClaimStatus.not_enough_information
    justification: str = ""
    supporting_image_ids: List[str] = Field(default_factory=list)  # without extension

# ---------- Final Output Row ----------

class OutputRecord(BaseModel):
    """Exactly the columns required by output.csv (order matters)"""
    user_id: str
    image_paths: str                # original string from CSV, e.g., "img_1.jpg;img_2.jpg"
    user_claim: str
    claim_object: str
    evidence_standard_met: str      # "true" or "false"
    evidence_standard_met_reason: str
    risk_flags: str                 # semicolon‑separated flags
    issue_type: str                 # use IssueType.value
    object_part: str
    claim_status: str               # ClaimStatus.value
    claim_status_justification: str
    supporting_image_ids: str       # semicolon‑separated, or "none"
    valid_image: str                # "true" or "false"
    severity: str                   # Severity.value

