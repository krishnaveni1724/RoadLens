from __future__ import annotations

import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


VALID_ROLES = frozenset({"USER", "ADMIN", "AUTHORITY"})


@dataclass(frozen=True)
class UserRecord:
    uid: str
    name: str | None
    email: str | None
    phone: str | None
    assigned_area: str | None
    is_active: bool
    role: str
    created_at: str
    updated_at: str

    def as_dict(self) -> dict:
        return asdict(self)


class UserStore:
    """Server-owned user roles backed by SQLite for the college demo."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        admin_uids: frozenset[str] = frozenset(),
        authority_uids: frozenset[str] = frozenset(),
    ):
        overlap = admin_uids & authority_uids
        if overlap:
            raise ValueError("A UID cannot be seeded as both ADMIN and AUTHORITY.")
        self.database_path = Path(database_path)
        self.admin_uids = admin_uids
        self.authority_uids = authority_uids
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    uid TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    assigned_area TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    role TEXT NOT NULL CHECK (role IN ('USER', 'ADMIN', 'AUTHORITY')),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            if "assigned_area" not in columns:
                connection.execute("ALTER TABLE users ADD COLUMN assigned_area TEXT")
            if "is_active" not in columns:
                connection.execute(
                    "ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
                )

    def _seeded_role(self, uid: str) -> str | None:
        if uid in self.admin_uids:
            return "ADMIN"
        if uid in self.authority_uids:
            return "AUTHORITY"
        return None

    def resolve_user(self, claims: dict) -> UserRecord:
        uid = str(claims.get("uid") or claims.get("sub") or "").strip()
        if not uid:
            raise ValueError("Verified Firebase token does not contain a UID.")

        name = _optional_text(claims.get("name"))
        email = _optional_text(claims.get("email"))
        phone = _optional_text(claims.get("phone_number"))
        now = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            existing = connection.execute(
                "SELECT * FROM users WHERE uid = ?", (uid,)
            ).fetchone()
            role = self._seeded_role(uid) or (existing["role"] if existing else "USER")
            connection.execute(
                """
                INSERT INTO users (
                    uid, name, email, phone, assigned_area, is_active,
                    role, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET
                    name = excluded.name,
                    email = excluded.email,
                    phone = excluded.phone,
                    role = excluded.role,
                    updated_at = excluded.updated_at
                """,
                (
                    uid,
                    name,
                    email,
                    phone,
                    existing["assigned_area"] if existing else None,
                    existing["is_active"] if existing else 1,
                    role,
                    existing["created_at"] if existing else now,
                    now,
                ),
            )
            row = connection.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        return _record(row)

    def get_user(self, uid: str) -> UserRecord | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE uid = ?", (uid,)).fetchone()
        return None if row is None else _record(row)

    def list_users(self, role: str | None = None) -> list[UserRecord]:
        if role is not None and role not in VALID_ROLES:
            raise ValueError("Unknown RoadLens role.")
        query = "SELECT * FROM users"
        parameters: tuple[str, ...] = ()
        if role is not None:
            query += " WHERE role = ?"
            parameters = (role,)
        query += " ORDER BY created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [_record(row) for row in rows]

    def role_counts(self) -> dict[str, int]:
        counts = {role: 0 for role in VALID_ROLES}
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT role, COUNT(*) AS total FROM users GROUP BY role"
            ).fetchall()
        for row in rows:
            counts[row["role"]] = row["total"]
        return counts

    def create_authority(
        self,
        *,
        uid: str,
        name: str,
        email: str,
        assigned_area: str,
    ) -> UserRecord:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    uid, name, email, phone, assigned_area, is_active,
                    role, created_at, updated_at
                ) VALUES (?, ?, ?, NULL, ?, 1, 'AUTHORITY', ?, ?)
                """,
                (uid, name, email, assigned_area, now, now),
            )
            row = connection.execute(
                "SELECT * FROM users WHERE uid = ?", (uid,)
            ).fetchone()
        return _record(row)

    def update_authority(
        self,
        uid: str,
        *,
        name: str,
        assigned_area: str,
        is_active: bool = True,
    ) -> UserRecord | None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE users
                SET name = ?, assigned_area = ?, is_active = ?, updated_at = ?
                WHERE uid = ? AND role = 'AUTHORITY'
                """,
                (name, assigned_area, 1 if is_active else 0, now, uid),
            )
            row = connection.execute(
                "SELECT * FROM users WHERE uid = ? AND role = 'AUTHORITY'", (uid,)
            ).fetchone()
        return None if row is None else _record(row)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _record(row: sqlite3.Row) -> UserRecord:
    data = dict(row)
    data["is_active"] = bool(data["is_active"])
    return UserRecord(**data)
