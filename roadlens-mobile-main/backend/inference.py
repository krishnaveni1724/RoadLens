from __future__ import annotations

import ast
import io
import logging
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps, UnidentifiedImageError

from . import config
from .analysis_summary import enrich_analysis_result
from .errors import AnalysisError
from .severity import calculate_severity


LOGGER = logging.getLogger("roadlens.inference")
RESAMPLING = getattr(Image, "Resampling", Image).BILINEAR


@dataclass(frozen=True)
class LetterboxInfo:
    scale: float
    pad_x: float
    pad_y: float
    input_width: int
    input_height: int


def image_quality(image: Image.Image) -> dict:
    gray = np.asarray(image.convert("L"), dtype=np.float32)
    brightness = float(gray.mean())
    if gray.shape[0] < 3 or gray.shape[1] < 3:
        blur_variance = 0.0
    else:
        center = gray[1:-1, 1:-1]
        laplacian = (
            gray[:-2, 1:-1] + gray[2:, 1:-1] + gray[1:-1, :-2] + gray[1:-1, 2:] - 4.0 * center
        )
        blur_variance = float(laplacian.var())
    return {
        "brightness": round(brightness, 2),
        "blur_variance": round(blur_variance, 2),
        "lighting": "LOW_LIGHT" if brightness < 70.0 else "DAY",
    }


def decode_image(data: bytes) -> tuple[Image.Image, dict]:
    if not data:
        raise AnalysisError("INVALID_IMAGE", "The selected image is empty.")
    if len(data) > config.MAX_IMAGE_BYTES:
        raise AnalysisError("INVALID_IMAGE", "The image is larger than the 15 MB limit.")
    try:
        with Image.open(io.BytesIO(data)) as opened:
            opened.verify()
        with Image.open(io.BytesIO(data)) as opened:
            image = ImageOps.exif_transpose(opened).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise AnalysisError("IMAGE_DECODE_FAILED", "The selected file is not a readable image.", detail=str(exc)) from exc

    width, height = image.size
    if min(width, height) < config.MIN_IMAGE_EDGE:
        raise AnalysisError("INVALID_IMAGE", f"Image dimensions are too small ({width}×{height}).")
    quality = image_quality(image)
    if quality["brightness"] < config.MIN_BRIGHTNESS:
        raise AnalysisError("INVALID_IMAGE", "Image is too dark for reliable analysis.")
    if quality["blur_variance"] < config.MIN_BLUR_VARIANCE:
        raise AnalysisError("INVALID_IMAGE", "Image is too blurred for reliable analysis.")
    return image, quality


def letterbox(image: Image.Image, input_width: int, input_height: int) -> tuple[np.ndarray, LetterboxInfo]:
    original_width, original_height = image.size
    scale = min(input_width / original_width, input_height / original_height)
    resized_width = max(1, round(original_width * scale))
    resized_height = max(1, round(original_height * scale))
    resized = image.resize((resized_width, resized_height), RESAMPLING)
    pad_x = (input_width - resized_width) / 2.0
    pad_y = (input_height - resized_height) / 2.0
    canvas = Image.new("RGB", (input_width, input_height), (114, 114, 114))
    canvas.paste(resized, (round(pad_x), round(pad_y)))
    array = np.asarray(canvas, dtype=np.float32) / 255.0
    tensor = np.transpose(array, (2, 0, 1))[None, ...]
    return np.ascontiguousarray(tensor), LetterboxInfo(scale, pad_x, pad_y, input_width, input_height)


def box_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])
    intersection = np.maximum(0.0, x2 - x1) * np.maximum(0.0, y2 - y1)
    area_a = max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])
    area_b = np.maximum(0.0, boxes[:, 2] - boxes[:, 0]) * np.maximum(0.0, boxes[:, 3] - boxes[:, 1])
    return intersection / np.maximum(area_a + area_b - intersection, 1e-9)


def non_maximum_suppression(boxes: np.ndarray, scores: np.ndarray, class_ids: np.ndarray, iou_threshold: float) -> list[int]:
    kept: list[int] = []
    for class_id in np.unique(class_ids):
        indices = np.where(class_ids == class_id)[0]
        order = indices[np.argsort(scores[indices])[::-1]]
        while order.size:
            best = int(order[0])
            kept.append(best)
            if order.size == 1:
                break
            remaining = order[1:]
            order = remaining[box_iou(boxes[best], boxes[remaining]) <= iou_threshold]
    return sorted(kept, key=lambda index: float(scores[index]), reverse=True)[: config.MAX_DETECTIONS]


