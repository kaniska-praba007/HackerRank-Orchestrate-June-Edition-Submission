from .pipeline.ingestion import load_claims, load_user_history, load_evidence_requirements, resolve_and_load_images
from .config import DATASET_DIR

if __name__ == "__main__":
    claims = load_claims(DATASET_DIR / "sample_claims.csv")
    history = load_user_history(DATASET_DIR / "user_history.csv")
    reqs = load_evidence_requirements(DATASET_DIR / "evidence_requirements.csv")

    # Test image loading for the first claim
    claim = claims[0]
    images = resolve_and_load_images(claim.image_paths, DATASET_DIR)
    for img in images:
        print(f"{img.image_id}: valid={img.valid}, error={img.error}")