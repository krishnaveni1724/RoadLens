from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


COMPLAINT_STATUSES = frozenset(
    {
        "SUBMITTED",
        "ACKNOWLEDGED",
        "ASSIGNED",
        "IN_PROGRESS",
        "RESOLVED",
        "CLOSED",
        "REJECTED",
    }
)

AUTHORITY_TRANSITIONS = {
    "SUBMITTED": frozenset({"ACKNOWLEDGED", "REJECTED"}),
    "ACKNOWLEDGED": frozenset({"IN_PROGRESS", "REJECTED"}),
    "ASSIGNED": frozenset({"IN_PROGRESS", "REJECTED"}),
    "IN_PROGRESS": frozenset({"RESOLVED"}),
}

ADMIN_TRANSITIONS = {
    "RESOLVED": frozenset({"CLOSED"}),
}


class ComplaintStoreError(Exception):
    pass


class ComplaintNotFound(ComplaintStoreError):
    pass


class InvalidStatusTransition(ComplaintStoreError):
    pass


class RepairEvidenceRequired(ComplaintStoreError):
    pass


class ComplaintStore:
    """SQLite persistence for RoadLens college-project complaints."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS complaint_sequences (
                    year INTEGER PRIMARY KEY,
                    last_value INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS authority_areas (
                    id TEXT PRIMARY KEY,
                    authority_id TEXT NOT NULL,
                    area_name TEXT NOT NULL,
                    city TEXT,
                    district TEXT,
                    state TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(authority_id, area_name)
                );

                CREATE TABLE IF NOT EXISTS complaints (
                    id TEXT PRIMARY KEY,
                    complaint_id TEXT NOT NULL UNIQUE,
                    inspection_id TEXT NOT NULL UNIQUE,
                    user_id TEXT NOT NULL,
                    authority_id TEXT,
                    assignment_status TEXT NOT NULL
                        CHECK (assignment_status IN ('ASSIGNED', 'UNASSIGNED')),
                    road_image_url TEXT NOT NULL,
                    annotated_image_url TEXT,
                    detections_json TEXT NOT NULL,
                    damage_type TEXT NOT NULL,
                    damage_count INTEGER NOT NULL DEFAULT 0,
                    estimated_damage_percentage REAL NOT NULL DEFAULT 0,
                    damage_estimation_method TEXT,
                    recommended_action TEXT,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    gps_accuracy REAL NOT NULL,
                    location_name TEXT,
                    captured_at TEXT NOT NULL,
                    authority_notification_status TEXT NOT NULL DEFAULT 'PENDING',
                    authority_push_status TEXT NOT NULL DEFAULT 'PENDING',
                    status TEXT NOT NULL CHECK (
                        status IN (
                            'SUBMITTED', 'ACKNOWLEDGED', 'ASSIGNED',
                            'IN_PROGRESS', 'RESOLVED', 'CLOSED', 'REJECTED'
                        )
                    ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS complaint_status_history (
                    id TEXT PRIMARY KEY,
                    complaint_id TEXT NOT NULL,
                    old_status TEXT,
                    new_status TEXT NOT NULL,
                    changed_by TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(complaint_id) REFERENCES complaints(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS repair_updates (
                    id TEXT PRIMARY KEY,
                    complaint_id TEXT NOT NULL,
                    authority_id TEXT NOT NULL,
                    image_url TEXT NOT NULL,
                    note TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(complaint_id) REFERENCES complaints(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_complaints_user
                    ON complaints(user_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_complaints_authority
                    ON complaints(authority_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_history_complaint
                    ON complaint_status_history(complaint_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_repairs_complaint
                    ON repair_updates(complaint_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_authority_areas_active
                    ON authority_areas(is_active, authority_id);
                """
            )
            self._ensure_column(
                connection, "complaints", "damage_count", "INTEGER NOT NULL DEFAULT 0"
            )
            self._ensure_column(
                connection,
                "complaints",
                "estimated_damage_percentage",
                "REAL NOT NULL DEFAULT 0",
            )
            self._ensure_column(
                connection, "complaints", "damage_estimation_method", "TEXT"
            )
            self._ensure_column(
                connection, "complaints", "recommended_action", "TEXT"
            )
            self._ensure_column(
                connection,
                "complaints",
                "authority_notification_status",
                "TEXT NOT NULL DEFAULT 'PENDING'",
            )
            self._ensure_column(
                connection,
                "complaints",
                "authority_push_status",
                "TEXT NOT NULL DEFAULT 'PENDING'",
            )

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table: str,
        column: str,
        declaration: str,
    ) -> None:
        existing = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in existing:
            connection.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {declaration}"
            )

    def schema_tables(self) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        return {row["name"] for row in rows}

    def configure_authority_area(
        self,
        authority_id: str,
        *,
        area_name: str,
        city: str | None = None,
        district: str | None = None,
        state: str | None = None,
        is_active: bool = True,
    ) -> dict:
        now = _now()
        normalized_area = area_name.strip()
        if not normalized_area:
            raise ValueError("A demonstration area name is required.")
        with self._connect() as connection:
            connection.execute(
                "UPDATE authority_areas SET is_active = 0, updated_at = ? WHERE authority_id = ?",
                (now, authority_id),
            )
            existing = connection.execute(
                "SELECT id, created_at FROM authority_areas WHERE authority_id = ? AND area_name = ?",
                (authority_id, normalized_area),
            ).fetchone()
            area_id = existing["id"] if existing else str(uuid4())
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """
                INSERT INTO authority_areas (
                    id, authority_id, area_name, city, district, state,
                    is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(authority_id, area_name) DO UPDATE SET
                    city = excluded.city,
                    district = excluded.district,
                    state = excluded.state,
                    is_active = excluded.is_active,
                    updated_at = excluded.updated_at
                """,
                (
                    area_id,
                    authority_id,
                    normalized_area,
                    _optional_text(city),
                    _optional_text(district),
                    _optional_text(state),
                    1 if is_active else 0,
                    created_at,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM authority_areas WHERE id = ?", (area_id,)
            ).fetchone()
        return _area_dict(row)

    def authority_areas(self, authority_id: str | None = None) -> list[dict]:
        query = "SELECT * FROM authority_areas"
        parameters: tuple[str, ...] = ()
        if authority_id is not None:
            query += " WHERE authority_id = ?"
            parameters = (authority_id,)
        query += " ORDER BY area_name"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [_area_dict(row) for row in rows]

    def route_authority(self, location_name: str | None) -> str | None:
        location = (location_name or "").strip().casefold()
        if not location:
            return None
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT a.*
                FROM authority_areas AS a
                JOIN users AS u ON u.uid = a.authority_id
                WHERE a.is_active = 1
                  AND u.role = 'AUTHORITY'
                  AND COALESCE(u.is_active, 1) = 1
                """
            ).fetchall()
        matches: set[str] = set()
        for row in rows:
            configured = [
                row["area_name"],
                row["city"],
                row["district"],
                row["state"],
            ]
            if any(
                value and str(value).strip().casefold() in location
                for value in configured
            ):
                matches.add(row["authority_id"])
        return next(iter(matches)) if len(matches) == 1 else None

    def create_complaint(
        self,
        *,
        inspection_id: str,
        user_id: str,
        road_image_url: str,
        detections: list[dict],
        damage_type: str,
        damage_count: int,
        estimated_damage_percentage: float,
        damage_estimation_method: str | None,
        recommended_action: str | None,
        severity: str,
        confidence: float,
        latitude: float,
        longitude: float,
        gps_accuracy: float,
        location_name: str | None,
        captured_at: str,
        annotated_image_url: str | None = None,
    ) -> tuple[dict, bool]:
        authority_id = self.route_authority(location_name)
        now = _now()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM complaints WHERE inspection_id = ?",
                (inspection_id,),
            ).fetchone()
            if existing is not None:
                return self._detail(connection, existing), True

            year = datetime.now(timezone.utc).year
            sequence = connection.execute(
                "SELECT last_value FROM complaint_sequences WHERE year = ?",
                (year,),
            ).fetchone()
            next_value = (sequence["last_value"] if sequence else 0) + 1
            connection.execute(
                """
                INSERT INTO complaint_sequences(year, last_value) VALUES (?, ?)
                ON CONFLICT(year) DO UPDATE SET last_value = excluded.last_value
                """,
                (year, next_value),
            )
            internal_id = str(uuid4())
            public_id = f"RDL-{year}-{next_value:06d}"
            connection.execute(
                """
                INSERT INTO complaints (
                    id, complaint_id, inspection_id, user_id, authority_id,
                    assignment_status, road_image_url, annotated_image_url,
                    detections_json, damage_type, damage_count,
                    estimated_damage_percentage, damage_estimation_method,
                    recommended_action, severity, confidence,
                    latitude, longitude, gps_accuracy, location_name,
                    captured_at, authority_notification_status,
                    authority_push_status, status, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, 'SUBMITTED', ?, ?
                )
                """,
                (
                    internal_id,
                    public_id,
                    inspection_id,
                    user_id,
                    authority_id,
                    "ASSIGNED" if authority_id else "UNASSIGNED",
                    road_image_url,
                    annotated_image_url,
                    json.dumps(detections, separators=(",", ":")),
                    damage_type,
                    damage_count,
                    estimated_damage_percentage,
                    _optional_text(damage_estimation_method),
                    _optional_text(recommended_action),
                    severity,
                    confidence,
                    latitude,
                    longitude,
                    gps_accuracy,
                    _optional_text(location_name),
                    captured_at,
                    "PENDING" if authority_id else "NOT_ROUTED",
                    "PENDING" if authority_id else "NOT_ROUTED",
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO complaint_status_history (
                    id, complaint_id, old_status, new_status,
                    changed_by, note, created_at
                ) VALUES (?, ?, NULL, 'SUBMITTED', ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    internal_id,
                    user_id,
                    "Complaint submitted from a verified RoadLens inspection.",
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM complaints WHERE id = ?", (internal_id,)
            ).fetchone()
            return self._detail(connection, row), False

    def update_authority_notification_status(
        self,
        identifier: str,
        *,
        notification_status: str,
        push_status: str,
    ) -> dict:
        allowed_notification = {"PENDING", "SENT", "FAILED", "NOT_ROUTED"}
        allowed_push = {
            "PENDING",
            "SENT",
            "FAILED",
            "NOT_REGISTERED",
            "DISABLED",
            "NOT_CONFIGURED",
            "NOT_ROUTED",
        }
        normalized_notification = notification_status.strip().upper()
        normalized_push = push_status.strip().upper()
        if normalized_notification not in allowed_notification:
            raise ValueError("Unknown authority notification status.")
        if normalized_push not in allowed_push:
            raise ValueError("Unknown authority push status.")
        with self._connect() as connection:
            complaint = self._find(connection, identifier)
            if complaint is None:
                raise ComplaintNotFound("Complaint was not found.")
            connection.execute(
                """
                UPDATE complaints
                SET authority_notification_status = ?, authority_push_status = ?
                WHERE id = ?
                """,
                (normalized_notification, normalized_push, complaint["id"]),
            )
            updated = self._find(connection, complaint["id"])
            return self._detail(connection, updated)

    def get(self, identifier: str) -> dict | None:
        with self._connect() as connection:
            row = self._find(connection, identifier)
            return None if row is None else self._detail(connection, row)

    def get_by_inspection(self, inspection_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM complaints WHERE inspection_id = ?",
                (inspection_id,),
            ).fetchone()
            return None if row is None else self._detail(connection, row)

    def list_for_user(self, user_id: str) -> list[dict]:
        return self._list("WHERE c.user_id = ?", (user_id,))

    def list_for_authority(self, authority_id: str) -> list[dict]:
        return self._list("WHERE c.authority_id = ?", (authority_id,))

    def list_all(self) -> list[dict]:
        return self._list("", ())

    def _list(self, clause: str, parameters: tuple) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT c.*, u.name AS authority_name
                FROM complaints AS c
                LEFT JOIN users AS u ON u.uid = c.authority_id
                {clause}
                ORDER BY c.created_at DESC
                """,
                parameters,
            ).fetchall()
        return [_complaint_dict(row) for row in rows]

    def counts(self, *, user_id: str | None = None, authority_id: str | None = None) -> dict:
        where: list[str] = []
        parameters: list[str] = []
        if user_id is not None:
            where.append("user_id = ?")
            parameters.append(user_id)
        if authority_id is not None:
            where.append("authority_id = ?")
            parameters.append(authority_id)
        clause = f"WHERE {' AND '.join(where)}" if where else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT status, COUNT(*) AS total FROM complaints {clause} GROUP BY status",
                tuple(parameters),
            ).fetchall()
        by_status = {status: 0 for status in COMPLAINT_STATUSES}
        for row in rows:
            status = _normalize_status(row["status"])
            if status in by_status:
                by_status[status] += row["total"]
        return {
            "total": sum(by_status.values()),
            "submitted": by_status["SUBMITTED"],
            "pending": by_status["SUBMITTED"]
            + by_status["ACKNOWLEDGED"]
            + by_status["ASSIGNED"],
            "assigned": by_status["SUBMITTED"]
            + by_status["ACKNOWLEDGED"]
            + by_status["ASSIGNED"],
            "in_progress": by_status["IN_PROGRESS"],
            "resolved": by_status["RESOLVED"] + by_status["CLOSED"],
            "rejected": by_status["REJECTED"],
            "unassigned": self._unassigned_count(user_id=user_id),
        }

    def _unassigned_count(self, *, user_id: str | None = None) -> int:
        query = "SELECT COUNT(*) AS total FROM complaints WHERE assignment_status = 'UNASSIGNED'"
        parameters: tuple[str, ...] = ()
        if user_id is not None:
            query += " AND user_id = ?"
            parameters = (user_id,)
        with self._connect() as connection:
            return connection.execute(query, parameters).fetchone()["total"]

    def assign(self, identifier: str, authority_id: str, *, changed_by: str) -> dict:
        now = _now()
        with self._connect() as connection:
            authority = connection.execute(
                """
                SELECT uid FROM users
                WHERE uid = ? AND role = 'AUTHORITY' AND COALESCE(is_active, 1) = 1
                """,
                (authority_id,),
            ).fetchone()
            if authority is None:
                raise ValueError("An active demo Authority is required.")
            complaint = self._find(connection, identifier)
            if complaint is None:
                raise ComplaintNotFound("Complaint was not found.")
            if (
                complaint["authority_id"] == authority_id
                and complaint["assignment_status"] == "ASSIGNED"
            ):
                return self._detail(connection, complaint)
            connection.execute(
                """
                UPDATE complaints
                SET authority_id = ?, assignment_status = 'ASSIGNED', updated_at = ?
                WHERE id = ?
                """,
                (authority_id, now, complaint["id"]),
            )
            connection.execute(
                """
                INSERT INTO complaint_status_history (
                    id, complaint_id, old_status, new_status,
                    changed_by, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    complaint["id"],
                    complaint["status"],
                    complaint["status"],
                    changed_by,
                    "Assigned to a configured RoadLens demo Authority.",
                    now,
                ),
            )
            updated = self._find(connection, complaint["id"])
            return self._detail(connection, updated)

    def add_repair_evidence(
        self,
        identifier: str,
        *,
        authority_id: str,
        image_url: str,
        note: str | None,
    ) -> dict:
        now = _now()
        with self._connect() as connection:
            complaint = self._find(connection, identifier)
            if complaint is None:
                raise ComplaintNotFound("Complaint was not found.")
            if complaint["authority_id"] != authority_id:
                raise PermissionError("This complaint is assigned to another Authority.")
            update_id = str(uuid4())
            connection.execute(
                """
                INSERT INTO repair_updates (
                    id, complaint_id, authority_id, image_url, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    update_id,
                    complaint["id"],
                    authority_id,
                    image_url,
                    _optional_text(note),
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM repair_updates WHERE id = ?", (update_id,)
            ).fetchone()
        return dict(row)

    def update_status(
        self,
        identifier: str,
        *,
        new_status: str,
        changed_by: str,
        actor_role: str,
        note: str | None = None,
    ) -> dict:
        target = new_status.strip().upper()
        if target not in COMPLAINT_STATUSES:
            raise InvalidStatusTransition("Unknown complaint status.")
        now = _now()
        with self._connect() as connection:
            complaint = self._find(connection, identifier)
            if complaint is None:
                raise ComplaintNotFound("Complaint was not found.")
            if actor_role == "AUTHORITY":
                if complaint["authority_id"] != changed_by:
                    raise PermissionError("This complaint is assigned to another Authority.")
                allowed = AUTHORITY_TRANSITIONS.get(complaint["status"], frozenset())
            elif actor_role == "ADMIN":
                allowed = ADMIN_TRANSITIONS.get(complaint["status"], frozenset())
            else:
                raise PermissionError("Users cannot update complaint status.")
            if target not in allowed:
                raise InvalidStatusTransition(
                    f"{complaint['status']} cannot transition to {target}."
                )
            normalized_note = _optional_text(note)
            if target == "REJECTED" and not normalized_note:
                raise InvalidStatusTransition("A rejection reason is required.")
            if target == "RESOLVED":
                evidence = connection.execute(
                    "SELECT 1 FROM repair_updates WHERE complaint_id = ? LIMIT 1",
                    (complaint["id"],),
                ).fetchone()
                if evidence is None:
                    raise RepairEvidenceRequired(
                        "Repair evidence is required before resolution."
                    )
            connection.execute(
                "UPDATE complaints SET status = ?, updated_at = ? WHERE id = ?",
                (target, now, complaint["id"]),
            )
            connection.execute(
                """
                INSERT INTO complaint_status_history (
                    id, complaint_id, old_status, new_status,
                    changed_by, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    complaint["id"],
                    complaint["status"],
                    target,
                    changed_by,
                    normalized_note,
                    now,
                ),
            )
            updated = self._find(connection, complaint["id"])
            return self._detail(connection, updated)

    def _find(self, connection: sqlite3.Connection, identifier: str):
        return connection.execute(
            "SELECT * FROM complaints WHERE id = ? OR complaint_id = ?",
            (identifier, identifier),
        ).fetchone()

    def _detail(self, connection: sqlite3.Connection, complaint) -> dict:
        authority = None
        if complaint["authority_id"]:
            authority = connection.execute(
                """
                SELECT uid, name, email, assigned_area, role, is_active
                FROM users WHERE uid = ?
                """,
                (complaint["authority_id"],),
            ).fetchone()
        reporter = connection.execute(
            "SELECT uid, name, email, phone FROM users WHERE uid = ?",
            (complaint["user_id"],),
        ).fetchone()
        history = connection.execute(
            """
            SELECT * FROM complaint_status_history
            WHERE complaint_id = ? ORDER BY created_at
            """,
            (complaint["id"],),
        ).fetchall()
        repairs = connection.execute(
            """
            SELECT * FROM repair_updates
            WHERE complaint_id = ? ORDER BY created_at
            """,
            (complaint["id"],),
        ).fetchall()
        result = _complaint_dict(complaint)
        result["authority"] = None if authority is None else dict(authority)
        result["reporter"] = None if reporter is None else dict(reporter)
        result["history"] = [dict(item) for item in history]
        result["repair_updates"] = [dict(item) for item in repairs]
        return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _area_dict(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["is_active"] = bool(result["is_active"])
    return result


def _complaint_dict(row: sqlite3.Row) -> dict:
    result = dict(row)
    result["status"] = _normalize_status(result["status"])
    result["detections"] = json.loads(result.pop("detections_json"))
    return result


def _normalize_status(value: object) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").upper()