def decode_yolo_output(
    raw_output: np.ndarray,
    class_names: dict[int, str],
    letterbox_info: LetterboxInfo,
    original_width: int,
    original_height: int,
    confidence_threshold: float,
    iou_threshold: float,
) -> tuple[list[dict], dict]:
    output = np.asarray(raw_output)
    if output.ndim == 3 and output.shape[0] == 1:
        output = output[0]
    if output.ndim != 2:
        raise AnalysisError("MODEL_OUTPUT_INVALID", f"Expected a 2D YOLO tensor after batch removal, got {output.shape}.")

    class_count = len(class_names)
    feature_counts = {4 + class_count, 5 + class_count}
    if output.shape[0] in feature_counts:
        predictions = output.T
    elif output.shape[1] in feature_counts:
        predictions = output
    else:
        raise AnalysisError("MODEL_OUTPUT_INVALID", f"Cannot map output shape {tuple(output.shape)} to {class_count} classes.")

    if not np.isfinite(predictions).all():
        raise AnalysisError("MODEL_OUTPUT_INVALID", "Model output contains NaN or infinite values.")

    has_objectness = predictions.shape[1] == 5 + class_count
    class_scores = predictions[:, 5:] if has_objectness else predictions[:, 4:]
    class_ids = np.argmax(class_scores, axis=1)
    scores = class_scores[np.arange(len(predictions)), class_ids]
    if has_objectness:
        scores = scores * predictions[:, 4]

    highest_confidence = float(scores.max()) if scores.size else 0.0
    confidence_mask = scores >= confidence_threshold
    predictions = predictions[confidence_mask]
    scores = scores[confidence_mask]
    class_ids = class_ids[confidence_mask]

    supported_mask = np.array([int(class_id) in config.SUPPORTED_CLASS_IDS for class_id in class_ids], dtype=bool)
    predictions = predictions[supported_mask]
    scores = scores[supported_mask]
    class_ids = class_ids[supported_mask]
    before_nms = int(len(scores))
    if not before_nms:
        return [], {"predictions_before_filter": int(len(confidence_mask)), "predictions_after_filter": 0, "predictions_after_nms": 0, "highest_confidence": highest_confidence}

    xywh = predictions[:, :4].astype(np.float32)
    boxes = np.column_stack((xywh[:, 0] - xywh[:, 2] / 2, xywh[:, 1] - xywh[:, 3] / 2, xywh[:, 0] + xywh[:, 2] / 2, xywh[:, 1] + xywh[:, 3] / 2))
    keep = non_maximum_suppression(boxes, scores, class_ids, iou_threshold)

    detections: list[dict] = []
    for index in keep:
        x1, y1, x2, y2 = boxes[index]
        x1 = float(np.clip((x1 - letterbox_info.pad_x) / letterbox_info.scale, 0, original_width))
        y1 = float(np.clip((y1 - letterbox_info.pad_y) / letterbox_info.scale, 0, original_height))
        x2 = float(np.clip((x2 - letterbox_info.pad_x) / letterbox_info.scale, 0, original_width))
        y2 = float(np.clip((y2 - letterbox_info.pad_y) / letterbox_info.scale, 0, original_height))
        if x2 <= x1 or y2 <= y1:
            continue
        class_id = int(class_ids[index])
        detections.append({
            "class_id": class_id,
            "damage_type": class_names[class_id],
            "confidence": round(float(scores[index]), 6),
            "bbox": {"x1": round(x1, 2), "y1": round(y1, 2), "x2": round(x2, 2), "y2": round(y2, 2)},
        })
    debug = {
        "predictions_before_filter": int(len(confidence_mask)),
        "predictions_after_filter": before_nms,
        "predictions_after_nms": len(detections),
        "highest_confidence": round(highest_confidence, 6),
    }
    return detections, debug


