# RoadLens test report

Date: 2026-08-25

## Automated checks

| Check | Result |
|---|---|
| Python backend API/unit suite | Passed: 13 tests |
| Flutter static analysis | Passed: no issues found |
| Flutter unit/widget tests | Passed: 4 tests |
| Render HTTPS health check | Passed: HTTP 200, both ONNX models loaded |
| Render real-image sequence | Passed: pothole, clean, pothole, clean; four HTTP 200 responses; final health passed |
| Android production release build | Passed: 57,253,446-byte APK |
| APK signature/package validation | Passed: client PKCS12 signer matched; APK Signature Scheme v2; `com.roadlens.roadlens`, version `1.0.0` |
| APK production configuration | Passed: compiled `production` environment and `https://roadlens-api.onrender.com` found in all three ABI snapshots |
| Manifest validation | Passed: camera, foreground location, internet, and connectivity only; no microphone/background location |
| Direct ONNX smoke inference | Passed: pothole fixture detected at 96.18%; clean-road fixture returned no detection |

Artifact: `RoadLens-production-1.0.0.apk`

Artifact SHA-256: `095CA46446915D021E3C8644250BF1D6C0A4D1AB5435D1CB4A14BDDFE40C0E53`

Signing certificate SHA-256: `0E6A95F02646177EA1063EF6BA87B67DC386DD3FFC8B046BCB45270A5009EF25`

Backend coverage includes the health endpoint, real image analysis contract, metadata validation/echo, invalid images, empty uploads, and inference error mapping. Flutter coverage includes domain parsing/state behavior, bounding-box contain-fit coordinate mapping, and the transparent local-mode login behavior.

## Implemented scenarios

- Rear camera selection, capture validation, flash toggle, retake, and use-photo flow
- Sequential camera/location permissions with denied/permanently-denied states
- GPS service-disabled handling, settings shortcut, timeout, retry, and no `0,0` fallback
- Timezone-aware capture timestamp
- Multipart upload of the exact saved image plus GPS metadata to the existing `/api/analyze` endpoint
- Real response parsing, no-damage state, annotated bounding boxes, confidence, severity, coordinates, address when geocoding succeeds, and timestamp
- Drift/SQLite persistence, inspection history, map-style coordinate list, and local settings
- Backend-unavailable `ANALYSIS_PENDING` persistence and connectivity-triggered retry

## Not verified in this environment

- Physical Android device install and hands-on rear-camera/GPS test: no Android device was connected.
- Client branding icon: no approved RoadLens logo asset was present, so the standard Flutter launcher placeholder remains.

Physical-device acceptance remains outstanding even though deployment, production signing, configuration, and artifact verification passed.
