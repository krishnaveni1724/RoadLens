from pathlib import Path

from fastapi.testclient import TestClient

from backend import config, server
from backend.auth import AuthenticationError
from backend.complaint_store import ComplaintStore
from backend.notification_service import NotificationService, NotificationStore
from backend.user_store import UserStore


client = TestClient(server.app)
FIXTURES = Path(__file__).resolve().parents[2] / "ai_test_images"


class FakeVerifier:
    def verify(self, token: str) -> dict:
        if token == "invalid":
            raise AuthenticationError("Invalid token")
        return {
            "uid": token,
            "name": f"Demo {token}",
            "email": f"{token}@example.test",
        }


class FakeRoadModel:
    def analyze_bytes(self, _data: bytes, _filename: str) -> dict:
        return {
            "success": True,
            "detected": True,
            "detections": [
                {
                    "damage_type": "Pothole",
                    "confidence": 0.91,
                    "bbox": {"x1": 10, "y1": 20, "x2": 80, "y2": 95},
                }
            ],
            "severity": {"level": "HIGH", "damage_area_ratio": 0.18},
        }


def authorization(uid: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {uid}"}


def configure_phase4(monkeypatch, tmp_path: Path):
    database = tmp_path / "roadlens.db"
    users = UserStore(
        database,
        admin_uids=frozenset({"admin-uid"}),
        authority_uids=frozenset({"authority-1", "authority-2"}),
    )
    complaints = ComplaintStore(database)
    notification_store = NotificationStore(database)
    monkeypatch.setattr(server, "get_token_verifier", lambda: FakeVerifier())
    monkeypatch.setattr(server, "get_user_store", lambda: users)
    monkeypatch.setattr(server, "get_complaint_store", lambda: complaints)
    monkeypatch.setattr(server, "get_notification_store", lambda: notification_store)
    monkeypatch.setattr(
        server,
        "get_notification_service",
        lambda: NotificationService(notification_store),
    )
    monkeypatch.setattr(server, "get_model", lambda: FakeRoadModel())
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "media")
    for uid in ("user-1", "admin-uid", "authority-1", "authority-2"):
        response = client.post("/api/auth/session", headers=authorization(uid))
        assert response.status_code == 200
    return users, complaints


def complaint_payload(
    inspection_id: str,
    *,
    location_name: str = "Demo Ward 10, RoadLens College City",
):
    return {
        "files": {
            "file": (
                "road.jpg",
                (FIXTURES / "known_pothole_01.jpg").read_bytes(),
                "image/jpeg",
            )
        },
        "data": {
            "inspection_id": inspection_id,
            "latitude": "15.3647",
            "longitude": "75.1240",
            "gps_accuracy": "7.4",
            "captured_at": "2026-08-26T09:30:00+05:30",
            "location_name": location_name,
        },
        "headers": authorization("user-1"),
    }


def create_routed_complaint(monkeypatch, tmp_path):
    _users, complaints = configure_phase4(monkeypatch, tmp_path)
    complaints.configure_authority_area(
        "authority-1",
        area_name="Demo Ward 10",
        city="RoadLens College City",
    )
    response = client.post(
        "/api/v1/complaints",
        **complaint_payload("inspection-1"),
    )
    assert response.status_code == 200
    return response.json()["complaint"], complaints


def test_schema_migration_creates_only_missing_complaint_tables(monkeypatch, tmp_path):
    _users, complaints = configure_phase4(monkeypatch, tmp_path)
    assert {
        "users",
        "complaints",
        "complaint_status_history",
        "authority_areas",
        "repair_updates",
    }.issubset(complaints.schema_tables())


def test_create_generates_unique_public_id_routes_and_prevents_duplicate(
    monkeypatch, tmp_path
):
    complaint, _store = create_routed_complaint(monkeypatch, tmp_path)
    duplicate = client.post(
        "/api/v1/complaints",
        **complaint_payload("inspection-1"),
    )

    assert complaint["id"] != complaint["complaint_id"]
    assert complaint["complaint_id"].startswith("RDL-2026-")
    assert complaint["inspection_id"] == "inspection-1"
    assert complaint["authority_id"] == "authority-1"
    assert complaint["assignment_status"] == "ASSIGNED"
    assert complaint["damage_type"] == "Pothole"
    assert complaint["confidence"] == 0.91
    assert complaint["damage_count"] == 1
    assert complaint["estimated_damage_percentage"] == 18.0
    assert "asphalt patch" in complaint["recommended_action"]
    assert complaint["authority_notification_status"] == "SENT"
    assert complaint["authority_push_status"] == "NOT_CONFIGURED"
    assert complaint["annotated_image_url"].endswith("/annotated.jpg")
    assert complaint["status"] == "SUBMITTED"
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True
    assert duplicate.json()["complaint"]["id"] == complaint["id"]


def test_user_dashboard_summary_refreshes_after_complaint_creation(
    monkeypatch, tmp_path
):
    _users, complaints = configure_phase4(monkeypatch, tmp_path)
    complaints.configure_authority_area(
        "authority-1",
        area_name="Demo Ward 10",
        city="RoadLens College City",
    )

    before = client.get(
        "/api/dashboard/user", headers=authorization("user-1")
    )
    created = client.post(
        "/api/v1/complaints", **complaint_payload("dashboard-inspection-1")
    )
    after = client.get(
        "/api/dashboard/user", headers=authorization("user-1")
    )
    mine = client.get(
        "/api/v1/complaints/me", headers=authorization("user-1")
    )

    assert before.status_code == 200
    assert before.json()["complaints"] == {
        "total": 0,
        "pending": 0,
        "in_progress": 0,
        "resolved": 0,
        "rejected": 0,
    }
    assert created.status_code == 200
    assert after.json()["complaints"] == {
        "total": 1,
        "pending": 1,
        "in_progress": 0,
        "resolved": 0,
        "rejected": 0,
    }
    assert len(mine.json()["complaints"]) == 1
    assert mine.json()["complaints"][0]["user_id"] == "user-1"


