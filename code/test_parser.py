from code.agents.claim_parser import parse_claim

sample = "Customer: There is a dent on my car door. | Support: When did you notice it?"
intent = parse_claim(sample)
print(f"Issue type : {intent.issue_type.value}")
print(f"Object part: {intent.object_part}")
print(f"Summary    : {intent.summary}")