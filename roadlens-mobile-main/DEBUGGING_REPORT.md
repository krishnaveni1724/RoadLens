# RoadLens image-analysis repair report

## ROOT CAUSE

- The project contained no AI model, inference runtime, backend endpoint, preprocessing code, postprocessing code, labels, or model metadata.
- Clicking analyze started a 1.45-second timer and then forced a successful state.
- The UI hard-coded pothole/crack labels, 94%/87% confidence, severity, a static bounding box, and 182 ms inference time.
- Uploaded files were used only to create a browser preview URL. Their bytes were never passed to a model.
- Result saving created another hard-coded detection object.

The failure was therefore not a tensor-decoding bug. No inference pipeline existed.

## FILES CHANGED

- `app.js` - removed timer predictions; added exact-file multipart analysis, explicit analysis states, API parsing, dynamic boxes/results, no-detection and error states.
- `styles.css` - dynamic confidence ring support.
- `README.md` and `start_app.ps1` - real server, inference and startup instructions.
- `backend/config.py` - centralized thresholds and model paths.
- `backend/errors.py` - stable technical error codes.
- `backend/inference.py` - validation, preprocessing, ONNX inference, output decoding, NMS, coordinate mapping, model ensemble and debug metrics.
- `backend/severity.py` - deterministic baseline severity heuristic.
- `backend/server.py` - FastAPI upload/model/health endpoints and frontend serving.
- `backend/requirements.txt` - pinned runtime dependencies.
- `backend/tests/*` - preprocessing, postprocessing, NMS, severity and API tests.
- `ai/debug_inference.py` - standalone inference and annotation utility.
- `ai_test_images/*` and `ai_test_outputs/*` - controlled fixtures and verified outputs.
- `backend/models/*` - packaged model artifacts and model-card material.

## MODEL DETAILS

### Road-distress generalist

- Format: ONNX, Ultralytics YOLOv8s detection export.
- Input: `images`, `float32 [1, 3, 640, 640]`.
- Output: `output0`, `float32 [1, 9, 8400]`.
- NMS embedded: no.
- SHA-256: `590A20E8C4A7BCBDB32E8A3B7B3A3C1D57D1FA8A7DDE5C83FCEC8928A4AA753F`.
- Classes from embedded metadata:
  - 0: Longitudinal Crack
  - 1: Transverse Crack
  - 2: Alligator Crack
  - 3: Pothole
  - 4: Other
- `Other` is excluded because its model card describes a weak mixed category covering manholes, patches, oil spills, and markings.

### Pothole specialist

- Format: ONNX, Ultralytics YOLOv8s detection export.
- Input: `images`, `float32 [1, 3, 640, 640]`.
- Output: `output0`, `float32 [1, 5, 8400]`.
- NMS embedded: no.
- SHA-256: `91DD7DE7A110C61314EA19A958FCC85C7B3461CC6D60D87FEFC08B41AC6E32C5`.
- Embedded name is the opaque value `0`; its model card defines the single class as pothole, so this model-specific mapping is configured explicitly as `0 -> Pothole`.

The original project model was absent. These are explicit replacement baselines, not representations of an undiscovered original model.

## PREPROCESSING

1. Reject empty, oversized, unsupported, unreadable, too-small, extremely dark, or severely blurred input.
2. Decode with Pillow and apply EXIF orientation.
3. Convert to RGB.
4. Calculate brightness and Laplacian variance quality metrics.
5. Preserve aspect ratio with 114-gray letterboxing to the model-reported 640x640 size.
6. Convert to contiguous `float32`, normalize to `[0,1]`, transpose HWC to CHW, and add the batch dimension.
7. Preserve scale and padding for reverse coordinate mapping.

No automatic low-light enhancement is applied because it has not been benchmarked against the packaged models.

## POSTPROCESSING

- Layout is selected from the actual tensor/class count; both packaged models use channel-first YOLOv8 output and are transposed to `[predictions, features]`.
- The decoder supports layouts with or without a separate objectness channel and rejects unknown shapes.
- Confidence threshold: 0.25, centralized in `backend/config.py`.
- NMS IoU threshold: 0.45, centralized in `backend/config.py`.
- NMS runs per class for each model and once more across the ensemble.
- Coordinates are converted from center-width-height to corners, reverse-scaled through letterbox padding, clamped to the original image, and returned in original-image pixels.
- Severity uses summed detected box area / image area and detection count. It is labelled `baseline severity heuristic`, deterministic, configurable, and separate from confidence.

## TESTS

Automated backend suite: **13 passed**.

- Preprocessing shape, dtype, normalization and letterbox padding: passed.
- Invalid decode contract: passed.
- Confidence filtering, class mapping and reverse coordinates: passed.
- Class-aware NMS: passed.
- Deterministic severity: passed.
- Model health/metadata API: passed.
- Invalid upload API contract: passed.
- Real pothole success response and original image dimensions: passed.
- Clean-road no-detection response: passed.
- Inference-failure/server-error response: passed.

Controlled images using the same production code:

- Test A - clear pothole: Pothole 96.2%; bounding box `(414.75, 429.14)-(1233.31, 780.71)`; passed visual review.
- Test B - clear crack: Alligator Crack 75.4%; passed.
- Test C - clean road: `no_detection`, `detections: []`; passed.
- Test D - night road: completed without crash; Alligator Crack 75.4%; passed with low-light classification.
- Test E - invalid blurry image: rejected as `INVALID_IMAGE`; passed.
- Test F - identical pothole analyzed twice: identical detections and coordinates; passed.

CPU inference in the verification environment was approximately 0.6-0.9 seconds for both ONNX models combined, excluding first-load overhead.

## KNOWN LIMITATIONS

- The Flutter Android client calls the deployed ONNX backend; inference remains server-side rather than on-device LiteRT. A physical Android device acceptance test is still required.
- The general model performs materially worse at night according to its model card; one passing low-light fixture does not establish broad night robustness.
- The two public replacement models were not trained specifically for this app's capture distribution.
- “Other” is intentionally ignored, which can reduce recall for ambiguous surface damage while avoiding fabricated pothole/crack labels.
- Severity is an operational baseline, not a civil-engineering assessment.
- GPS values in the existing web prototype remain simulated and were intentionally not modified.
- Embedded Ultralytics model metadata declares AGPL-3.0. Licensing must be reviewed before commercial distribution.

## NEXT IMPROVEMENTS

1. Replace the public baseline artifacts with the project's own validated weights and preserve their embedded class metadata.
2. Build a held-out, locally representative validation set including clean roads, repairs, shadows, rain, and night scenes.
3. Calibrate per-class confidence thresholds instead of using one global threshold.
4. Export the proven model to FP32/FP16 LiteRT, reuse the exact letterbox/postprocessing fixtures, and compare numerical outputs with ONNX.
5. Add real camera/GPS integration in Flutter only after desktop, LiteRT, and device outputs agree on the controlled corpus.
6. Benchmark optional low-light enhancement against the original image and keep it disabled unless it improves validated metrics.
