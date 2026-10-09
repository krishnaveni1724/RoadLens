from __future__ import annotations


RECOMMENDED_MAINTENANCE_ACTIONS = {
    "Pothole": (
        "Clean the damaged area, remove loose material, place a suitable "
        "asphalt patch, compact it thoroughly, and seal the edges."
    ),
    "Longitudinal Crack": (
        "Clean and dry the crack, then apply a suitable crack-sealing material "
        "to limit water entry and further deterioration."
    ),
    "Transverse Crack": (
        "Clean and dry the crack, then apply a suitable crack-sealing material "
        "and inspect the surrounding pavement for movement."
    ),
    "Alligator Crack": (
        "Arrange an engineering inspection. Remove failed pavement where "
        "necessary and consider full-depth patching or resurfacing."
    ),
}


def recommended_maintenance_action(
    detections: list[dict], severity_level: str | None
) -> str | None:
    """Return advisory maintenance text derived only from detected model classes."""
    if not detections:
        return None

    # Prefer the class covering the largest detected region; confidence breaks ties.
    primary = max(
        detections,
        key=lambda item: (
            _box_area(item.get("bbox") or {}),
            float(item.get("confidence") or 0.0),
        ),
    )
    action = RECOMMENDED_MAINTENANCE_ACTIONS.get(str(primary.get("damage_type")))
    if action is None:
        action = (
            "Arrange a qualified road-maintenance inspection to confirm the "
            "appropriate repair method."
        )
    if str(severity_level or "").upper() == "HIGH":
        return "Prioritize a prompt site review. " + action
    return action


def enrich_analysis_result(result: dict) -> dict:
    """Add transparent report fields without altering detector output or severity."""
    detections = list(result.get("detections") or [])
    severity = result.get("severity") or {}
    ratio = float(severity.get("damage_area_ratio") or 0.0)
    result["damage_count"] = len(detections)
    result["damage_types"] = sorted(
        {str(item["damage_type"]) for item in detections}
    )
    result["estimated_damage_percentage"] = round(ratio * 100.0, 2)
    result["damage_estimation_method"] = (
        "sum of detected bounding-box areas divided by full image area; "
        "approximate, not a pavement-condition measurement"
        if detections
        else "no supported detections"
    )
    result["recommended_action"] = recommended_maintenance_action(
        detections, severity.get("level")
    )
    # The Flutter result view draws boxes over the local image. The public
    # analyze endpoint does not persist uploads, so it cannot truthfully return
    # a hosted annotated image URL.
    result["annotated_image_url"] = None
    return result


def _box_area(box: dict) -> float:
    return max(0.0, float(box.get("x2") or 0) - float(box.get("x1") or 0)) * max(
        0.0, float(box.get("y2") or 0) - float(box.get("y1") or 0)
    )
