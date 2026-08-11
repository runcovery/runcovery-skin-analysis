"""Redness map using CIE LAB a* channel analysis."""
import cv2
import numpy as np


def redness_map(img_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute redness map from BGR image.

    Uses CIE LAB a* channel (red-green axis).
    Higher values indicate more redness.

    Args:
        img_bgr: Input image in BGR format
        masks: Dict of region masks (forehead, cheeks, nose, chin)

    Returns:
        Normalized redness map [0, 1]
    """
    # Convert to CIE LAB
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype("float32")
    a_channel = lab[..., 1]

    # Create combined face mask
    face_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return np.zeros(img_bgr.shape[:2], dtype=np.float32)

    # Get face region values
    face_vals = a_channel[face_mask]

    # Z-score normalization within face
    mu = np.mean(face_vals)
    sigma = np.std(face_vals) + 1e-6

    z_scores = (a_channel - mu) / sigma

    # Normalize to [0, 1]
    z_min = z_scores[face_mask].min()
    z_max = z_scores[face_mask].max()

    if z_max - z_min < 1e-6:
        normalized = np.zeros_like(z_scores)
    else:
        normalized = (z_scores - z_min) / (z_max - z_min)

    # Clip to [0, 1] and mask outside face
    normalized = np.clip(normalized, 0, 1)
    normalized[~face_mask] = 0

    return normalized.astype(np.float32)
