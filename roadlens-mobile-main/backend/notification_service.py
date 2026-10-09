from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from uuid import uuid4

from firebase_admin import messaging


logger = logging.getLogger("roadlens.notifications")

NOTIFICATION_TYPES = frozenset(
    {
        "COMPLAINT_ASSIGNED",
        "COMPLAINT_ACKNOWLEDGED",
        "COMPLAINT_IN_PROGRESS",
        "COMPLAINT_RESOLVED",
        "COMPLAINT_CLOSED",
        "COMPLAINT_REJECTED",
        "COMPLAINT_REASSIGNED",
        "REPAIR_EVIDENCE_ADDED",
    }
)

STATUS_NOTIFICATION_CONTENT = {
    "ACKNOWLEDGED": (
        "COMPLAINT_ACKNOWLEDGED",
        "Complaint Acknowledged",
        "Your complaint {complaint_id} has been acknowledged by the assigned RoadLens Demo Authority.",
    ),
    "IN_PROGRESS": (
        "COMPLAINT_IN_PROGRESS",
        "Repair Work Started",
        "Your complaint {complaint_id} is now in progress.",
    ),
    "RESOLVED": (
        "COMPLAINT_RESOLVED",
        "Complaint Resolved",
        "Your reported road-damage issue {complaint_id} has been marked as resolved.",
    ),
    "CLOSED": (
        "COMPLAINT_CLOSED",
        "Complaint Closed",
        "Complaint {complaint_id} has been closed.",
    ),
    "REJECTED": (
        "COMPLAINT_REJECTED",
        "Complaint Rejected",
        "Your complaint {complaint_id} was rejected. Open the complaint to view the reason.",
    ),
}


class NotificationNotFound(Exception):
    pass


class InvalidDeviceToken(Exception):
    pass


