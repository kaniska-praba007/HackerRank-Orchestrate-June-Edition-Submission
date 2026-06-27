"""Shared part matching with synonyms."""
from typing import List

# Synonyms: if the claimed part contains any of these keys, any synonym value counts as a match
PART_SYNONYMS = {
    "corner": ["corner", "edge"],
    "seal": ["seal", "tape", "flap", "tamper-evident tape"],
    "surface": ["surface", "side", "top", "front", "back", "panel", "flap"],
    "box": ["box", "cardboard", "package", "shipping box"],
    "contents": ["contents", "inside", "item", "product"],
    "shipping": ["box", "package", "cardboard"],
    "hood": ["hood", "bonnet"],
    "windshield": ["windshield", "windscreen"],
    "side mirror": ["side mirror", "wing mirror"],
    "display": ["display", "screen"],
    "trackpad": ["trackpad", "touchpad"],
}

def normalize(text: str) -> str:
    return text.lower().replace("_", " ").replace("-", " ").strip()

def part_matches(claimed: str, visible_parts: List[str]) -> bool:
    """
    Check if the claimed part is visible in the list of visible parts.
    Uses normalization, substring, and synonym expansion.
    """
    claimed_norm = normalize(claimed)
    for vp in visible_parts:
        vp_norm = normalize(vp)
        # Direct match
        if claimed_norm == vp_norm:
            return True
        # Substring in either direction
        if claimed_norm in vp_norm or vp_norm in claimed_norm:
            return True
    # Synonym expansion
    for keyword, synonyms in PART_SYNONYMS.items():
        if keyword in claimed_norm:
            for syn in synonyms:
                for vp in visible_parts:
                    vp_norm = normalize(vp)
                    if syn in vp_norm or vp_norm in syn:
                        return True
    return False