# RoadLens backend deployment

## Reused components

- Entry point: `backend/server.py` (`backend.server:app`)
- Existing endpoint: `POST /api/analyze`
- Existing ONNX inference and model selection code under `backend/roadlens_ai`
- Existing ONNX weights under `backend/models`
- Existing preprocessing, confidence filtering, non-maximum suppression, bounding-box mapping, classification, and severity calculation

The mobile integration did not duplicate or replace the inference pipeline. The existing multipart endpoint now accepts optional `latitude`, `longitude`, `gps_accuracy`, and timezone-aware `captured_at` fields. When all are present and valid, the response echoes them as `inspection_metadata`; image inference is unchanged.

## Local development

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
$env:PYTHONPATH=(Get-Location).Path
uvicorn backend.server:app --host 0.0.0.0 --port 4173
```

Smoke check:

```powershell
Invoke-RestMethod http://127.0.0.1:4173/api/health
```

## Production deployment

The production service is deployed from the private `kasimd33/roadlens-mobile` GitHub repository through the repository-root `render.yaml` Blueprint:

- URL: `https://roadlens-api.onrender.com`
- Health: `GET /api/health`
- Analysis: `POST /api/analyze`
- Runtime: Python 3.12 on a Render Web Service
- Start command: `python -m uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
- Health check path: `/api/health`

The production ONNX sessions use sequential, single-threaded execution with CPU arenas and memory patterns disabled. This keeps both real YOLO models within the free instance's memory limit during repeated inference. No mock inference is used.

For another hosting target, a representative start command is:

```text
uvicorn backend.server:app --host 0.0.0.0 --port $PORT --proxy-headers
```

The hosting platform must provide enough memory for ONNX Runtime and retain the model directory. Put the service behind managed TLS/HTTPS, configure health checks against `/api/health`, set request-size and request-timeout limits appropriate for phone camera images, and restrict cross-origin policy to approved clients where relevant.

## Operational validation

The Render service passed four consecutive HTTPS analyses in an alternating sequence: pothole, clean road, pothole, clean road. Both pothole requests produced the same real 0.961797-confidence Pothole detection and `HIGH` severity; both clean-road requests returned a valid no-detection response. `/api/health` returned HTTP 200 before and after the sequence with both models loaded.

Render free instances spin down after inactivity, so the first request after an idle period can take 50 seconds or more while the service wakes.
