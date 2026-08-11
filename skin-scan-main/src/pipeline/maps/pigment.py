"""Pigmentation map via melanin/brown mask detection."""
import cv2
import numpy as np


def pigment_map(img_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute pigmentation map.

    Detects melanin-rich areas (hyperpigmentation, age spots, etc.)
    using brown color detection in LAB color space.

    Args:
        img_bgr: Input image in BGR format
        masks: Dict of region masks

    Returns:
        Normalized pigmentation map [0, 1]
    """
    # Convert to LAB color space
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_channel = lab[..., 0].astype(np.float32)
    a_channel = lab[..., 1].astype(np.float32)
    b_channel = lab[..., 2].astype(np.float32)

    # Create face mask
    face_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return np.zeros(img_bgr.shape[:2], dtype=np.float32)

    # Brown/melanin detection criteria:
    # 1. Lower L* (darker)
    # 2. Positive b* (yellowish, toward brown)
    # 3. Slightly positive a* (reddish component)

    # Normalize within face region
    l_face = l_channel[face_mask]
    l_mean = np.mean(l_face)
    l_std = np.std(l_face) + 1e-6

    # Detect darker areas (potential pigmentation)
    darkness_score = (l_mean - l_channel) / l_std
    darkness_score = np.clip(darkness_score, 0, None)

    # Brown color detection via b* channel (yellow-blue axis)
    # Brown has positive b* (yellow)
    b_normalized = (b_channel - 128) / 128  # Center and normalize
    brown_yellow = np.clip(b_normalized, 0, 1)

    # Slight redness (a* channel)
    a_normalized = (a_channel - 128) / 128
    brown_red = np.clip(a_normalized * 0.5, 0, 1)  # Less weight on red

    # Combine features
    pigment = darkness_score * 0.5 + brown_yellow * 0.3 + brown_red * 0.2

    # Normalize to [0, 1]
    if face_mask.any():
        face_vals = pigment[face_mask]
        p_min, p_max = face_vals.min(), face_vals.max()
        if p_max - p_min > 1e-6:
            pigment = (pigment - p_min) / (p_max - p_min)

    pigment = np.clip(pigment, 0, 1)
    pigment[~face_mask] = 0

    # Optional: Filter out very small spots (freckles) if desired
    # For now, keep all pigmentation

    return pigment.astype(np.float32)
