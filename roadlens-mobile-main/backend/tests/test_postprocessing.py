import numpy as np

from backend.inference import LetterboxInfo, decode_yolo_output, non_maximum_suppression


CLASSES = {0: "Longitudinal Crack", 1: "Transverse Crack", 2: "Alligator Crack", 3: "Pothole", 4: "Other"}


def test_class_aware_nms_removes_overlapping_duplicate():
    boxes = np.array([[10, 10, 100, 100], [12, 12, 98, 98], [12, 12, 98, 98]], dtype=np.float32)
    scores = np.array([0.9, 0.8, 0.7], dtype=np.float32)
    classes = np.array([3, 3, 2])
    kept = non_maximum_suppression(boxes, scores, classes, 0.45)
    assert kept == [0, 2]


def test_yolov8_layout_confidence_filter_and_coordinate_restore():
    output = np.zeros((1, 9, 3), dtype=np.float32)
    output[0, :4, 0] = [320, 320, 200, 100]
    output[0, 7, 0] = 0.91  # class 3, pothole
    output[0, :4, 1] = [320, 320, 200, 100]
    output[0, 7, 1] = 0.10  # below threshold
    output[0, :4, 2] = [100, 100, 50, 50]
    output[0, 8, 2] = 0.99  # unsupported Other
    detections, debug = decode_yolo_output(output, CLASSES, LetterboxInfo(0.5, 0, 140, 640, 640), 1280, 720, 0.25, 0.45)
    assert len(detections) == 1
    assert detections[0]["damage_type"] == "Pothole"
    assert detections[0]["confidence"] == 0.91
    assert detections[0]["bbox"] == {"x1": 440.0, "y1": 260.0, "x2": 840.0, "y2": 460.0}
    assert debug["predictions_after_nms"] == 1
