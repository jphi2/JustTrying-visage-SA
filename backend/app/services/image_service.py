"""Image upload decoding and response encoding for the standalone API."""

from __future__ import annotations

import cv2
import numpy as np

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000


class ImageInputError(ValueError):
    """Raised when an uploaded image is invalid or exceeds safety limits."""


def decode_rgb(data: bytes, filename: str = "image") -> np.ndarray:
    if not data:
        raise ImageInputError(f"Le fichier {filename!r} est vide.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageInputError(
            f"Le fichier {filename!r} dépasse la limite de {MAX_UPLOAD_BYTES // (1024 * 1024)} Mo."
        )
    encoded = np.frombuffer(data, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise ImageInputError(f"Le fichier {filename!r} n'est pas une image lisible.")
    height, width = image.shape[:2]
    if height <= 0 or width <= 0 or height * width > MAX_IMAGE_PIXELS:
        raise ImageInputError(f"Dimensions d'image non autorisées : {width} x {height}.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def encode_jpeg(rgb: np.ndarray, quality: int = 95) -> bytes:
    if not isinstance(rgb, np.ndarray) or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("L'image de sortie doit être un tableau RGB HxWx3.")
    bgr = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    ok, encoded = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise RuntimeError("Impossible d'encoder l'image de sortie en JPEG.")
    return encoded.tobytes()