class RoadDamageModel:
    def __init__(self, model_path: str | Path = config.MODEL_PATH, *, class_names_override: dict[int, str] | None = None, model_name: str = "road-distress-generalist"):
        self.model_path = Path(model_path)
        self.model_name = model_name
        if not self.model_path.is_file():
            raise AnalysisError("MODEL_LOAD_FAILED", f"Model file was not found: {self.model_path}")
        try:
            session_options = ort.SessionOptions()
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            session_options.intra_op_num_threads = config.ORT_INTRA_OP_THREADS
            session_options.inter_op_num_threads = config.ORT_INTER_OP_THREADS
            session_options.enable_cpu_mem_arena = not config.ORT_DISABLE_CPU_ARENA
            session_options.enable_mem_pattern = not config.ORT_DISABLE_MEMORY_PATTERN
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            self.session = ort.InferenceSession(
                str(self.model_path),
                sess_options=session_options,
                providers=["CPUExecutionProvider"],
            )
        except Exception as exc:
            raise AnalysisError("MODEL_LOAD_FAILED", "The road-damage model could not be initialized.", detail=str(exc)) from exc

        self.input = self.session.get_inputs()[0]
        self.output = self.session.get_outputs()[0]
        if self.input.type != "tensor(float)" or len(self.input.shape) != 4:
            raise AnalysisError("MODEL_LOAD_FAILED", f"Unsupported input tensor: {self.input.type} {self.input.shape}")
        self.input_height = int(self.input.shape[2])
        self.input_width = int(self.input.shape[3])
        metadata = self.session.get_modelmeta().custom_metadata_map
        try:
            names = ast.literal_eval(metadata["names"])
            self.class_names = {int(key): str(value) for key, value in names.items()}
        except Exception as exc:
            raise AnalysisError("MODEL_LOAD_FAILED", "Model class metadata is missing or invalid.", detail=str(exc)) from exc
        if class_names_override is not None:
            if len(class_names_override) != len(self.class_names):
                raise AnalysisError("MODEL_LOAD_FAILED", "Class-name override does not match the model output.")
            self.class_names = dict(class_names_override)
        self.model_metadata = metadata
        LOGGER.info("Model path: %s", self.model_path)
        LOGGER.info("Model input: %s %s %s", self.input.name, self.input.shape, self.input.type)
        LOGGER.info("Model output: %s %s %s", self.output.name, self.output.shape, self.output.type)
        LOGGER.info("Classes: %s", self.class_names)

    def details(self) -> dict:
        return {
            "name": self.model_name,
            "path": str(self.model_path),
            "format": "ONNX",
            "input": {"name": self.input.name, "shape": self.input.shape, "datatype": self.input.type},
            "output": {"name": self.output.name, "shape": self.output.shape, "datatype": self.output.type},
            "classes": self.class_names,
            "confidence_threshold": config.CONFIDENCE_THRESHOLD,
            "iou_threshold": config.IOU_THRESHOLD,
            "nms_in_model": False,
        }

    def analyze_bytes(self, data: bytes, filename: str = "image") -> dict:
        total_start = time.perf_counter()
        image, quality = decode_image(data)
        original_width, original_height = image.size

        preprocess_start = time.perf_counter()
        tensor, letterbox_info = letterbox(image, self.input_width, self.input_height)
        preprocess_ms = (time.perf_counter() - preprocess_start) * 1000

        inference_start = time.perf_counter()
        try:
            raw_output = self.session.run([self.output.name], {self.input.name: tensor})[0]
        except Exception as exc:
            raise AnalysisError("INFERENCE_FAILED", "The model could not analyze this image.", detail=str(exc)) from exc
        inference_ms = (time.perf_counter() - inference_start) * 1000

        postprocess_start = time.perf_counter()
        detections, debug_counts = decode_yolo_output(
            raw_output,
            self.class_names,
            letterbox_info,
            original_width,
            original_height,
            config.CONFIDENCE_THRESHOLD,
            config.IOU_THRESHOLD,
        )
        severity = calculate_severity(detections, original_width, original_height)
        postprocess_ms = (time.perf_counter() - postprocess_start) * 1000
        total_ms = (time.perf_counter() - total_start) * 1000

        if config.DEBUG_INFERENCE:
            flat = raw_output.reshape(-1)
            LOGGER.info("Image %s: bytes=%d size=%dx%d decoded=true", filename, len(data), original_width, original_height)
            LOGGER.info("Raw output shape=%s sample=%s", raw_output.shape, np.array2string(flat[:12], precision=4))
            LOGGER.info("Counts=%s final_classes=%s", debug_counts, [d["damage_type"] for d in detections])

        response = {
            "success": True,
            "status": "success" if detections else "no_detection",
            "detected": bool(detections),
            "message": "Road damage detected" if detections else "No supported road damage detected",
            "image": {"width": original_width, "height": original_height, "filename": filename},
            "quality": quality,
            "detections": detections,
            "severity": None if severity is None else {
                "level": severity.level,
                "damage_area_ratio": round(severity.damage_area_ratio, 6),
                "method": severity.method,
            },
            "timing_ms": {
                "preprocessing": round(preprocess_ms, 2),
                "inference": round(inference_ms, 2),
                "postprocessing": round(postprocess_ms, 2),
                "total": round(total_ms, 2),
            },
        }
        if config.DEBUG_INFERENCE:
            response["debug"] = {
                **debug_counts,
                "input_tensor_shape": list(tensor.shape),
                "output_tensor_shape": list(raw_output.shape),
                "model_input_size": [self.input_width, self.input_height],
            }
        LOGGER.info(
            "Inference completed: bytes=%d image=%dx%d detections=%d classes=%s total_ms=%.2f",
            len(data),
            original_width,
            original_height,
            len(detections),
            [item["damage_type"] for item in detections],
            total_ms,
        )
        return enrich_analysis_result(response)


