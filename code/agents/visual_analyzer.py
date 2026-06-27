"""Visual analysis – Gemini vision with retry and robust damage parsing."""
import io
import base64
import json
import logging
from PIL.Image import Image
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from code.models.schemas import SingleImageFinding, IssueType
from code.config import GEMINI_VISION_MODEL, GEMINI_API_KEY
from code.services.retry_llm import create_retry_decorator

logger = logging.getLogger("evidence_review")

# Retry decorator for vision calls
retry_llm = create_retry_decorator(max_attempts=3)

vision_llm = ChatGoogleGenerativeAI(
    model=GEMINI_VISION_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
    max_output_tokens=2048,
)

# Ultra‑strict prompt: forces a single damage type
VISION_PROMPT = """You are a damage inspector. Analyse the image and return **only** a JSON object, no markdown. Use exactly this format:
{"object_detected":"car|laptop|package|null","visible_parts":["main part1"],"damage_type":"{allowed_issues}","affected_part":"part or null","severity":"none|low|medium|high|unknown","quality_flags":["blurry|glare|dark|cropped|wrong_angle"],"has_text_overlay":false,"possible_manipulation":false}

CRITICAL RULES:
- damage_type MUST be EXACTLY ONE of the allowed values.
- visible_parts: list the most specific parts visible (e.g., "front bumper", "rear bumper", "corner", "seal tape", "top flap", "hinge", "screen", "trackpad"). Avoid generic terms like "top" alone if more specific parts exist.
- If the claim context mentions a specific part, try to include that exact part if it is visible.
- If no damage, damage_type="none", severity="none", affected_part=null.
- If object unclear, object_detected=null, visible_parts=[].
- DO NOT include the claim context in the JSON.
- Return ONLY the JSON, no extra text."""

# Allowed issue types as a set for fast lookup
_ALLOWED_ISSUES = {t.value for t in IssueType}

def encode_image(pil_img: Image) -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def _clean_damage_type(raw: str) -> str:
    """Gemini sometimes returns 'dent, broken_part'. Pick the first valid one."""
    if not raw or raw in _ALLOWED_ISSUES:
        return raw if raw in _ALLOWED_ISSUES else "unknown"
    for token in raw.split(","):
        token = token.strip()
        if token in _ALLOWED_ISSUES:
            return token
    return "unknown"

def _parse_and_clean(raw: str) -> dict:
    """Clean markdown, fix truncation, and sanitise damage_type."""
    raw = raw.strip()
    # Remove markdown fences
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    # Attempt to fix truncation
    if not raw.endswith("}"):
        raw = raw.rstrip().rstrip(",") + '}'
    data = json.loads(raw)
    # Clean damage_type
    if "damage_type" in data:
        data["damage_type"] = _clean_damage_type(data["damage_type"])
    return data

def _invoke_vision_with_retry(messages: list) -> str:
    """Call vision LLM with retry logic, returning the raw response text."""
    @retry_llm
    def _call():
        response = vision_llm.invoke(messages)
        return response.content
    return _call()

def analyze_single_image(image: Image, claim_context: str) -> SingleImageFinding:
    allowed = ", ".join(_ALLOWED_ISSUES)
    prompt = VISION_PROMPT.replace("{allowed_issues}", allowed)
    user_text = f"Claim context: {claim_context}\n\n{prompt}"
    img_b64 = encode_image(image)

    msg = HumanMessage(content=[
        {"type": "text", "text": user_text},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
    ])

    try:
        response_text = _invoke_vision_with_retry([msg])
        data = _parse_and_clean(response_text)
        return SingleImageFinding.model_validate(data)
    except Exception as e:
        logger.error(f"Vision call failed after retries: {e}")
        return SingleImageFinding(
            damage_type=IssueType.unknown,
            severity="unknown",
        )