from dataclasses import dataclass

from . import config


@dataclass(frozen=True)
class SeverityResult:
    level: str
    damage_area_ratio: float
    method: str = "baseline severity heuristic"


def calculate_severity(detections: list[dict], image_width: int, image_height: int) -> SeverityResult | None:
    """Return a deterministic, configurable baseline based on measurable boxes."""
    if not detections:
        return None

    image_area = max(1, image_width * image_height)
    damaged_area = 0.0
    for detection in detections:
        box = detection["bbox"]
        damaged_area += max(0.0, box["x2"] - box["x1"]) * max(0.0, box["y2"] - box["y1"])
    ratio = min(1.0, damaged_area / image_area)

    if ratio >= config.SEVERITY_HIGH_AREA_RATIO or len(detections) >= config.SEVERITY_HIGH_COUNT:
        level = "HIGH"
    elif ratio >= config.SEVERITY_MEDIUM_AREA_RATIO or len(detections) >= config.SEVERITY_MEDIUM_COUNT:
        level = "MEDIUM"
    else:
        level = "LOW"
    return SeverityResult(level=level, damage_area_ratio=ratio)
