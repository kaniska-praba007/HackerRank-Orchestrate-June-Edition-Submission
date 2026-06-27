"""Quick test: Gemini vision on a single image."""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from PIL import Image
from code.agents.visual_analyzer import analyze_single_image

# Use the first sample image (car with dent on rear bumper)
img_path = Path("dataset/images/sample/case_001/img_1.jpg")
image = Image.open(img_path).convert("RGB")
claim_context = "The user claims a dent on the rear bumper."

finding = analyze_single_image(image, claim_context)
print(f"Object detected: {finding.object_detected}")
print(f"Visible parts : {finding.visible_parts}")
print(f"Damage type   : {finding.damage_type.value}")
print(f"Affected part : {finding.affected_part}")
print(f"Severity      : {finding.severity.value}")
print(f"Quality flags : {finding.quality_flags}")