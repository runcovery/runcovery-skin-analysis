"""Image preprocessing: color constancy, normalization, face cropping."""
import cv2
import numpy as np


def preprocess(img_bgr: np.ndarray, max_size: int = 1024) -> np.ndarray:
    """
    Preprocess image for skin analysis.

    Steps:
    1. Resize to max dimension
    2. Color constancy (gray-world assumption)
    3. CLAHE for contrast enhancement
    4. Gamma correction

    Args:
        img_bgr: Input BGR image
        max_size: Maximum dimension

    Returns:
        Preprocessed BGR image
    """
    # Resize if needed
    h, w = img_bgr.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Gray-world color constancy
    img_bgr = gray_world_normalization(img_bgr)

    # CLAHE for contrast enhancement on L channel
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    lab = cv2.merge([l, a, b])
    img_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Gamma correction (slight brightening)
    img_bgr = gamma_correction(img_bgr, gamma=1.1)

    return img_bgr


def gray_world_normalization(img_bgr: np.ndarray) -> np.ndarray:
    """
    Apply gray-world color constancy assumption.

    Assumes the average color in the scene should be gray (neutral).
    Adjusts color channels to achieve this.
    """
    img_float = img_bgr.astype(np.float32)

    # Compute mean of each channel
    b_mean = np.mean(img_float[..., 0])
    g_mean = np.mean(img_float[..., 1])
    r_mean = np.mean(img_float[..., 2])

    # Gray world: target is mean of all channels
    gray_mean = (b_mean + g_mean + r_mean) / 3

    # Scale each channel
    if b_mean > 0:
        img_float[..., 0] *= gray_mean / b_mean
    if g_mean > 0:
        img_float[..., 1] *= gray_mean / g_mean
    if r_mean > 0:
        img_float[..., 2] *= gray_mean / r_mean

    # Clip and convert back
    img_float = np.clip(img_float, 0, 255)
    return img_float.astype(np.uint8)


def gamma_correction(img_bgr: np.ndarray, gamma: float = 1.0) -> np.ndarray:
    """
    Apply gamma correction.

    gamma < 1.0: brighten
    gamma > 1.0: darken
    """
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
    return cv2.LUT(img_bgr, table)


def white_balance(img_bgr: np.ndarray) -> np.ndarray:
    """
    Simple white balance using max RGB.
    Alternative to gray-world.
    """
    result = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
