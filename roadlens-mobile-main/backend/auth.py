from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials


class AuthenticationError(Exception):
    pass


class AuthenticationConfigurationError(AuthenticationError):
    pass


class TokenVerifier(Protocol):
    def verify(self, token: str) -> dict: ...


@dataclass(frozen=True)
class FirebaseTokenVerifier:
    project_id: str
    service_account_json: str = field(default="", repr=False)

    def _app(self):
        if not self.project_id:
            raise AuthenticationConfigurationError(
                "Firebase token verification is not configured on the server."
            )
        try:
            app = firebase_admin.get_app("roadlens-auth")
        except ValueError:
            credential = None
            if self.service_account_json:
                try:
                    credential = credentials.Certificate(
                        json.loads(self.service_account_json)
                    )
                except (TypeError, ValueError) as exc:
                    raise AuthenticationConfigurationError(
                        "Firebase service-account JSON is invalid."
                    ) from exc
            app = firebase_admin.initialize_app(
                credential,
                options={"projectId": self.project_id},
                name="roadlens-auth",
            )
        return app

    def verify(self, token: str) -> dict:
        app = self._app()
        try:
            return firebase_auth.verify_id_token(token, app=app)
        except Exception as exc:
            raise AuthenticationError("Firebase ID token is invalid or expired.") from exc

    def firebase_app(self):
        """Return the configured Firebase app for server-side FCM delivery."""
        return self._app()

    def create_authority(self, *, name: str, email: str, password: str) -> str:
        try:
            user = firebase_auth.create_user(
                display_name=name,
                email=email,
                password=password,
                app=self._app(),
            )
            return user.uid
        except AuthenticationConfigurationError:
            raise
        except Exception as exc:
            raise AuthenticationError(
                "Firebase could not create the demo Authority account."
            ) from exc

    def update_authority(self, uid: str, *, name: str) -> None:
        try:
            firebase_auth.update_user(uid, display_name=name, app=self._app())
        except AuthenticationConfigurationError:
            raise
        except Exception as exc:
            raise AuthenticationError(
                "Firebase could not update the demo Authority account."
            ) from exc


def bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthenticationError("Authorization bearer token is required.")
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationError("Authorization header must use the Bearer scheme.")
    return token.strip()


def require_role(actual_role: str, *allowed_roles: str) -> None:
    if actual_role not in allowed_roles:
        raise PermissionError("This account is not authorized for that operation.")
