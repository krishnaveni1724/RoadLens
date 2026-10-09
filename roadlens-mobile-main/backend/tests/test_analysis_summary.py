from backend.analysis_summary import enrich_analysis_result


def test_analysis_summary_uses_real_boxes_and_supported_class():
    result = enrich_analysis_result(
        {
            "detections": [
                {
                    "damage_type": "Pothole",
                    "confidence": 0.91,
                    "bbox": {"x1": 10, "y1": 10, "x2": 110, "y2": 110},
                }
            ],
            "severity": {"level": "HIGH", "damage_area_ratio": 0.1},
        }
    )

    assert result["damage_count"] == 1
    assert result["damage_types"] == ["Pothole"]
    assert result["estimated_damage_percentage"] == 10.0
    assert "asphalt patch" in result["recommended_action"]
    assert "approximate" in result["damage_estimation_method"]
    assert result["annotated_image_url"] is None


def test_analysis_summary_does_not_invent_damage_for_clean_road():
    result = enrich_analysis_result({"detections": [], "severity": None})

    assert result["damage_count"] == 0
    assert result["damage_types"] == []
    assert result["estimated_damage_percentage"] == 0.0
    assert result["recommended_action"] is None
