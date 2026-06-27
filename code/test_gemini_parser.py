"""Quick test: Gemini claim parsing."""
from dotenv import load_dotenv
load_dotenv()

from code.agents.claim_parser import parse_claim

sample = "Customer: There is a dent on my car door. | Support: When did you notice it?"
result = parse_claim(sample)
print(f"Issue type : {result.issue_type.value}")
print(f"Object part: {result.object_part}")
print(f"Summary    : {result.summary}")