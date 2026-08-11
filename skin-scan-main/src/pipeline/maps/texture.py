"""Texture map using local variance analysis."""
import cv2
import numpy as np
from skimage.feature import local_binary_pattern


def texture_map(img_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute texture/roughness map.

    Uses local variance and Local Binary Pattern (LBP) analysis.
    Higher values indicate rougher texture.

    Args:
        img_bgr: Input image in BGR format
        masks: Dict of region masks

    Returns:
        Normalized texture map [0, 1]
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Create face mask
    face_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return np.zeros(img_bgr.shape[:2], dtype=np.float32)

    # Method 1: Local variance (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    variance = cv2.GaussianBlur(laplacian**2, (9, 9), 0)

    # Method 2: Local Binary Pattern
    radius = 1
    n_points = 8 * radius
    lbp = local_binary_pattern(gray, n_points, radius, method="uniform")

    # Compute LBP variance in local patches
    lbp_var = cv2.GaussianBlur(lbp.astype(np.float32), (9, 9), 0)

    # Combine both metrics
    # Normalize each first
    var_norm = variance / (variance[face_mask].max() + 1e-6)
    lbp_norm = lbp_var / (lbp_var[face_mask].max() + 1e-6)

    # Weighted combination
    texture = 0.6 * var_norm + 0.4 * lbp_norm

    # Normalize to [0, 1]
    if face_mask.any():
        face_vals = texture[face_mask]
        t_min, t_max = face_vals.min(), face_vals.max()
        if t_max - t_min > 1e-6:
            texture = (texture - t_min) / (t_max - t_min)

    texture = np.clip(texture, 0, 1)
    texture[~face_mask] = 0

    return texture.astype(np.float32)
