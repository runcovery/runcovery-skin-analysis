"""Image I/O utilities with EXIF scrubbing."""
import base64
import io
import cv2
import numpy as np
from PIL import Image


def read_image_bgr(data: bytes) -> np.ndarray:
    """
    Read image from bytes into BGR numpy array.
    Strips EXIF data for privacy.
    """
    # Load with PIL to strip EXIF
    pil_img = Image.open(io.BytesIO(data))

    # Remove EXIF data
    img_without_exif = Image.new(pil_img.mode, pil_img.size)
    img_without_exif.putdata(list(pil_img.getdata()))

    # Convert to numpy BGR for OpenCV
    img_rgb = np.array(img_without_exif)

    # Handle grayscale
    if len(img_rgb.shape) == 2:
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_GRAY2BGR)
    elif img_rgb.shape[2] == 4:  # RGBA
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGBA2BGR)
    else:  # RGB
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    return img_bgr


def encode_png_base64(img: np.ndarray) -> str:
    """
    Encode numpy array as base64 PNG data URI.
    Expects RGBA or grayscale image.
    """
    # Encode as PNG
    success, buffer = cv2.imencode(".png", img)
    if not success:
        raise ValueError("Failed to encode image as PNG")

    # Convert to base64
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def resize_max(img: np.ndarray, max_size: int) -> np.ndarray:
    """Resize image so largest dimension is max_size, maintaining aspect ratio."""
    h, w = img.shape[:2]
    if max(h, w) <= max_size:
        return img

    scale = max_size / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
