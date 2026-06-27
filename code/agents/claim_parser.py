"""Claim Parsing Agent – extracts intent from user conversation with retry logic."""
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from code.models.schemas import ClaimIntent, IssueType
from code.config import GEMINI_LLM_MODEL, GEMINI_API_KEY
from code.services.retry_llm import create_retry_decorator

logger = logging.getLogger("evidence_review")

# Create retry decorator for Gemini calls
retry_llm = create_retry_decorator(max_attempts=3)

# Single LLM instance
llm = ChatGoogleGenerativeAI(
    model=GEMINI_LLM_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
    max_output_tokens=200,
)

CLAIM_PARSER_SYSTEM = """You are an insurance claim parser. 
Extract from the user conversation:
- The claimed issue type (damage category)
- The claimed object part (e.g., rear_bumper, screen, keyboard, package_corner)
- A one‑sentence summary of what the user is claiming.

Allowed issue types: {allowed_issues}

Mapping examples:
- "cracked screen" → crack
- "broken hinge" → broken_part
- "scratched bumper" → scratch
- "torn seal" → torn_packaging
- "water stain on side" → water_damage (or stain depending on description)
- "missing item" → missing_part
- "crushed corner" → crushed_packaging

If the claim mentions multiple issues, pick the one the user seems most concerned about. 
If the conversation is ambiguous or does not clearly identify an issue or part, set both to "unknown".

Return a JSON object with the following keys:
- issue_type (string, one of the allowed types)
- object_part (string)
- summary (string)
"""

def _invoke_chain_with_retry(chain, inputs):
    """Helper that applies the retry decorator to the chain invoke."""
    @retry_llm
    def _call():
        return chain.invoke(inputs)
    return _call()

def parse_claim(user_claim: str) -> ClaimIntent:
    """Parse a user claim conversation into a ClaimIntent with automatic retries."""
    allowed_issues = ", ".join([t.value for t in IssueType])
    prompt = ChatPromptTemplate.from_messages([
        ("system", CLAIM_PARSER_SYSTEM),
        ("human", "{user_claim}"),
    ])
    prompt = prompt.partial(allowed_issues=allowed_issues)
    chain = prompt | llm.with_structured_output(ClaimIntent)

    try:
        result = _invoke_chain_with_retry(chain, {"user_claim": user_claim})
        logger.debug(f"Parsed claim: {result.model_dump()}")
        return result
    except Exception as e:
        logger.error(f"Claim parsing failed after retries: {e}")
        return ClaimIntent(
            issue_type="unknown",
            object_part="unknown",
            summary="Parsing error"
        )