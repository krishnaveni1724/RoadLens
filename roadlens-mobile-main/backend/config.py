import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
WEB_DIR = PROJECT_DIR / "web"
MODEL_PATH = BACKEND_DIR / "models" / "road_damage.onnx"
POTHOLE_MODEL_PATH = BACKEND_DIR / "models" / "pothole_specialist.onnx"

# Centralized detection configuration. The ONNX model does not contain NMS.
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
MAX_DETECTIONS = 100
SUPPORTED_CLASS_IDS = frozenset({0, 1, 2, 3})

# Validation limits. Quality thresholds are deliberately conservative so a
# marginal image is not silently turned into a positive detection.
MAX_IMAGE_BYTES = 15 * 1024 * 1024
MIN_IMAGE_EDGE = 96
MIN_BRIGHTNESS = 8.0
MIN_BLUR_VARIANCE = 2.0

# Baseline severity heuristic. These are operational demo thresholds, not a
# scientifically validated civil-engineering severity scale.
SEVERITY_MEDIUM_AREA_RATIO = 0.04
SEVERITY_HIGH_AREA_RATIO = 0.15
SEVERITY_MEDIUM_COUNT = 2
SEVERITY_HIGH_COUNT = 4

DEBUG_INFERENCE = os.getenv("DEBUG_INFERENCE", "false").lower() in {"1", "true", "yes"}


def _uid_set(environment_name: str) -> frozenset[str]:
    return frozenset(
        uid.strip()
        for uid in os.getenv(environment_name, "").split(",")
        if uid.strip()
    )


FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "").strip()
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()
AUTH_DB_PATH = Path(os.getenv("AUTH_DB_PATH", str(BACKEND_DIR / "data" / "auth.db")))
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", str(BACKEND_DIR / "data" / "media")))
ROADLENS_ADMIN_UIDS = _uid_set("ROADLENS_ADMIN_UIDS")
ROADLENS_AUTHORITY_UIDS = _uid_set("ROADLENS_AUTHORITY_UIDS")

# ONNX Runtime's default CPU memory arena retains large allocations between
# requests. The production service runs two YOLO models on a 512 MB instance,
# so Render disables the arena and memory pattern to keep the worker below the
# platform limit after repeated inference calls.
ORT_INTRA_OP_THREADS = max(1, int(os.getenv("ORT_INTRA_OP_THREADS", "1")))
ORT_INTER_OP_THREADS = max(1, int(os.getenv("ORT_INTER_OP_THREADS", "1")))
ORT_DISABLE_CPU_ARENA = os.getenv("ORT_DISABLE_CPU_ARENA", "false").lower() in {"1", "true", "yes"}
ORT_DISABLE_MEMORY_PATTERN = os.getenv("ORT_DISABLE_MEMORY_PATTERN", "false").lower() in {"1", "true", "yes"}
