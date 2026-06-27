from typing import TypedDict, List, Optional, Dict
from PIL.Image import Image
from code.models.schemas import (
    ClaimRecord,
    ClaimIntent,
    VisualFinding,
    EvidenceAssessment,
    RiskFlag,
    ClaimDecision,
    EvidenceRequirement,   # added
    UserHistory,           # added
)

class PipelineState(TypedDict, total=False):
    claim: ClaimRecord
    claim_intent: Optional[ClaimIntent]
    images: List[Image]
    findings: VisualFinding
    evidence: EvidenceAssessment
    risks: List[RiskFlag]
    decision: Optional[ClaimDecision]
    error: Optional[str]
    # Phase 6 additions
    requirements: List[EvidenceRequirement]
    user_history: Dict[str, UserHistory]