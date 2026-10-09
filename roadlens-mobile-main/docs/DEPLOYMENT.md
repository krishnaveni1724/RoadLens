# RoadLens production backend deployment

Last validated: 2026-08-29

## Production service

- Render Blueprint: `roadlens-production`
- Render service: `roadlens-api`
- Service URL: `https://roadlens-api.onrender.com`
- Source: private GitHub repository `kasimd33/roadlens-mobile`, branch `main`
- Runtime: Python 3.12.8
- ASGI application: `backend.server:app`
- Health check: `GET /api/health`

The repository-root `render.yaml` is the production configuration. It uses
Linux-safe `pathlib` paths, binds Uvicorn to `0.0.0.0:$PORT`, disables inference
debug output, and retains the ONNX Runtime memory settings already validated on
Render. Both ONNX files are tracked in `backend/models/`; they are loaded from
paths relative to `backend/config.py`, so no Windows path is used in production.

## Required Render environment variables

| Variable | Required | Secret | Production value or source |
| --- | --- | --- | --- |
| `PYTHON_VERSION` | Yes | No | `3.12.8` |
| `DEBUG_INFERENCE` | Yes | No | `false` |
| `AUTH_DB_PATH` | Yes | No | `/var/data/roadlens.sqlite3` |
| `MEDIA_DIR` | Yes | No | `/var/data/media` |
| `FIREBASE_PROJECT_ID` | For authenticated APIs/FCM | No | The real Firebase project ID used by the Android app |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | For authenticated APIs/FCM | Yes | The complete service-account JSON, entered only in Render |
| `ROADLENS_ADMIN_UIDS` | For Admin access | Treat as private | Comma-separated Firebase Authentication UIDs |
| `ROADLENS_AUTHORITY_UIDS` | Optional seed | Treat as private | Comma-separated Firebase Authentication UIDs for existing Authority accounts |
| `ORT_INTRA_OP_THREADS` | Yes | No | `1` |
| `ORT_INTER_OP_THREADS` | Yes | No | `1` |
| `ORT_DISABLE_CPU_ARENA` | Yes | No | `true` |
| `ORT_DISABLE_MEMORY_PATTERN` | Yes | No | `true` |

`FIREBASE_SERVICE_ACCOUNT_JSON` must never be added to Git, a Dart define, the
APK, documentation, or logs. In Render, open **roadlens-api → Environment**, add
the real values, and select **Save, rebuild, and deploy**. The `sync: false`
entries in `render.yaml` document required secrets, but Render does not add new
`sync: false` variables automatically to an existing Blueprint.

The Android Firebase project ID and package must match the client configuration.
Create the service-account key in the same Firebase/Google Cloud project, then
paste the JSON directly into the Render secret value. The backend uses it for
Firebase ID-token verification, Authority account administration, and FCM. It
remains server-side.

## Production database and media persistence

RoadLens currently uses one SQLite database for users, server-owned roles,
Authority areas, complaints, status history, repair evidence metadata,
notifications, preferences, and device tokens. Uploaded complaint and repair
images use `MEDIA_DIR`. Both paths are environment-controlled.

The existing Render service is on the Free plan. Its filesystem is ephemeral,
so the complete API can run, but database records and uploaded media are not
durable across restarts or deploys. Do not treat that configuration as a final
production datastore.

To enable durable production storage without changing RoadLens business logic:

1. In Render, open **roadlens-api → Compute** and select a paid instance.
2. Open **Disk**, add the smallest suitable persistent disk, and mount it at
   `/var/data`.
3. Confirm `AUTH_DB_PATH=/var/data/roadlens.sqlite3` and
   `MEDIA_DIR=/var/data/media` under **Environment**.
4. Redeploy once, then create a test account/complaint and restart the service.
5. Confirm the account, complaint, notification, and media URL still exist.

Attaching or upgrading a disk can create a charge and must be performed by the
Render account owner. Do not attach a disk at the repository root, and do not
store the SQLite database or uploaded media in Git.

## APIs included in the complete backend

Public:

- `GET /api/health`
- `GET /api/model`
- `POST /api/analyze`
- `GET /docs`
- `GET /openapi.json`
- `GET /media/...`

Firebase bearer token required:

- `POST /api/auth/session`
- `GET /api/auth/me`
- `GET /api/dashboard/user`
- `GET /api/dashboard/admin`
- `GET /api/dashboard/authority`
- `GET /api/admin/users`
- `GET /api/admin/authorities`
- `POST /api/admin/authorities`
- `PUT /api/admin/authorities/{uid}`
- `POST /api/v1/complaints`
- `GET /api/v1/complaints/me`
- `GET /api/v1/authority/complaints`
- `GET /api/v1/admin/complaints`
- `GET /api/v1/complaints/{identifier}`
- `POST /api/v1/complaints/{identifier}/retry-authority-notification`
- `PATCH /api/v1/complaints/{identifier}/status`
- `POST /api/v1/complaints/{identifier}/repair-evidence`
- `POST /api/v1/admin/complaints/{identifier}/assign`
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/unread-count`
- `POST /api/v1/notifications/mark-all-read`
- `PATCH /api/v1/notifications/{notification_id}/read`
- `GET /api/v1/notifications/preferences`
- `PATCH /api/v1/notifications/preferences`
- `POST /api/v1/devices/register`
- `DELETE /api/v1/devices/{device_id}`

Road-damage analysis responses include the real detection list, detection count,
the existing severity result, an explicitly approximate bounding-box affected
percentage, and a class-based recommended maintenance action. Submitted
complaints persist those fields plus separate in-app authority-notification and
FCM push-attempt statuses. FCM `SENT` means Firebase accepted the message; it
does not claim physical-device delivery.

Roles are resolved and enforced by the backend. Selecting a role in Flutter does
not grant that role. New identities default to `USER`; only UIDs configured by
the server or Authority accounts created by an Admin receive privileged roles.

## Local validation before deployment

From the repository root on Windows PowerShell:

```powershell
& '.\backend\.venv\Scripts\python.exe' -m pytest -q -p no:cacheprovider backend\tests
```

The suite covers ONNX inference, validation, authentication, role authorization,
dashboards, complaints, assignment/reassignment, status transitions, repair
evidence, notification persistence, token lifecycle, and push-failure fallback.

## Live validation after deployment

Verify the public contract:

```powershell
$baseUrl = 'https://roadlens-api.onrender.com'
Invoke-RestMethod "$baseUrl/api/health"
$openApi = Invoke-RestMethod "$baseUrl/openapi.json"
$openApi.paths.PSObject.Properties.Name | Sort-Object
```

Protected routes should return `401` without a bearer token. After the real
Firebase variables are configured, obtain a Firebase ID token by signing in
through the RoadLens client and validate the three role flows. Do not paste a
token into source control or documentation.

## Flutter production backend URL

RoadLens reads the backend URL from Dart compile-time defines. Production builds
must use the deployed HTTPS URL:

```powershell
flutter build apk --release `
  --dart-define=APP_ENV=production `
  --dart-define=API_BASE_URL=https://roadlens-api.onrender.com
```

Firebase client defines are also required for a real authenticated build. This
deployment task intentionally does not build an APK.

## Deployment gates

The backend is fully production-operable only after all of the following are
true:

- the complete backend commit is deployed and `/openapi.json` lists every route;
- the four Firebase/role environment variables contain real project values;
- the service has a persistent disk at `/var/data` (or an approved durable
  database/media replacement is implemented in a future, separately scoped task);
- authenticated USER, ADMIN, and AUTHORITY smoke tests pass against production;
- FCM is verified on a physical Android device.