def test_unmatched_and_ambiguous_areas_remain_unassigned_for_admin(
    monkeypatch, tmp_path
):
    _users, complaints = configure_phase4(monkeypatch, tmp_path)
    complaints.configure_authority_area(
        "authority-1", area_name="Shared Demo Campus"
    )
    complaints.configure_authority_area(
        "authority-2", area_name="Shared Demo Campus"
    )
    ambiguous = client.post(
        "/api/v1/complaints",
        **complaint_payload(
            "inspection-ambiguous", location_name="Shared Demo Campus"
        ),
    ).json()["complaint"]
    unmatched = client.post(
        "/api/v1/complaints",
        **complaint_payload("inspection-unmatched", location_name="Unknown Zone"),
    ).json()["complaint"]

    assert ambiguous["assignment_status"] == "UNASSIGNED"
    assert ambiguous["authority_id"] is None
    assert unmatched["assignment_status"] == "UNASSIGNED"

    assigned = client.post(
        f"/api/v1/admin/complaints/{unmatched['id']}/assign",
        json={"authority_id": "authority-2"},
        headers=authorization("admin-uid"),
    )
    assert assigned.status_code == 200
    assert assigned.json()["complaint"]["authority_id"] == "authority-2"


def test_authority_can_only_view_and_update_assigned_complaints(monkeypatch, tmp_path):
    complaint, _store = create_routed_complaint(monkeypatch, tmp_path)
    own_list = client.get(
        "/api/v1/authority/complaints", headers=authorization("authority-1")
    )
    other_list = client.get(
        "/api/v1/authority/complaints", headers=authorization("authority-2")
    )
    denied = client.get(
        f"/api/v1/complaints/{complaint['id']}",
        headers=authorization("authority-2"),
    )
    denied_update = client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=authorization("authority-2"),
    )

    assert [item["id"] for item in own_list.json()["complaints"]] == [
        complaint["id"]
    ]
    assert other_list.json()["complaints"] == []
    assert denied.status_code == 403
    assert denied_update.status_code == 403


def test_status_lifecycle_records_history_and_requires_repair_evidence(
    monkeypatch, tmp_path
):
    complaint, _store = create_routed_complaint(monkeypatch, tmp_path)
    path = f"/api/v1/complaints/{complaint['id']}"
    acknowledged = client.patch(
        f"{path}/status",
        json={"status": "ACKNOWLEDGED", "note": "Complaint reviewed."},
        headers=authorization("authority-1"),
    )
    started = client.patch(
        f"{path}/status",
        json={"status": "IN_PROGRESS", "note": "Repair team started work."},
        headers=authorization("authority-1"),
    )
    premature = client.patch(
        f"{path}/status",
        json={"status": "RESOLVED"},
        headers=authorization("authority-1"),
    )
    evidence = client.post(
        f"{path}/repair-evidence",
        files={
            "file": (
                "repair.jpg",
                (FIXTURES / "clean_road_01.jpg").read_bytes(),
                "image/jpeg",
            )
        },
        data={"note": "Road surface repaired."},
        headers=authorization("authority-1"),
    )
    resolved = client.patch(
        f"{path}/status",
        json={"status": "RESOLVED", "note": "Repair verified."},
        headers=authorization("authority-1"),
    )

    assert acknowledged.json()["complaint"]["status"] == "ACKNOWLEDGED"
    assert started.json()["complaint"]["status"] == "IN_PROGRESS"
    assert premature.status_code == 422
    assert evidence.status_code == 200
    detail = resolved.json()["complaint"]
    assert detail["status"] == "RESOLVED"
    assert [item["new_status"] for item in detail["history"]] == [
        "SUBMITTED",
        "ACKNOWLEDGED",
        "IN_PROGRESS",
        "RESOLVED",
    ]
    assert len(detail["repair_updates"]) == 1


def test_user_sees_own_timeline_but_cannot_change_status(monkeypatch, tmp_path):
    complaint, _store = create_routed_complaint(monkeypatch, tmp_path)
    mine = client.get("/api/v1/complaints/me", headers=authorization("user-1"))
    detail = client.get(
        f"/api/v1/complaints/{complaint['id']}",
        headers=authorization("user-1"),
    )
    denied = client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=authorization("user-1"),
    )

    assert mine.status_code == 200
    assert mine.json()["complaints"][0]["complaint_id"] == complaint["complaint_id"]
    assert detail.json()["complaint"]["history"][0]["new_status"] == "SUBMITTED"
    assert denied.status_code == 403


def test_admin_reassignment_transfers_authority_ownership(monkeypatch, tmp_path):
    complaint, _store = create_routed_complaint(monkeypatch, tmp_path)
    reassigned = client.post(
        f"/api/v1/admin/complaints/{complaint['id']}/assign",
        json={"authority_id": "authority-2"},
        headers=authorization("admin-uid"),
    )
    old_access = client.get(
        f"/api/v1/complaints/{complaint['id']}",
        headers=authorization("authority-1"),
    )
    new_access = client.get(
        f"/api/v1/complaints/{complaint['id']}",
        headers=authorization("authority-2"),
    )

    assert reassigned.status_code == 200
    assert reassigned.json()["complaint"]["authority_id"] == "authority-2"
    assert old_access.status_code == 403
    assert new_access.status_code == 200