class RoadDamageEnsemble:
    """Two real ONNX detectors: RDD multi-class + a pothole specialist."""

    def __init__(self):
        self.general = RoadDamageModel(config.MODEL_PATH, model_name="road-distress-generalist")
        self.pothole = RoadDamageModel(
            config.POTHOLE_MODEL_PATH,
            class_names_override={0: "Pothole"},
            model_name="pothole-specialist",
        )

    def details(self) -> dict:
        return {
            "strategy": "class-aware ensemble with cross-model NMS",
            "models": [self.general.details(), self.pothole.details()],
            "confidence_threshold": config.CONFIDENCE_THRESHOLD,
            "iou_threshold": config.IOU_THRESHOLD,
        }

    @staticmethod
    def _merge_detections(detections: list[dict]) -> list[dict]:
        if not detections:
            return []
        class_keys = {name: index for index, name in enumerate(sorted({item["damage_type"] for item in detections}))}
        boxes = np.array([[item["bbox"]["x1"], item["bbox"]["y1"], item["bbox"]["x2"], item["bbox"]["y2"]] for item in detections], dtype=np.float32)
        scores = np.array([item["confidence"] for item in detections], dtype=np.float32)
        class_ids = np.array([class_keys[item["damage_type"]] for item in detections], dtype=np.int64)
        keep = non_maximum_suppression(boxes, scores, class_ids, config.IOU_THRESHOLD)
        return [detections[index] for index in keep]

    def analyze_bytes(self, data: bytes, filename: str = "image") -> dict:
        total_start = time.perf_counter()
        general_result = self.general.analyze_bytes(data, filename)
        pothole_result = self.pothole.analyze_bytes(data, filename)
        detections = [
            *({**item, "source_model": self.general.model_name} for item in general_result["detections"]),
            *({**item, "source_model": self.pothole.model_name} for item in pothole_result["detections"]),
        ]
        detections = self._merge_detections(detections)
        width = general_result["image"]["width"]
        height = general_result["image"]["height"]
        severity = calculate_severity(detections, width, height)
        timing = {
            key: round(general_result["timing_ms"][key] + pothole_result["timing_ms"][key], 2)
            for key in ("preprocessing", "inference", "postprocessing")
        }
        timing["total"] = round((time.perf_counter() - total_start) * 1000, 2)
        response = {
            "success": True,
            "status": "success" if detections else "no_detection",
            "detected": bool(detections),
            "message": "Road damage detected" if detections else "No supported road damage detected",
            "image": general_result["image"],
            "quality": general_result["quality"],
            "detections": detections,
            "severity": None if severity is None else {
                "level": severity.level,
                "damage_area_ratio": round(severity.damage_area_ratio, 6),
                "method": severity.method,
            },
            "timing_ms": timing,
        }
        if config.DEBUG_INFERENCE:
            response["debug"] = {
                "input_tensor_shape": general_result["debug"]["input_tensor_shape"],
                "output_tensor_shapes": [general_result["debug"]["output_tensor_shape"], pothole_result["debug"]["output_tensor_shape"]],
                "model_input_size": general_result["debug"]["model_input_size"],
                "highest_confidence": max(general_result["debug"]["highest_confidence"], pothole_result["debug"]["highest_confidence"]),
                "predictions_after_nms": len(detections),
                "models": {
                    self.general.model_name: general_result["debug"],
                    self.pothole.model_name: pothole_result["debug"],
                },
                "final_classes": [item["damage_type"] for item in detections],
            }
        LOGGER.info(
            "Ensemble inference completed: bytes=%d image=%dx%d detections=%d classes=%s total_ms=%.2f",
            len(data),
            width,
            height,
            len(detections),
            [item["damage_type"] for item in detections],
            timing["total"],
        )
        return enrich_analysis_result(response)
