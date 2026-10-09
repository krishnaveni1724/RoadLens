from pathlib import Path

from fastapi.testclient import TestClient

from backend import server
from backend.errors import AnalysisError


client = TestClient(server.app)
FIXTURES = Path(__file__).resolve().parents[2] / "ai_test_images"


def test_health_exposes_real_model_details():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_loaded"] is True
    assert body["model"]["models"][0]["input"]["shape"] == [1, 3, 640, 640]
    assert body["model"]["models"][0]["output"]["shape"] == [1, 9, 8400]
    assert body["model"]["models"][1]["output"]["shape"] == [1, 5, 8400]


def test_public_static_mount_does_not_expose_backend_or_models():
    response = client.get("/backend/models/road_damage.onnx")
    assert response.status_code == 404


def test_invalid_upload_has_stable_error_contract():
    response = client.post("/api/analyze", files={"file": ("bad.jpg", b"not-an-image", "image/jpeg")})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "IMAGE_DECODE_FAILED"


def test_clear_pothole_returns_real_detection_contract():
    data = (FIXTURES / "known_pothole_01.jpg").read_bytes()
    response = client.post("/api/analyze", files={"file": ("known_pothole_01.jpg", data, "image/jpeg")})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["detected"] is True
    assert "debug" not in body
    assert any(item["damage_type"] == "Pothole" for item in body["detections"])
    assert body["image"] == {"width": 1448, "height": 1086, "filename": "known_pothole_01.jpg"}
    assert body["damage_count"] == len(body["detections"])
    assert body["damage_types"] == ["Pothole"]
    assert body["estimated_damage_percentage"] > 0
    assert "bounding-box" in body["damage_estimation_method"]
    assert "asphalt patch" in body["recommended_action"]
    assert body["annotated_image_url"] is None


def test_clean_road_returns_valid_no_detection_contract():
    data = (FIXTURES / "clean_road_01.jpg").read_bytes()
    response = client.post("/api/analyze", files={"file": ("clean_road_01.jpg", data, "image/jpeg")})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["status"] == "no_detection"
    assert body["detected"] is False
    assert body["detections"] == []
    assert body["message"] == "No supported road damage detected"
    assert body["damage_count"] == 0
    assert body["estimated_damage_percentage"] == 0
    assert body["recommended_action"] is None


def test_same_image_produces_deterministic_model_result():
    data = (FIXTURES / "known_pothole_01.jpg").read_bytes()
    first = client.post(
        "/api/analyze",
        files={"file": ("repeat.jpg", data, "image/jpeg")},
    )
    second = client.post(
        "/api/analyze",
        files={"file": ("repeat.jpg", data, "image/jpeg")},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["detected"] is True
    assert first.json()["detections"] == second.json()["detections"]
    assert first.json()["severity"] == second.json()["severity"]


def test_mobile_metadata_is_validated_and_echoed_with_real_analysis():
    data = (FIXTURES / "known_pothole_01.jpg").read_bytes()
    response = client.post(
        "/api/analyze",
        files={"file": ("capture.jpg", data, "image/jpeg")},
        data={
            "latitude": "15.3647",
            "longitude": "75.1240",
            "gps_accuracy": "8.2",
            "captured_at": "2026-08-24T20:35:00+05:30",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["detected"] is True
    assert body["inspection_metadata"] == {
        "latitude": 15.3647,
        "longitude": 75.124,
        "gps_accuracy": 8.2,
        "captured_at": "2026-08-24T20:35:00+05:30",
    }


def test_mobile_metadata_rejects_missing_fields_and_naive_timestamp():
    data = (FIXTURES / "clean_road_01.jpg").read_bytes()
    incomplete = client.post(
        "/api/analyze",
        files={"file": ("capture.jpg", data, "image/jpeg")},
        data={"latitude": "15.3647"},
    )
    assert incomplete.status_code == 422

    naive = client.post(
        "/api/analyze",
        files={"file": ("capture.jpg", data, "image/jpeg")},
        data={
            "latitude": "15.3647",
            "longitude": "75.1240",
            "gps_accuracy": "8.2",
            "captured_at": "2026-08-24T20:35:00",
        },
    )
    assert naive.status_code == 422


def test_inference_failure_has_server_error_contract(monkeypatch):
    class BrokenModel:
        def analyze_bytes(self, _data, _filename):
            raise AnalysisError("INFERENCE_FAILED", "The model could not analyze this image.")

    monkeypatch.setattr(server, "get_model", lambda: BrokenModel())
    response = client.post("/api/analyze", files={"file": ("road.jpg", (FIXTURES / "known_pothole_01.jpg").read_bytes(), "image/jpeg")})
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INFERENCE_FAILED"
