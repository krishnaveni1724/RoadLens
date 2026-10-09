from pathlib import Path

from fastapi.testclient import TestClient

from backend import config, server
from backend.complaint_store import ComplaintStore
from backend.notification_service import NotificationService, NotificationStore
from backend.user_store import UserStore


client = TestClient(server.app)
FIXTURES = Path(__file__).resolve().parents[2] / "ai_test_images"


class FakeVerifier:
    def verify(self, token: str) -> dict:
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
                    "confidence": 0.92,
                    "bbox": {"x1": 1, "y1": 2, "x2": 30, "y2": 40},
                }
            ],
            "severity": {"level": "HIGH", "damage_area_ratio": 0.18},
        }


class RecordingPushSender:
    def __init__(self, *, fail: bool = False):
        self.fail = fail
        self.sent = []

    def send(self, token: str, title: str, message: str, data: dict) -> None:
        self.sent.append((token, title, message, data))
        if self.fail:
            raise RuntimeError("Firebase unavailable")


def headers(uid: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {uid}"}


def configure(monkeypatch, tmp_path, *, push_fail: bool = False):
    database = tmp_path / "roadlens.db"
    users = UserStore(
        database,
        admin_uids=frozenset({"admin-uid"}),
        authority_uids=frozenset({"authority-a", "authority-b"}),
    )
    complaints = ComplaintStore(database)
    notifications = NotificationStore(database)
    sender = RecordingPushSender(fail=push_fail)
    service = NotificationService(notifications, sender)
    monkeypatch.setattr(server, "get_token_verifier", lambda: FakeVerifier())
    monkeypatch.setattr(server, "get_user_store", lambda: users)
    monkeypatch.setattr(server, "get_complaint_store", lambda: complaints)
    monkeypatch.setattr(server, "get_notification_store", lambda: notifications)
    monkeypatch.setattr(server, "get_notification_service", lambda: service)
    monkeypatch.setattr(server, "get_model", lambda: FakeRoadModel())
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "media")
    for uid in (
        "user-1",
        "user-2",
        "admin-uid",
        "authority-a",
        "authority-b",
    ):
        assert client.post("/api/auth/session", headers=headers(uid)).status_code == 200
    complaints.configure_authority_area(
        "authority-a", area_name="Demo Ward A", city="RoadLens Demo City"
    )
    return database, complaints, notifications, sender


def create_assigned_complaint():
    response = client.post(
        "/api/v1/complaints",
        files={
            "file": (
                "road.jpg",
                (FIXTURES / "known_pothole_01.jpg").read_bytes(),
                "image/jpeg",
            )
        },
        data={
            "inspection_id": "inspection-notification-1",
            "latitude": "15.3",
            "longitude": "75.1",
            "gps_accuracy": "5.0",
            "captured_at": "2026-08-26T10:00:00+05:30",
            "location_name": "Demo Ward A, RoadLens Demo City",
        },
        headers=headers("user-1"),
    )
    assert response.status_code == 200
    return response.json()["complaint"]


def register(uid: str, token: str, device_id: str = "device-1"):
    return client.post(
        "/api/v1/devices/register",
        json={
            "fcm_token": token,
            "platform": "android",
            "device_id": device_id,
        },
        headers=headers(uid),
    )


def test_assignment_notifies_only_the_assigned_authority_and_persists(
    monkeypatch, tmp_path
):
    database, _complaints, notifications, sender = configure(monkeypatch, tmp_path)
    assert register("authority-a", "authority-a-token").status_code == 200
    assert register("authority-b", "authority-b-token").status_code == 200

    complaint = create_assigned_complaint()
    authority_a = client.get("/api/v1/notifications", headers=headers("authority-a"))
    authority_b = client.get("/api/v1/notifications", headers=headers("authority-b"))

    assert complaint["authority_id"] == "authority-a"
    assert complaint["authority_notification_status"] == "SENT"
    assert complaint["authority_push_status"] == "SENT"
    assert len(authority_a.json()["notifications"]) == 1
    assert authority_a.json()["notifications"][0]["type"] == "COMPLAINT_ASSIGNED"
    assert authority_b.json()["notifications"] == []
    assert [item[0] for item in sender.sent] == ["authority-a-token"]
    assert len(NotificationStore(database).list_for("authority-a")) == 1
    assert "notifications" in notifications.schema_tables()
    assert "device_tokens" in notifications.schema_tables()


