from functools import lru_cache
from io import BytesIO
import logging

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError

from . import config
from .analysis_summary import enrich_analysis_result
from .auth import (
    AuthenticationConfigurationError,
    AuthenticationError,
    FirebaseTokenVerifier,
    bearer_token,
    require_role,
)
from .complaint_store import (
    ComplaintNotFound,
    ComplaintStore,
    InvalidStatusTransition,
    RepairEvidenceRequired,
)
from .errors import AnalysisError
from .inference import RoadDamageEnsemble
from .notification_service import (
    FirebasePushSender,
    NotificationNotFound,
    NotificationService,
    NotificationStore,
)
from .user_store import UserRecord, UserStore


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
app = FastAPI(title="RoadLens Local Inference API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

_token_verifier = FirebaseTokenVerifier(
    config.FIREBASE_PROJECT_ID,
    config.FIREBASE_SERVICE_ACCOUNT_JSON,
)
_user_store = UserStore(
    config.AUTH_DB_PATH,
    admin_uids=config.ROADLENS_ADMIN_UIDS,
    authority_uids=config.ROADLENS_AUTHORITY_UIDS,
)
_complaint_store = ComplaintStore(config.AUTH_DB_PATH)
_notification_store = NotificationStore(config.AUTH_DB_PATH)
_notification_service = NotificationService(
    _notification_store,
    FirebasePushSender(lambda: get_token_verifier().firebase_app()),
)
config.MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def get_token_verifier():
    return _token_verifier


def get_user_store():
    return _user_store


def get_complaint_store():
    return _complaint_store


def get_notification_store():
    return _notification_store


def get_notification_service():
    return _notification_service


def authenticated_user(authorization: str | None = Header(default=None)) -> UserRecord:
    try:
        token = bearer_token(authorization)
        claims = get_token_verifier().verify(token)
        user = get_user_store().resolve_user(claims)
        if user.role == "AUTHORITY" and not user.is_active:
            raise HTTPException(status_code=403, detail="This demo Authority account is inactive.")
        return user
    except AuthenticationConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def authenticated_role(*allowed_roles: str):
    def dependency(user: UserRecord = Depends(authenticated_user)) -> UserRecord:
        try:
            require_role(user.role, *allowed_roles)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return user

    return dependency


class AuthorityCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    temporary_password: str = Field(min_length=8, max_length=128)
    assigned_area: str = Field(min_length=2, max_length=160)
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)


class AuthorityUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    assigned_area: str = Field(min_length=2, max_length=160)
    is_active: bool = True
    city: str | None = Field(default=None, max_length=100)
    district: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)


class ComplaintStatusRequest(BaseModel):
    status: str = Field(min_length=4, max_length=30)
    note: str | None = Field(default=None, max_length=500)


class ComplaintAssignmentRequest(BaseModel):
    authority_id: str = Field(min_length=1, max_length=160)


class DeviceRegisterRequest(BaseModel):
    fcm_token: str = Field(min_length=10, max_length=4096)
    platform: str = Field(min_length=2, max_length=30)
    device_id: str = Field(min_length=3, max_length=200)


class NotificationPreferenceRequest(BaseModel):
    push_enabled: bool


@lru_cache(maxsize=1)
def get_model() -> RoadDamageEnsemble:
    return RoadDamageEnsemble()


@app.exception_handler(AnalysisError)
async def analysis_error_handler(_request, exc: AnalysisError):
    status = 422 if exc.code in {"INVALID_IMAGE", "IMAGE_DECODE_FAILED"} else 500
    return JSONResponse(status_code=status, content=exc.as_dict())


@app.get("/api/health")
def health() -> dict:
    try:
        details = get_model().details()
        return {"success": True, "model_loaded": True, "model": details}
    except AnalysisError as exc:
        return {"success": False, "model_loaded": False, "error": exc.as_dict()["error"]}


