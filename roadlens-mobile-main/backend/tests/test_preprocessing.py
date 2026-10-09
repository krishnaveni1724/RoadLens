import io

import numpy as np
import pytest
from PIL import Image

from backend.errors import AnalysisError
from backend.inference import decode_image, letterbox


def image_bytes(size=(800, 400), color=(120, 130, 140)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_letterbox_shape_dtype_normalization_and_padding():
    image = Image.new("RGB", (800, 400), (120, 130, 140))
    tensor, info = letterbox(image, 640, 640)
    assert tensor.shape == (1, 3, 640, 640)
    assert tensor.dtype == np.float32
    assert 0.0 <= float(tensor.min()) <= float(tensor.max()) <= 1.0
    assert info.scale == pytest.approx(0.8)
    assert info.pad_x == pytest.approx(0.0)
    assert info.pad_y == pytest.approx(160.0)


def test_invalid_bytes_are_rejected():
    with pytest.raises(AnalysisError) as exc:
        decode_image(b"not-an-image")
    assert exc.value.code == "IMAGE_DECODE_FAILED"