def test_failed_authority_push_keeps_report_and_can_be_retried(
    monkeypatch, tmp_path
):
    _database, _complaints, _notifications, sender = configure(
        monkeypatch, tmp_path, push_fail=True
    )
    register("authority-a", "failing-authority-token")

    complaint = create_assigned_complaint()
    detail = client.get(
        f"/api/v1/complaints/{complaint['id']}", headers=headers("user-1")
    )
    retry = client.post(
        f"/api/v1/complaints/{complaint['id']}/retry-authority-notification",
        headers=headers("user-1"),
    )
    authority_notifications = client.get(
        "/api/v1/notifications", headers=headers("authority-a")
    ).json()["notifications"]

    assert detail.status_code == 200
    assert detail.json()["complaint"]["status"] == "SUBMITTED"
    assert complaint["authority_notification_status"] == "SENT"
    assert complaint["authority_push_status"] == "FAILED"
    assert retry.status_code == 200
    assert retry.json()["complaint"]["authority_push_status"] == "FAILED"
    assert len(authority_notifications) == 1
    assert [item[0] for item in sender.sent] == [
        "failing-authority-token",
        "failing-authority-token",
    ]


def test_status_events_notify_user_once_with_real_complaint_data(
    monkeypatch, tmp_path
):
    _database, _complaints, _notifications, sender = configure(monkeypatch, tmp_path)
    register("user-1", "user-token")
    complaint = create_assigned_complaint()
    path = f"/api/v1/complaints/{complaint['id']}"

    acknowledged = client.patch(
        f"{path}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers("authority-a"),
    )
    duplicate = client.patch(
        f"{path}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers("authority-a"),
    )
    in_progress = client.patch(
        f"{path}/status",
        json={"status": "IN_PROGRESS"},
        headers=headers("authority-a"),
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
        headers=headers("authority-a"),
    )
    resolved = client.patch(
        f"{path}/status",
        json={"status": "RESOLVED"},
        headers=headers("authority-a"),
    )
    user_notifications = client.get(
        "/api/v1/notifications", headers=headers("user-1")
    ).json()["notifications"]

    assert acknowledged.status_code == 200
    assert duplicate.status_code == 422
    assert in_progress.status_code == 200
    assert evidence.status_code == 200
    assert resolved.status_code == 200
    assert {item["type"] for item in user_notifications} == {
        "COMPLAINT_ACKNOWLEDGED",
        "COMPLAINT_IN_PROGRESS",
        "REPAIR_EVIDENCE_ADDED",
        "COMPLAINT_RESOLVED",
    }
    assert all(
        item["metadata"]["complaint_public_id"] == complaint["complaint_id"]
        for item in user_notifications
    )
    assert len([item for item in sender.sent if item[0] == "user-token"]) == 4


def test_read_unread_mark_all_and_recipient_authorization(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path)
    complaint = create_assigned_complaint()
    client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers("authority-a"),
    )
    notification = client.get(
        "/api/v1/notifications", headers=headers("user-1")
    ).json()["notifications"][0]
    unread = client.get(
        "/api/v1/notifications/unread-count", headers=headers("user-1")
    )
    denied = client.patch(
        f"/api/v1/notifications/{notification['id']}/read",
        headers=headers("user-2"),
    )
    marked = client.patch(
        f"/api/v1/notifications/{notification['id']}/read",
        headers=headers("user-1"),
    )
    after = client.get(
        "/api/v1/notifications/unread-count", headers=headers("user-1")
    )
    all_read = client.post(
        "/api/v1/notifications/mark-all-read", headers=headers("user-1")
    )

    assert unread.json()["unread_count"] == 1
    assert denied.status_code == 403
    assert marked.json()["notification"]["is_read"] is True
    assert after.json()["unread_count"] == 0
    assert all_read.json()["unread_count"] == 0


def test_token_refresh_preferences_and_device_ownership(monkeypatch, tmp_path):
    _database, _complaints, notifications, _sender = configure(monkeypatch, tmp_path)
    first = register("user-1", "old-fcm-token", "phone-1").json()["device"]
    refreshed = register("user-1", "new-fcm-token", "phone-1").json()["device"]
    preference = client.patch(
        "/api/v1/notifications/preferences",
        json={"push_enabled": False},
        headers=headers("user-1"),
    )
    denied_delete = client.delete(
        f"/api/v1/devices/{refreshed['id']}", headers=headers("user-2")
    )
    deleted = client.delete(
        f"/api/v1/devices/{refreshed['id']}", headers=headers("user-1")
    )

    assert first["id"] == refreshed["id"]
    assert notifications.active_tokens("user-1") == []
    assert preference.json()["push_enabled"] is False
    assert denied_delete.status_code == 404
    assert deleted.status_code == 200


def test_push_failure_never_rolls_back_status_or_in_app_notification(
    monkeypatch, tmp_path
):
    configure(monkeypatch, tmp_path, push_fail=True)
    register("user-1", "failing-token")
    complaint = create_assigned_complaint()
    response = client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={"status": "ACKNOWLEDGED"},
        headers=headers("authority-a"),
    )
    detail = client.get(
        f"/api/v1/complaints/{complaint['id']}", headers=headers("user-1")
    )
    notification_items = client.get(
        "/api/v1/notifications", headers=headers("user-1")
    ).json()["notifications"]

    assert response.status_code == 200
    assert detail.json()["complaint"]["status"] == "ACKNOWLEDGED"
    assert notification_items[0]["type"] == "COMPLAINT_ACKNOWLEDGED"
