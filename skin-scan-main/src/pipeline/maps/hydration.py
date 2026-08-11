"""Hydration map - proxy via texture and specular response."""
import cv2
import numpy as np


def _robust_normalize(
    metric: np.ndarray,
    face_mask: np.ndarray,
    percentile: float = 95.0,
) -> np.ndarray:
    """Scale a non-negative feature by a robust face-region upper bound."""
    upper = float(np.percentile(metric[face_mask], percentile))
    if upper <= 1e-6:
        return np.zeros(metric.shape, dtype=np.float32)
    return np.clip(metric / upper, 0.0, 1.0).astype(np.float32)


def hydration_map(img_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """
    Estimate a hydration-looking map from image texture (proxy metric).

    The algorithm first estimates dryness from three non-negative features:
    local roughness, brightness unevenness, and gradient strength. Each feature
    is scaled by its 95th percentile inside the detected face to avoid the
    extreme-value distortion caused by reciprocal/max normalization. The final
    hydration proxy is ``1 - dryness``.

    This is not a direct measurement such as transepidermal water loss (TEWL).

    Args:
        img_bgr: Input image in BGR format
        masks: Dict of region masks

    Returns:
        Normalized hydration-looking map [0, 1] (higher = smoother/more even)
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    face_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return np.zeros(img_bgr.shape[:2], dtype=np.float32)

    # Feature 1: local high-frequency roughness.
    laplacian = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    roughness = cv2.GaussianBlur(np.abs(laplacian), (9, 9), 0)
    roughness_norm = _robust_normalize(roughness, face_mask)

    # Feature 2: local brightness unevenness.
    value = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)[..., 2].astype(np.float32)
    value_mean = cv2.GaussianBlur(value, (15, 15), 0)
    value_variance = cv2.GaussianBlur((value - value_mean) ** 2, (15, 15), 0)
    brightness_std = np.sqrt(np.maximum(value_variance, 0.0))
    unevenness_norm = _robust_normalize(brightness_std, face_mask)

    # Feature 3: local edge strength, smoothed so isolated pixels do not dominate.
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.GaussianBlur(np.sqrt(grad_x**2 + grad_y**2), (9, 9), 0)
    gradient_norm = _robust_normalize(gradient, face_mask)

    dryness = (
        0.4 * roughness_norm
        + 0.3 * unevenness_norm
        + 0.3 * gradient_norm
    )
    hydration = 1.0 - np.clip(dryness, 0.0, 1.0)
    hydration[~face_mask] = 0.0
    return hydration.astype(np.float32)