class NotificationStore:
    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    recipient_user_id TEXT NOT NULL,
                    recipient_role TEXT NOT NULL CHECK (
                        recipient_role IN ('USER', 'AUTHORITY')
                    ),
                    complaint_id TEXT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    event_key TEXT NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS device_tokens (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    fcm_token TEXT NOT NULL UNIQUE,
                    platform TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, device_id)
                );

                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id TEXT PRIMARY KEY,
                    push_enabled INTEGER NOT NULL DEFAULT 1,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_notifications_recipient
                    ON notifications(recipient_user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_notifications_unread
                    ON notifications(recipient_user_id, is_read);
                CREATE INDEX IF NOT EXISTS idx_devices_user
                    ON device_tokens(user_id, is_active);
                """
            )

    def schema_tables(self) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        return {row["name"] for row in rows}

    def create(
        self,
        *,
        recipient_user_id: str,
        recipient_role: str,
        complaint_id: str | None,
        notification_type: str,
        title: str,
        message: str,
        metadata: dict,
        event_key: str,
    ) -> tuple[dict, bool]:
        if notification_type not in NOTIFICATION_TYPES:
            raise ValueError("Unknown notification type.")
        now = _now()
        notification_id = str(uuid4())
        with self._connect() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO notifications (
                        id, recipient_user_id, recipient_role, complaint_id,
                        type, title, message, is_read, created_at,
                        metadata_json, event_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                    """,
                    (
                        notification_id,
                        recipient_user_id,
                        recipient_role,
                        complaint_id,
                        notification_type,
                        title,
                        message,
                        now,
                        json.dumps(metadata, separators=(",", ":")),
                        event_key,
                    ),
                )
                created = True
            except sqlite3.IntegrityError:
                created = False
            row = connection.execute(
                "SELECT * FROM notifications WHERE event_key = ?", (event_key,)
            ).fetchone()
        return _notification_dict(row), created

    def list_for(self, user_id: str) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM notifications
                WHERE recipient_user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [_notification_dict(row) for row in rows]

    def unread_count(self, user_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS total FROM notifications
                WHERE recipient_user_id = ? AND is_read = 0
                """,
                (user_id,),
            ).fetchone()
        return row["total"]

    def mark_read(self, notification_id: str, user_id: str) -> dict:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM notifications WHERE id = ?", (notification_id,)
            ).fetchone()
            if row is None:
                raise NotificationNotFound("Notification was not found.")
            if row["recipient_user_id"] != user_id:
                raise PermissionError("This notification belongs to another account.")
            connection.execute(
                "UPDATE notifications SET is_read = 1 WHERE id = ?",
                (notification_id,),
            )
            updated = connection.execute(
                "SELECT * FROM notifications WHERE id = ?", (notification_id,)
            ).fetchone()
        return _notification_dict(updated)

    def mark_all_read(self, user_id: str) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE notifications SET is_read = 1
                WHERE recipient_user_id = ? AND is_read = 0
                """,
                (user_id,),
            )
        return cursor.rowcount

    def register_device(
        self,
        *,
        user_id: str,
        fcm_token: str,
        platform: str,
        device_id: str,
    ) -> dict:
        token = fcm_token.strip()
        if not token:
            raise ValueError("FCM token is required.")
        now = _now()
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id, created_at FROM device_tokens WHERE user_id = ? AND device_id = ?",
                (user_id, device_id),
            ).fetchone()
            device_token_id = existing["id"] if existing else str(uuid4())
            created_at = existing["created_at"] if existing else now
            connection.execute(
                "DELETE FROM device_tokens WHERE fcm_token = ? AND id != ?",
                (token, device_token_id),
            )
            connection.execute(
                """
                INSERT INTO device_tokens (
                    id, user_id, fcm_token, platform, device_id,
                    is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(user_id, device_id) DO UPDATE SET
                    fcm_token = excluded.fcm_token,
                    platform = excluded.platform,
                    is_active = 1,
                    updated_at = excluded.updated_at
                """,
                (
                    device_token_id,
                    user_id,
                    token,
                    platform.strip().lower(),
                    device_id.strip(),
                    created_at,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM device_tokens WHERE id = ?", (device_token_id,)
            ).fetchone()
        return _device_dict(row)

    def deactivate_device(self, device_id: str, user_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE device_tokens SET is_active = 0, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (_now(), device_id, user_id),
            )
        return cursor.rowcount > 0

    def deactivate_token(self, token: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE device_tokens SET is_active = 0, updated_at = ? WHERE fcm_token = ?",
                (_now(), token),
            )

    def active_tokens(self, user_id: str) -> list[str]:
        if not self.push_enabled(user_id):
            return []
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT fcm_token FROM device_tokens
                WHERE user_id = ? AND is_active = 1
                """,
                (user_id,),
            ).fetchall()
        return [row["fcm_token"] for row in rows]

    def set_push_enabled(self, user_id: str, enabled: bool) -> bool:
        now = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO notification_preferences(user_id, push_enabled, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    push_enabled = excluded.push_enabled,
                    updated_at = excluded.updated_at
                """,
                (user_id, 1 if enabled else 0, now),
            )
        return enabled

    def push_enabled(self, user_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT push_enabled FROM notification_preferences WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return True if row is None else bool(row["push_enabled"])


@dataclass(frozen=True)
class FirebasePushSender:
    app_provider: Callable

    def send(self, token: str, title: str, message: str, data: dict) -> None:
        try:
            messaging.send(
                messaging.Message(
                    token=token,
                    notification=messaging.Notification(title=title, body=message),
                    data={key: str(value) for key, value in data.items() if value is not None},
                    android=messaging.AndroidConfig(
                        priority="high",
                    ),
                ),
                app=self.app_provider(),
            )
        except Exception as exc:
            if exc.__class__.__name__ in {
                "UnregisteredError",
                "InvalidArgumentError",
                "SenderIdMismatchError",
            }:
                raise InvalidDeviceToken(str(exc)) from exc
            raise


class NotificationService:
    def __init__(self, store: NotificationStore, push_sender=None):
        self.store = store
        self.push_sender = push_sender

    def create_notification(
        self,
        *,
        recipient_user_id: str,
        recipient_role: str,
        complaint: dict,
        notification_type: str,
        title: str,
        message: str,
        event_key: str,
        force_push: bool = False,
    ) -> dict:
        metadata = {
            "complaint_id": complaint["id"],
            "complaint_public_id": complaint["complaint_id"],
            "damage_type": complaint["damage_type"],
            "severity": complaint["severity"],
            "location": complaint.get("location_name"),
            "status": complaint["status"],
            "recipient_role": recipient_role,
        }
        notification, created = self.store.create(
            recipient_user_id=recipient_user_id,
            recipient_role=recipient_role,
            complaint_id=complaint["id"],
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=metadata,
            event_key=event_key,
        )
        push_status = (
            self._attempt_push(recipient_user_id, notification)
            if created or force_push
            else "NOT_ATTEMPTED"
        )
        notification["delivery_status"] = "SENT"
        notification["push_status"] = push_status
        return notification

    def notify_complaint_assigned(
        self,
        complaint: dict,
        *,
        reassigned: bool = False,
        force_push: bool = False,
    ) -> dict | None:
        authority_id = complaint.get("authority_id")
        if not authority_id:
            return None
        notification_type = (
            "COMPLAINT_REASSIGNED" if reassigned else "COMPLAINT_ASSIGNED"
        )
        title = (
            "Road Damage Complaint Reassigned"
            if reassigned
            else "New Road Damage Complaint"
        )
        severity = str(complaint["severity"]).lower()
        affected = float(complaint.get("estimated_damage_percentage") or 0.0)
        location = complaint.get("location_name") or "GPS coordinates in the report"
        message = (
            f"{complaint['complaint_id']} has been reassigned to your RoadLens demo area. "
            f"Damage: {complaint['damage_type']}; severity: {severity}; "
            f"estimated affected area: {affected:.2f}%; location: {location}."
            if reassigned
            else f"New road damage report {complaint['complaint_id']}. "
            f"Damage: {complaint['damage_type']}; severity: {severity}; "
            f"estimated affected area: {affected:.2f}%; location: {location}. "
            "Please review it in the authority dashboard."
        )
        return self.create_notification(
            recipient_user_id=authority_id,
            recipient_role="AUTHORITY",
            complaint=complaint,
            notification_type=notification_type,
            title=title,
            message=message,
            event_key=(
                f"complaint:{complaint['id']}:assignment:"
                f"{authority_id}:{complaint['updated_at']}"
            ),
            force_push=force_push,
        )

    def notify_status_changed(self, complaint: dict) -> dict | None:
        content = STATUS_NOTIFICATION_CONTENT.get(complaint["status"])
        if content is None:
            return None
        notification_type, title, template = content
        return self.create_notification(
            recipient_user_id=complaint["user_id"],
            recipient_role="USER",
            complaint=complaint,
            notification_type=notification_type,
            title=title,
            message=template.format(complaint_id=complaint["complaint_id"]),
            event_key=f"complaint:{complaint['id']}:status:{complaint['status']}",
        )

    def notify_user_reassigned(self, complaint: dict) -> dict:
        return self.create_notification(
            recipient_user_id=complaint["user_id"],
            recipient_role="USER",
            complaint=complaint,
            notification_type="COMPLAINT_REASSIGNED",
            title="Demo Authority Assignment Updated",
            message=(
                f"Complaint {complaint['complaint_id']} was assigned to a RoadLens Demo Authority."
            ),
            event_key=(
                f"complaint:{complaint['id']}:user-assignment:"
                f"{complaint['authority_id']}:{complaint['updated_at']}"
            ),
        )

    def notify_repair_evidence_added(
        self,
        complaint: dict,
        repair_update: dict,
    ) -> dict:
        return self.create_notification(
            recipient_user_id=complaint["user_id"],
            recipient_role="USER",
            complaint=complaint,
            notification_type="REPAIR_EVIDENCE_ADDED",
            title="Repair Evidence Added",
            message=(
                f"A repair update was added to complaint {complaint['complaint_id']}."
            ),
            event_key=(
                f"complaint:{complaint['id']}:repair-evidence:"
                f"{repair_update['id']}"
            ),
        )

    def _attempt_push(self, recipient_user_id: str, notification: dict) -> str:
        if self.push_sender is None:
            return "NOT_CONFIGURED"
        if not self.store.push_enabled(recipient_user_id):
            return "DISABLED"
        tokens = self.store.active_tokens(recipient_user_id)
        if not tokens:
            return "NOT_REGISTERED"
        sent = 0
        for token in tokens:
            try:
                self.push_sender.send(
                    token,
                    notification["title"],
                    notification["message"],
                    {
                        **notification["metadata"],
                        "notification_id": notification["id"],
                    },
                )
                sent += 1
            except InvalidDeviceToken:
                self.store.deactivate_token(token)
                logger.warning("Deactivated an invalid FCM token.")
            except Exception:
                logger.exception(
                    "FCM delivery failed; the in-app notification remains stored."
                )
        return "SENT" if sent else "FAILED"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _notification_dict(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["is_read"] = bool(result["is_read"])
    result["metadata"] = json.loads(result.pop("metadata_json"))
    result.pop("event_key", None)
    return result


def _device_dict(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["is_active"] = bool(result["is_active"])
    result.pop("fcm_token", None)
    return result
