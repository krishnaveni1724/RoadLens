# RoadLens - real image inference build

RoadLens now analyzes the exact selected or captured image with two packaged ONNX models. The previous timer-driven, hard-coded pothole/crack result has been removed.

## Start the app

From PowerShell in this folder:

```powershell
.\start_app.ps1
```

The first run creates `backend/.venv` and installs the pinned packages in `backend/requirements.txt`. When the server prints that it is ready, open `http://127.0.0.1:4173/`.

Do not open `index.html` directly; real inference requires the local API.

## Real analysis flow

```text
selected File bytes
-> FastAPI multipart upload
-> Pillow decode + EXIF orientation
-> dimensions / brightness / blur validation
-> RGB letterbox to 640x640
-> float32 CHW tensor normalized to [0, 1]
-> ONNX Runtime inference
-> actual output-layout inspection
-> confidence filtering (0.25)
-> supported-class filtering
-> class-aware NMS (IoU 0.45)
-> reverse letterbox coordinates
-> deterministic baseline severity heuristic
-> structured JSON result
-> UI bounding boxes
```

No detection is a valid result and returns `detections: []`. Invalid images and inference failures are separate UI states.

## Models

- `backend/models/road_damage.onnx`: YOLOv8s road-distress generalist, output `[1, 9, 8400]`.
- `backend/models/pothole_specialist.onnx`: YOLOv8s pothole specialist, output `[1, 5, 8400]`.

Both expose `float32 [1, 3, 640, 640]` input metadata and declare that NMS is not embedded. The model metadata declares Ultralytics AGPL-3.0; review licensing before commercial distribution. The general model repository page separately labels the repository Apache-2.0, so this conflict is documented rather than resolved by assumption.

## Standalone inference

After `start_app.ps1` has created the environment:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\backend\.venv\Scripts\python.exe .\ai\debug_inference.py .\ai_test_images\known_pothole_01.jpg --output .\debug_output.jpg
```

The script uses the same decode, preprocessing, models, output decoder, filtering, NMS and severity code as the API.

## Tests

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\backend\.venv\Scripts\python.exe -m pip install pytest httpx
.\backend\.venv\Scripts\python.exe -m pytest .\backend\tests -q
```

See `DEBUGGING_REPORT.md` for the root cause, model contract, controlled-image results and limitations.

## Flutter Android client

The new production-structured Flutter client is under `mobile/`; the original web frontend is preserved under `web/`. The Android app uses the real rear camera and foreground GPS, persists inspections in Drift/SQLite, sends the exact captured image and capture metadata to the existing `POST /api/analyze` endpoint, renders returned boxes, and queues analysis when the backend is unavailable.

Start with:

- `docs/MOBILE_BUILD.md` for development, environment configuration, release signing, and APK commands.
- `docs/BACKEND_DEPLOYMENT.md` for local and HTTPS backend deployment.
- `docs/TEST_REPORT.md` for verified checks and remaining physical-device/client release gates.

Production API: `https://roadlens-api.onrender.com`. The client release is compiled with this HTTPS URL and uses the existing server-side ONNX ensemble; no inference data is mocked.
