from backend.severity import calculate_severity


def detection(x1, y1, x2, y2):
    return {"bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}}


def test_severity_is_deterministic_and_area_based():
    low = calculate_severity([detection(0, 0, 100, 100)], 1000, 1000)
    medium = calculate_severity([detection(0, 0, 250, 250)], 1000, 1000)
    high = calculate_severity([detection(0, 0, 500, 500)], 1000, 1000)
    assert low.level == "LOW"
    assert medium.level == "MEDIUM"
    assert high.level == "HIGH"
    assert calculate_severity([], 1000, 1000) is None
