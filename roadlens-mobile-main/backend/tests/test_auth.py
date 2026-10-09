from fastapi.testclient import TestClient

from backend import server
from backend.auth import AuthenticationError, require_role
from backend.complaint_store import ComplaintStore
from backend.user_store import UserStore


client = TestClient(server.app)


class FakeVerifier:
    def __init__(self):
        self.created_authorities = []

    def verify(self, token: str) -> dict:
        if token == "invalid":
            raise AuthenticationError("Firebase ID token is invalid or expired.")
        return {
            "uid": token,
            "name": f"Demo {token}",
            "email": f"{token}@example.test",
        }

    def create_authority(self, *, name: str, email: str, password: str) -> str:
        uid = f"created-authority-{len(self.created_authorities) + 1}"
        self.created_authorities.append((uid, name, email, password))
        return uid

    def update_authority(self, uid: str, *, name: str) -> None:
        return None


def configure_auth(monkeypatch, tmp_path):
    store = UserStore(
        tmp_path / "auth.db",
        admin_uids=frozenset({"admin-uid"}),
        authority_uids=frozenset({"authority-uid"}),
    )
    monkeypatch.setattr(server, "get_token_verifier", lambda: FakeVerifier())
    monkeypatch.setattr(server, "get_user_store", lambda: store)
    monkeypatch.setattr(
        server,
        "get_complaint_store",
        lambda: ComplaintStore(tmp_path / "auth.db"),
    )
    return store


def test_auth_session_requires_a_verified_bearer_token(monkeypatch, tmp_path):
    configure_auth(monkeypatch, tmp_path)
    missing = client.post("/api/auth/session")
    invalid = client.post(
        "/api/auth/session", headers={"Authorization": "Bearer invalid"}
    )
    assert missing.status_code == 401
    assert invalid.status_code == 401


def test_new_identity_is_registered_as_user(monkeypatch, tmp_path):
    configure_auth(monkeypatch, tmp_path)
    response = client.post(
        "/api/auth/session", headers={"Authorization": "Bearer new-user"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "USER"
    assert response.json()["user"]["uid"] == "new-user"


def test_server_seed_controls_privileged_roles(monkeypatch, tmp_path):
    configure_auth(monkeypatch, tmp_path)
    admin = client.post(
        "/api/auth/session", headers={"Authorization": "Bearer admin-uid"}
    )
    authority = client.post(
        "/api/auth/session", headers={"Authorization": "Bearer authority-uid"}
    )
    assert admin.json()["user"]["role"] == "ADMIN"
    assert authority.json()["user"]["role"] == "AUTHORITY"


def test_existing_user_cannot_self_promote(monkeypatch, tmp_path):
    store = configure_auth(monkeypatch, tmp_path)
    first = store.resolve_user({"uid": "ordinary-user", "role": "ADMIN"})
    second = store.resolve_user({"uid": "ordinary-user", "role": "AUTHORITY"})
    assert first.role == "USER"
    assert second.role == "USER"


def test_role_guard_rejects_wrong_role():
    require_role("ADMIN", "ADMIN")
    try:
        require_role("USER", "ADMIN", "AUTHORITY")
    except PermissionError:
        pass
    else:
        raise AssertionError("USER unexpectedly passed a privileged role guard")


def test_dashboard_routes_enforce_the_authenticated_server_role(monkeypatch, tmp_path):
    configure_auth(monkeypatch, tmp_path)
    user_admin_attempt = client.get(
        "/api/dashboard/admin", headers={"Authorization": "Bearer ordinary-user"}
    )
    authority_admin_attempt = client.get(
        "/api/dashboard/admin", headers={"Authorization": "Bearer authority-uid"}
    )
    admin_dashboard = client.get(
        "/api/dashboard/admin", headers={"Authorization": "Bearer admin-uid"}
    )
    authority_dashboard = client.get(
        "/api/dashboard/authority",
        headers={"Authorization": "Bearer authority-uid"},
    )
    admin_user_attempt = client.get(
        "/api/dashboard/user", headers={"Authorization": "Bearer admin-uid"}
    )

    assert user_admin_attempt.status_code == 403
    assert authority_admin_attempt.status_code == 403
    assert admin_dashboard.status_code == 200
    assert authority_dashboard.status_code == 200
    assert admin_user_attempt.status_code == 403


def test_admin_can_create_and_update_demo_authority(monkeypatch, tmp_path):
    configure_auth(monkeypatch, tmp_path)
    payload = {
        "name": "Demo Road Authority",
        "email": "authority@example.test",
        "temporary_password": "temporary-pass-123",
        "assigned_area": "Demo Ward 7",
    }
    denied = client.post(
        "/api/admin/authorities",
        json=payload,
        headers={"Authorization": "Bearer ordinary-user"},
    )
    created = client.post(
        "/api/admin/authorities",
        json=payload,
        headers={"Authorization": "Bearer admin-uid"},
    )
    authority = created.json()["authority"]
    updated = client.put(
        f"/api/admin/authorities/{authority['uid']}",
        json={"name": "Updated Demo Authority", "assigned_area": "Demo Ward 8"},
        headers={"Authorization": "Bearer admin-uid"},
    )
    listed = client.get(
        "/api/admin/authorities", headers={"Authorization": "Bearer admin-uid"}
    )

    assert denied.status_code == 403
    assert created.status_code == 201
    assert authority["role"] == "AUTHORITY"
    assert authority["assigned_area"] == "Demo Ward 7"
    assert updated.status_code == 200
    assert updated.json()["authority"]["assigned_area"] == "Demo Ward 8"
    assert len(listed.json()["authorities"]) == 1
