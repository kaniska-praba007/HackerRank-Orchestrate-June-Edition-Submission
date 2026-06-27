"""Data ingestion: CSV loaders and image resolver."""
import pandas as pd
from pathlib import Path
from typing import List, Dict
from PIL import Image
from code.models.schemas import (
    ClaimRecord,
    UserHistory,
    EvidenceRequirement,
    ImageInfo,
)

def load_claims(csv_path: Path) -> List[ClaimRecord]:
    """Load claims.csv and return a list of ClaimRecord."""
    df = pd.read_csv(csv_path)
    records = []
    for _, row in df.iterrows():
        # image_paths may be a string like "path1;path2"
        img_str = str(row.get("image_paths", ""))
        image_paths = [p.strip() for p in img_str.split(";") if p.strip()]
        records.append(
            ClaimRecord(
                user_id=str(row["user_id"]),
                image_paths=image_paths,
                user_claim=str(row["user_claim"]),
                claim_object=str(row.get("claim_object", "")) if pd.notna(row.get("claim_object")) else None,
            )
        )
    print(f"Loaded {len(records)} claims from {csv_path.name}")
    return records


def load_user_history(csv_path: Path) -> Dict[str, UserHistory]:
    """Load user_history.csv and return a dict keyed by user_id."""
    df = pd.read_csv(csv_path)
    history = {}
    for _, row in df.iterrows():
        user = UserHistory(
            user_id=str(row["user_id"]),
            past_claim_count=int(row["past_claim_count"]),
            accept_claim=int(row["accept_claim"]),
            manual_review_claim=int(row["manual_review_claim"]),
            rejected_claim=int(row["rejected_claim"]),
            last_90_days_claim_count=int(row["last_90_days_claim_count"]),
            history_flags=str(row["history_flags"]),
            history_summary=str(row["history_summary"]),
        )
        history[user.user_id] = user
    print(f"Loaded {len(history)} user history records from {csv_path.name}")
    return history


def load_evidence_requirements(csv_path: Path) -> List[EvidenceRequirement]:
    """Load evidence_requirements.csv and return a list of EvidenceRequirement."""
    df = pd.read_csv(csv_path)
    reqs = []
    for _, row in df.iterrows():
        reqs.append(
            EvidenceRequirement(
                requirement_id=str(row["requirement_id"]),
                claim_object=str(row["claim_object"]),
                applies_to=str(row["applies_to"]),
                minimum_image_evidence=str(row["minimum_image_evidence"]),
            )
        )
    print(f"Loaded {len(reqs)} evidence requirements from {csv_path.name}")
    return reqs


def resolve_and_load_images(relative_paths: List[str], base_dir: Path) -> List[ImageInfo]:
    """
    Given a list of relative paths (e.g., 'images/sample/case_001/img_1.jpg'),
    resolve them against base_dir (the dataset root), load images,
    and return ImageInfo objects.
    """
    images_info = []
    for rp in relative_paths:
        # Remove any leading/trailing slashes or backslashes
        rp = rp.strip().replace("\\", "/").lstrip("/")
        full_path = base_dir / rp
        image_id = Path(rp).stem  # filename without extension

        if not full_path.exists():
            images_info.append(
                ImageInfo(
                    image_id=image_id,
                    path=str(full_path),
                    valid=False,
                    error=f"File not found: {full_path}",
                )
            )
            continue

        try:
            pil_img = Image.open(full_path)
            # Optional: convert to RGB if needed
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            images_info.append(
                ImageInfo(
                    image_id=image_id,
                    path=str(full_path),
                    pil_image=pil_img,
                    valid=True,
                )
            )
        except Exception as e:
            images_info.append(
                ImageInfo(
                    image_id=image_id,
                    path=str(full_path),
                    valid=False,
                    error=f"Failed to open image: {str(e)}",
                )
            )
    return images_info