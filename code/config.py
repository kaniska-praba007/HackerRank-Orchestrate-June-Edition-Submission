import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # load .env file for API keys if present

# Paths
BASE_DIR = Path(__file__).parent.parent   # root of the code directory
DATASET_DIR = BASE_DIR / "dataset"
IMAGE_DIR = DATASET_DIR / "images"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Models – Gemini 2.5 Flash handles both text and vision well
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")
GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")  # same model works

# Free tier considerations
MAX_IMAGES_PER_MINUTE = 3          # adjust based on your rate limit tier
MAX_TOKENS_PER_MINUTE = 40_000
LLM_REQUEST_TIMEOUT = 60           # seconds
VLM_REQUEST_TIMEOUT = 90

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "pipeline.log"

# Evaluation
SAMPLE_CLAIMS_PATH = DATASET_DIR / "sample_claims.csv"