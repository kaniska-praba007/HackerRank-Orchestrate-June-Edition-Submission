"""LangGraph orchestrator shell – no AI, placeholder outputs."""
import logging
from pathlib import Path
from typing import List, Dict
from PIL.Image import Image
from code.models.schemas import VisualFinding, IssueType, Severity
from code.agents.visual_analyzer import analyze_single_image
from code.agents.mock_visual_analyzer import analyze_single_image_mock
from langgraph.graph import StateGraph, END
from code.pipeline.state import PipelineState
from code.pipeline.ingestion import resolve_and_load_images

from code.agents.risk_detector import check_image_quality, check_object_consistency, check_user_history
from code.agents.mock_risk import MOCK_RISK_FLAGS

from code.models.schemas import (
    ClaimRecord,
    UserHistory,
    EvidenceRequirement,
    VisualFinding,
    SingleImageFinding,
    EvidenceAssessment,
    RiskFlag,
    ClaimDecision,
    ClaimStatus,
    OutputRecord,
    IssueType,
    Severity,
)
from code.config import DATASET_DIR

logger = logging.getLogger("evidence_review")

# ---------- Dummy node implementations ----------
from code.agents.claim_parser import parse_claim as llm_parse_claim
from code.agents.mock_claim_parser import parse_claim_mock

def parse_claim(state: PipelineState) -> PipelineState:
    """Parse claim intent – uses mock when API is unavailable."""
    if USE_MOCK_PARSER:
        intent = parse_claim_mock(state["claim"].user_id)
    else:
        intent = llm_parse_claim(state["claim"].user_claim)
    state["claim_intent"] = intent
    logger.info(f"Parsed intent: {intent.issue_type.value} on {intent.object_part}")
    return state


def load_images(state: PipelineState) -> PipelineState:
    """Load images from resolved paths."""
    claim = state["claim"]
    images_info = resolve_and_load_images(claim.image_paths, DATASET_DIR)
    valid_images = [img.pil_image for img in images_info if img.valid]
    if not valid_images:
        state["error"] = "No valid images found"
        return state
    state["images"] = valid_images
    logger.info(f"Loaded {len(valid_images)} images")
    return state

# Add this near the top of the file, after the imports
USE_MOCK_PARSER = False
USE_MOCK_VLM   = False
USE_MOCK_RISK  = False
def analyze_images(state: PipelineState) -> PipelineState:
    """Analyze each image using VLM (or mock) and aggregate findings."""
    images = state["images"]
    claim = state["claim"]
    intent = state.get("claim_intent")
    summary = intent.summary if intent else claim.user_claim

    per_image_findings = []
    for i, img in enumerate(images):
        if USE_MOCK_VLM:
            finding = analyze_single_image_mock(img, summary, claim.user_id, i)
        else:
            finding = analyze_single_image(img, summary)
            finding.image_id = f"img_{i+1}"   # ensure image ID is set
        per_image_findings.append(finding)

    # Aggregate across images
    overall_issue = IssueType.none
    overall_severity = Severity.none
    all_parts = []
    for f in per_image_findings:
        if f.damage_type != IssueType.none:
            overall_issue = f.damage_type
        if f.severity != Severity.none and f.severity != Severity.unknown:
            if Severity.index(f.severity) > Severity.index(overall_severity):
                overall_severity = f.severity
        all_parts.extend(f.visible_parts)

    state["findings"] = VisualFinding(
        overall_issue_type=overall_issue,
        overall_severity=overall_severity,
        object_parts_visible=list(set(all_parts)),
        per_image_findings=per_image_findings,
    )
    logger.info(f"Visual findings: {overall_issue.value} on {all_parts}, severity={overall_severity.value}")
    return state

from code.agents.evidence_engine import check_evidence_sufficiency

def check_evidence(state: PipelineState) -> PipelineState:
    intent = state.get("claim_intent")
    findings = state["findings"]
    requirements = state.get("requirements", [])
    if not intent or not requirements:
        state["evidence"] = EvidenceAssessment(met=False, reason="Missing claim intent or evidence requirements.")
        return state

    assessment = check_evidence_sufficiency(
        intent,
        findings,
        requirements,
        claim_object=state["claim"].claim_object or "unknown",   # pass the actual claim object
    )
    state["evidence"] = assessment
    logger.info(f"Evidence standard met: {assessment.met} – {assessment.reason}")
    return state
    
def assess_risks(state: PipelineState) -> PipelineState:
    """Detect image quality, object consistency, and user history risks."""
    claim = state["claim"]
    intent = state.get("claim_intent")
    findings = state["findings"]
    history = state.get("user_history", {})

    if USE_MOCK_RISK:
        # Use pre-defined risk flags from sample CSV
        risks = MOCK_RISK_FLAGS.get(claim.user_id, [RiskFlag.none])
    else:
        risks = []
        # 1. Image quality risks
        risks.extend(check_image_quality(findings.per_image_findings))
        # 2. Object consistency
        claimed_obj = claim.claim_object or ""
        if intent:
            risks.extend(check_object_consistency(intent, findings, claimed_obj))
        # 3. User history
        risks.extend(check_user_history(claim.user_id, history))
        if not risks:
            risks = [RiskFlag.none]

    state["risks"] = risks
    risk_str = ";".join([r.value for r in risks])
    logger.info(f"Risk flags: {risk_str}")
    return state