@app.get("/api/model")
def model_details() -> dict:
    try:
        return {"success": True, "model": get_model().details()}
    except AnalysisError as exc:
        raise HTTPException(status_code=500, detail=exc.as_dict()["error"]) from exc


@app.post("/api/auth/session")
def auth_session(user: UserRecord = Depends(authenticated_user)) -> dict:
    """Return the server-owned role for a verified Firebase identity."""
    return {"success": True, "user": user.as_dict()}


@app.get("/api/auth/me")
def auth_me(user: UserRecord = Depends(authenticated_user)) -> dict:
    return {"success": True, "user": user.as_dict()}


@app.get("/api/dashboard/user")
def user_dashboard(
    user: UserRecord = Depends(authenticated_role("USER")),
) -> dict:
    counts = get_complaint_store().counts(user_id=user.uid)
    return {
        "success": True,
        "user": user.as_dict(),
        "complaints": {
            "total": counts["total"],
            "pending": counts["pending"],
            "in_progress": counts["in_progress"],
            "resolved": counts["resolved"],
            "rejected": counts["rejected"],
        },
        "inspection_source": "device",
    }


@app.get("/api/dashboard/admin")
def admin_dashboard(
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    counts = get_user_store().role_counts()
    complaint_counts = get_complaint_store().counts()
    return {
        "success": True,
        "totals": {
            "users": counts["USER"],
            "authorities": counts["AUTHORITY"],
            "inspections": None,
            "complaints": complaint_counts["total"],
            "pending": complaint_counts["pending"],
            "in_progress": complaint_counts["in_progress"],
            "resolved": complaint_counts["resolved"],
        },
        "notice": "Complaint metrics use persisted RoadLens demo-project records.",
    }


@app.get("/api/dashboard/authority")
def authority_dashboard(
    user: UserRecord = Depends(authenticated_role("AUTHORITY")),
) -> dict:
    counts = get_complaint_store().counts(authority_id=user.uid)
    return {
        "success": True,
        "authority": user.as_dict(),
        "complaints": {
            "assigned": counts["assigned"],
            "in_progress": counts["in_progress"],
            "resolved": counts["resolved"],
            "items": get_complaint_store().list_for_authority(user.uid),
        },
    }


@app.get("/api/admin/users")
def admin_users(
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    return {
        "success": True,
        "users": [record.as_dict() for record in get_user_store().list_users()],
    }


@app.get("/api/admin/authorities")
def admin_authorities(
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    authorities = []
    for record in get_user_store().list_users(role="AUTHORITY"):
        item = record.as_dict()
        item["areas"] = get_complaint_store().authority_areas(record.uid)
        authorities.append(item)
    return {"success": True, "authorities": authorities}


@app.post("/api/admin/authorities", status_code=201)
def create_admin_authority(
    request: AuthorityCreateRequest,
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    verifier = get_token_verifier()
    try:
        uid = verifier.create_authority(
            name=request.name.strip(),
            email=request.email.strip().lower(),
            password=request.temporary_password,
        )
        record = get_user_store().create_authority(
            uid=uid,
            name=request.name.strip(),
            email=request.email.strip().lower(),
            assigned_area=request.assigned_area.strip(),
        )
        area = get_complaint_store().configure_authority_area(
            record.uid,
            area_name=request.assigned_area,
            city=request.city,
            district=request.district,
            state=request.state,
        )
    except AuthenticationConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except (AuthenticationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    body = record.as_dict()
    body["areas"] = [area]
    return {"success": True, "authority": body}


@app.put("/api/admin/authorities/{uid}")
def update_admin_authority(
    uid: str,
    request: AuthorityUpdateRequest,
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    existing = get_user_store().get_user(uid)
    if existing is None or existing.role != "AUTHORITY":
        raise HTTPException(status_code=404, detail="Demo Authority was not found.")
    try:
        get_token_verifier().update_authority(uid, name=request.name.strip())
    except AuthenticationConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AuthenticationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record = get_user_store().update_authority(
        uid,
        name=request.name.strip(),
        assigned_area=request.assigned_area.strip(),
        is_active=request.is_active,
    )
    area = get_complaint_store().configure_authority_area(
        uid,
        area_name=request.assigned_area,
        city=request.city,
        district=request.district,
        state=request.state,
        is_active=request.is_active,
    )
    body = record.as_dict()
    body["areas"] = [area]
    return {"success": True, "authority": body}


def _complaint_or_404(identifier: str) -> dict:
    complaint = get_complaint_store().get(identifier)
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint was not found.")
    return complaint


def _authorize_complaint_read(complaint: dict, user: UserRecord) -> None:
    if user.role == "ADMIN":
        return
    if user.role == "USER" and complaint["user_id"] == user.uid:
        return
    if user.role == "AUTHORITY" and complaint["authority_id"] == user.uid:
        return
    raise HTTPException(status_code=403, detail="This complaint is not available to this account.")


def _image_extension(content_type: str | None) -> str:
    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    extension = extensions.get(content_type or "")
    if extension is None:
        raise HTTPException(status_code=422, detail="Choose a JPEG, PNG, or WebP image.")
    return extension


def _store_media(data: bytes, *, category: str, filename: str) -> str:
    media_id = str(uuid4())
    relative = Path(category) / media_id / filename
    destination = config.MEDIA_DIR / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return "/media/" + relative.as_posix()


def _notification_safely(action, event_name: str):
    try:
        return action()
    except Exception:
        logging.getLogger("roadlens.notifications").exception(
            "Notification processing failed after committed event %s.", event_name
        )
        return None


def _annotated_image(data: bytes, detections: list[dict]) -> bytes | None:
    try:
        with Image.open(BytesIO(data)) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
        draw = ImageDraw.Draw(image)
        stroke = max(3, round(min(image.size) / 180))
        for detection in detections:
            box = detection["bbox"]
            coordinates = (box["x1"], box["y1"], box["x2"], box["y2"])
            draw.rectangle(coordinates, outline=(220, 38, 38), width=stroke)
            label = (
                f"{detection['damage_type']} "
                f"{float(detection['confidence']) * 100:.0f}%"
            )
            text_box = draw.textbbox((coordinates[0], coordinates[1]), label)
            draw.rectangle(text_box, fill=(220, 38, 38))
            draw.text((coordinates[0], coordinates[1]), label, fill=(255, 255, 255))
        output = BytesIO()
        image.save(output, format="JPEG", quality=90, optimize=True)
        return output.getvalue()
    except Exception:
        logging.getLogger("roadlens.analysis").exception(
            "Could not generate an annotated complaint image."
        )
        return None


@app.post("/api/v1/complaints")
async def create_complaint(
    file: UploadFile = File(...),
    inspection_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    gps_accuracy: float = Form(...),
    captured_at: str = Form(...),
    location_name: str | None = Form(default=None),
    user: UserRecord = Depends(authenticated_role("USER")),
) -> dict:
    inspection_id = inspection_id.strip()
    if not inspection_id:
        raise HTTPException(status_code=422, detail="Inspection ID is required.")
    existing = get_complaint_store().get_by_inspection(inspection_id)
    if existing is not None:
        if existing["user_id"] != user.uid:
            raise HTTPException(status_code=409, detail="This inspection is already linked to a complaint.")
        return {"success": True, "duplicate": True, "complaint": existing}
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="GPS coordinates are outside valid ranges.")
    if gps_accuracy < 0:
        raise HTTPException(status_code=422, detail="GPS accuracy cannot be negative.")
    try:
        captured = datetime.fromisoformat(captured_at)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="captured_at must be an ISO-8601 timestamp.") from exc
    if captured.utcoffset() is None:
        raise HTTPException(status_code=422, detail="captured_at must include a timezone offset.")

    extension = _image_extension(file.content_type)
    data = await file.read(config.MAX_IMAGE_BYTES + 1)
    if len(data) > config.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="The road image is too large.")
    result = enrich_analysis_result(
        get_model().analyze_bytes(data, file.filename or "road-image")
    )
    detections = result.get("detections") or []
    if not result.get("detected") or not detections:
        raise HTTPException(
            status_code=422,
            detail="A complaint requires a supported road-damage detection.",
        )
    primary = detections[0]
    severity = result.get("severity") or {}
    road_image_url = _store_media(
        data,
        category="complaints",
        filename=f"road{extension}",
    )
    annotated_data = _annotated_image(data, detections)
    annotated_image_url = (
        None
        if annotated_data is None
        else _store_media(
            annotated_data,
            category="complaints",
            filename="annotated.jpg",
        )
    )
    complaint, duplicate = get_complaint_store().create_complaint(
        inspection_id=inspection_id,
        user_id=user.uid,
        road_image_url=road_image_url,
        detections=detections,
        damage_type=str(primary["damage_type"]),
        damage_count=int(result["damage_count"]),
        estimated_damage_percentage=float(result["estimated_damage_percentage"]),
        damage_estimation_method=result.get("damage_estimation_method"),
        recommended_action=result.get("recommended_action"),
        severity=str(severity.get("level") or "LOW"),
        confidence=float(primary["confidence"]),
        latitude=latitude,
        longitude=longitude,
        gps_accuracy=gps_accuracy,
        location_name=location_name,
        captured_at=captured_at,
        annotated_image_url=annotated_image_url,
    )
    logging.getLogger("roadlens.complaints").info(
        "Report saved: report_id=%s damage_count=%d severity=%s assigned=%s duplicate=%s",
        complaint["complaint_id"],
        complaint["damage_count"],
        complaint["severity"],
        bool(complaint.get("authority_id")),
        duplicate,
    )
    if not duplicate and complaint.get("authority_id"):
        logging.getLogger("roadlens.notifications").info(
            "Attempting authority notification for report_id=%s.",
            complaint["complaint_id"],
        )
        notification = _notification_safely(
            lambda: get_notification_service().notify_complaint_assigned(complaint),
            "complaint_assigned",
        )
        try:
            complaint = get_complaint_store().update_authority_notification_status(
                complaint["id"],
                notification_status="SENT" if notification is not None else "FAILED",
                push_status=(
                    str(notification.get("push_status") or "FAILED")
                    if notification is not None
                    else "FAILED"
                ),
            )
            logging.getLogger("roadlens.notifications").info(
                "Authority notification recorded: report_id=%s in_app=%s push=%s.",
                complaint["complaint_id"],
                complaint["authority_notification_status"],
                complaint["authority_push_status"],
            )
        except Exception:
            logging.getLogger("roadlens.notifications").exception(
                "Could not persist complaint notification status."
            )
    return {"success": True, "duplicate": duplicate, "complaint": complaint}


@app.post("/api/v1/complaints/{identifier}/retry-authority-notification")
def retry_authority_notification(
    identifier: str,
    user: UserRecord = Depends(authenticated_role("USER", "ADMIN")),
) -> dict:
    complaint = _complaint_or_404(identifier)
    _authorize_complaint_read(complaint, user)
    if not complaint.get("authority_id"):
        raise HTTPException(
            status_code=422,
            detail="This complaint has not been assigned to a Demo Authority.",
        )
    notification = _notification_safely(
        lambda: get_notification_service().notify_complaint_assigned(
            complaint, force_push=True
        ),
        "complaint_assignment_retry",
    )
    complaint = get_complaint_store().update_authority_notification_status(
        complaint["id"],
        notification_status="SENT" if notification is not None else "FAILED",
        push_status=(
            str(notification.get("push_status") or "FAILED")
            if notification is not None
            else "FAILED"
        ),
    )
    return {"success": True, "complaint": complaint}


@app.get("/api/v1/complaints/me")
def my_complaints(user: UserRecord = Depends(authenticated_role("USER"))) -> dict:
    return {
        "success": True,
        "complaints": get_complaint_store().list_for_user(user.uid),
    }


@app.get("/api/v1/authority/complaints")
def authority_complaints(
    user: UserRecord = Depends(authenticated_role("AUTHORITY")),
) -> dict:
    return {
        "success": True,
        "complaints": get_complaint_store().list_for_authority(user.uid),
    }


@app.get("/api/v1/admin/complaints")
def admin_complaints(
    _user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    return {"success": True, "complaints": get_complaint_store().list_all()}


@app.get("/api/v1/complaints/{identifier}")
def complaint_details(
    identifier: str,
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY", "ADMIN")),
) -> dict:
    complaint = _complaint_or_404(identifier)
    _authorize_complaint_read(complaint, user)
    return {"success": True, "complaint": complaint}


@app.patch("/api/v1/complaints/{identifier}/status")
def update_complaint_status(
    identifier: str,
    request: ComplaintStatusRequest,
    user: UserRecord = Depends(authenticated_role("AUTHORITY", "ADMIN")),
) -> dict:
    try:
        complaint = get_complaint_store().update_status(
            identifier,
            new_status=request.status,
            changed_by=user.uid,
            actor_role=user.role,
            note=request.note,
        )
    except ComplaintNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (InvalidStatusTransition, RepairEvidenceRequired) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    _notification_safely(
        lambda: get_notification_service().notify_status_changed(complaint),
        "complaint_status_changed",
    )
    return {"success": True, "complaint": complaint}


@app.post("/api/v1/complaints/{identifier}/repair-evidence")
async def add_repair_evidence(
    identifier: str,
    file: UploadFile = File(...),
    note: str | None = Form(default=None),
    user: UserRecord = Depends(authenticated_role("AUTHORITY")),
) -> dict:
    extension = _image_extension(file.content_type)
    data = await file.read(config.MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=422, detail="Repair evidence image is empty.")
    if len(data) > config.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Repair evidence image is too large.")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=422,
            detail="Repair evidence must be a valid image.",
        ) from exc
    complaint = _complaint_or_404(identifier)
    if complaint["authority_id"] != user.uid:
        raise HTTPException(status_code=403, detail="This complaint is assigned to another Authority.")
    image_url = _store_media(
        data,
        category="repairs",
        filename=f"repair{extension}",
    )
    try:
        repair = get_complaint_store().add_repair_evidence(
            identifier,
            authority_id=user.uid,
            image_url=image_url,
            note=note,
        )
    except ComplaintNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    _notification_safely(
        lambda: get_notification_service().notify_repair_evidence_added(
            complaint,
            repair,
        ),
        "repair_evidence_added",
    )
    return {"success": True, "repair_update": repair}


@app.post("/api/v1/admin/complaints/{identifier}/assign")
def assign_complaint(
    identifier: str,
    request: ComplaintAssignmentRequest,
    user: UserRecord = Depends(authenticated_role("ADMIN")),
) -> dict:
    previous = _complaint_or_404(identifier)
    try:
        complaint = get_complaint_store().assign(
            identifier,
            request.authority_id,
            changed_by=user.uid,
        )
    except ComplaintNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if previous.get("authority_id") != complaint.get("authority_id"):
        authority_notification = _notification_safely(
            lambda: get_notification_service().notify_complaint_assigned(
                complaint,
                reassigned=previous.get("authority_id") is not None,
            ),
            "complaint_reassigned_authority",
        )
        complaint = get_complaint_store().update_authority_notification_status(
            complaint["id"],
            notification_status=(
                "SENT" if authority_notification is not None else "FAILED"
            ),
            push_status=(
                str(authority_notification.get("push_status") or "FAILED")
                if authority_notification is not None
                else "FAILED"
            ),
        )
        _notification_safely(
            lambda: get_notification_service().notify_user_reassigned(complaint),
            "complaint_reassigned_user",
        )
    return {"success": True, "complaint": complaint}


@app.get("/api/v1/notifications")
def notifications(
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    return {
        "success": True,
        "notifications": get_notification_store().list_for(user.uid),
        "push_enabled": get_notification_store().push_enabled(user.uid),
    }


@app.get("/api/v1/notifications/unread-count")
def notification_unread_count(
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    return {
        "success": True,
        "unread_count": get_notification_store().unread_count(user.uid),
    }


@app.post("/api/v1/notifications/mark-all-read")
def mark_all_notifications_read(
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    updated = get_notification_store().mark_all_read(user.uid)
    return {"success": True, "updated": updated, "unread_count": 0}


@app.patch("/api/v1/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    try:
        notification = get_notification_store().mark_read(notification_id, user.uid)
    except NotificationNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {"success": True, "notification": notification}


@app.get("/api/v1/notifications/preferences")
def notification_preferences(
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    return {
        "success": True,
        "push_enabled": get_notification_store().push_enabled(user.uid),
    }


@app.patch("/api/v1/notifications/preferences")
def update_notification_preferences(
    request: NotificationPreferenceRequest,
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    enabled = get_notification_store().set_push_enabled(
        user.uid, request.push_enabled
    )
    return {"success": True, "push_enabled": enabled}


@app.post("/api/v1/devices/register")
def register_device(
    request: DeviceRegisterRequest,
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    try:
        device = get_notification_store().register_device(
            user_id=user.uid,
            fcm_token=request.fcm_token,
            platform=request.platform,
            device_id=request.device_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"success": True, "device": device}


@app.delete("/api/v1/devices/{device_id}")
def unregister_device(
    device_id: str,
    user: UserRecord = Depends(authenticated_role("USER", "AUTHORITY")),
) -> dict:
    if not get_notification_store().deactivate_device(device_id, user.uid):
        raise HTTPException(status_code=404, detail="Registered device was not found.")
    return {"success": True}


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    gps_accuracy: float | None = Form(default=None),
    captured_at: str | None = Form(default=None),
) -> dict:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise AnalysisError("INVALID_IMAGE", "Choose a JPEG, PNG, or WebP road image.")
    metadata_values = (latitude, longitude, gps_accuracy, captured_at)
    if any(value is not None for value in metadata_values):
        if not all(value is not None for value in metadata_values):
            raise HTTPException(status_code=422, detail="Mobile inspection metadata must be complete.")
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise HTTPException(status_code=422, detail="GPS coordinates are outside valid ranges.")
        if gps_accuracy < 0:
            raise HTTPException(status_code=422, detail="GPS accuracy cannot be negative.")
        try:
            captured = datetime.fromisoformat(captured_at)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="captured_at must be an ISO-8601 timestamp.") from exc
        if captured.utcoffset() is None:
            raise HTTPException(status_code=422, detail="captured_at must include a timezone offset.")

    data = await file.read(config.MAX_IMAGE_BYTES + 1)
    result = get_model().analyze_bytes(data, file.filename or "image")
    if all(value is not None for value in metadata_values):
        result["inspection_metadata"] = {
            "latitude": latitude,
            "longitude": longitude,
            "gps_accuracy": gps_accuracy,
            "captured_at": captured_at,
        }
    return result


# Complaint and repair files are stored beneath the configured media root only.
app.mount("/media", StaticFiles(directory=config.MEDIA_DIR), name="media")

# Keep this mount last so /api and /media routes take precedence. Only the
# public web directory is exposed; backend source and ONNX model files remain private.
app.mount("/", StaticFiles(directory=config.WEB_DIR, html=True), name="frontend")