from code.agents.verifier import verify_claim as decide_claim_status

def verify_claim(state: PipelineState) -> PipelineState:
    """Produce final claim status based on evidence and findings."""
    intent = state.get("claim_intent")
    findings = state["findings"]
    evidence = state.get("evidence")

    if not intent:
        state["decision"] = ClaimDecision(
            status=ClaimStatus.not_enough_information,
            justification="No claim intent could be extracted.",
            supporting_image_ids=[],
        )
        return state

    decision = decide_claim_status(intent, findings, evidence)
    state["decision"] = decision
    logger.info(f"Claim status: {decision.status.value} – {decision.justification}")
    return state

def create_output_record(state: PipelineState) -> OutputRecord:
    """Convert final state into an OutputRecord."""
    claim = state["claim"]
    risk_flags_str = ";".join([r.value for r in state.get("risks", [])])
    return OutputRecord(
        user_id=claim.user_id,
        image_paths=";".join(claim.image_paths),
        user_claim=claim.user_claim,
        claim_object=claim.claim_object or "",
        evidence_standard_met="false" if not state.get("evidence", EvidenceAssessment()).met else "true",
        evidence_standard_met_reason=state.get("evidence", EvidenceAssessment()).reason,
        risk_flags=risk_flags_str,
        issue_type=state["findings"].overall_issue_type.value,
        object_part=", ".join(state["findings"].object_parts_visible),
        claim_status=state["decision"].status.value,
        claim_status_justification=state["decision"].justification,
        supporting_image_ids="none" if not state["decision"].supporting_image_ids else ";".join(state["decision"].supporting_image_ids),
        valid_image="true" if state.get("images") else "false",
        severity=state["findings"].overall_severity.value,
    )

# ---------- Graph construction ----------

def build_graph() -> StateGraph:
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("parse_claim", parse_claim)
    workflow.add_node("load_images", load_images)
    workflow.add_node("analyze_images", analyze_images)
    workflow.add_node("check_evidence", check_evidence)
    workflow.add_node("assess_risks", assess_risks)
    workflow.add_node("verify_claim", verify_claim)

    # Edges
    workflow.set_entry_point("parse_claim")
    workflow.add_edge("parse_claim", "load_images")
    workflow.add_edge("load_images", "analyze_images")
    workflow.add_edge("analyze_images", "check_evidence")
    workflow.add_edge("check_evidence", "assess_risks")
    workflow.add_edge("assess_risks", "verify_claim")
    workflow.add_edge("verify_claim", END)

    return workflow.compile()

# ---------- Processing functions ----------

def process_claim(claim, history, requirements) -> OutputRecord:
    graph = build_graph()
    initial_state: PipelineState = {
        "claim": claim,
        "claim_intent": None,
        "images": [],
        "findings": VisualFinding(),
        "evidence": EvidenceAssessment(),
        "risks": [],
        "decision": None,
        "error": None,
        "requirements": requirements,
        "user_history": history,
    }
    final_state = graph.invoke(initial_state)

    # Fallback in case parse_claim node somehow leaves claim_intent as None
    if not final_state.get("claim_intent"):
        from code.models.schemas import ClaimIntent
        final_state["claim_intent"] = ClaimIntent(
            issue_type="unknown",
            object_part="unknown",
            summary="Parsing unavailable"
        )

    return create_output_record(final_state)

def process_dataset(claims_csv: Path, history_csv: Path,
                    requirements_csv: Path, output_csv: Path) -> None:
    """Load all data, process each claim, write output."""
    from code.pipeline.ingestion import load_claims, load_user_history, load_evidence_requirements
    from code.pipeline.output_writer import write_output

    claims = load_claims(claims_csv)
    history = load_user_history(history_csv)
    reqs = load_evidence_requirements(requirements_csv)

    output_records = []
    for i, claim in enumerate(claims):
        logger.info(f"Processing claim {i+1}/{len(claims)} for user {claim.user_id}")
        try:
            record = process_claim(claim, history, reqs)
            output_records.append(record)
        except Exception as e:
            logger.error(f"Failed to process claim for user {claim.user_id}: {str(e)}")
            # Append a fallback error record with unknown status
            output_records.append(OutputRecord(
                user_id=claim.user_id,
                image_paths=";".join(claim.image_paths),
                user_claim=claim.user_claim,
                claim_object=claim.claim_object or "",
                evidence_standard_met="false",
                evidence_standard_met_reason="Processing error",
                risk_flags="manual_review_required",
                issue_type="unknown",
                object_part="unknown",
                claim_status="not_enough_information",
                claim_status_justification="Pipeline error prevented full analysis",
                supporting_image_ids="none",
                valid_image="false",
                severity="unknown",
            ))

    write_output(output_records, output_csv)
    logger.info(f"Finished processing. Output written to {output_csv}")