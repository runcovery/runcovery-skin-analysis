"""Pore detection using blob detection on high-pass filtered image."""
import cv2
import numpy as np


def pores_map(img_bgr: np.ndarray, masks: dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute pore density map.

    Uses Difference of Gaussians (DoG) high-pass filter followed by
    Laplacian of Gaussian blob detection.

    Args:
        img_bgr: Input image in BGR format
        masks: Dict of region masks

    Returns:
        Normalized pore density map [0, 1]
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Create face mask
    face_mask = np.zeros(img_bgr.shape[:2], dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return np.zeros(img_bgr.shape[:2], dtype=np.float32)

    # High-pass filter using Difference of Gaussians
    blur1 = cv2.GaussianBlur(gray, (3, 3), 0.5)
    blur2 = cv2.GaussianBlur(gray, (9, 9), 2.0)
    high_pass = cv2.subtract(blur1, blur2)

    # Enhance contrast
    high_pass = cv2.normalize(high_pass, None, 0, 255, cv2.NORM_MINMAX)

    # Threshold to find dark spots (pores)
    _, pore_candidates = cv2.threshold(high_pass, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pore_candidates = 255 - pore_candidates  # Invert: pores are dark

    # Morphological operations to clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    pore_candidates = cv2.morphologyEx(pore_candidates, cv2.MORPH_OPEN, kernel)

    # Find contours (pore candidates)
    contours, _ = cv2.findContours(pore_candidates, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter by size: pores are typically 2-5 pixels in radius
    pore_map = np.zeros(gray.shape, dtype=np.uint8)
    for contour in contours:
        area = cv2.contourArea(contour)
        if 4 < area < 80:  # Pore size range in pixels
            cv2.drawContours(pore_map, [contour], -1, 255, -1)

    # Create density map by blurring detected pores
    pore_density = cv2.GaussianBlur(pore_map.astype(np.float32), (15, 15), 5)

    # Normalize to [0, 1]
    if face_mask.any():
        face_vals = pore_density[face_mask]
        p_max = face_vals.max()
        if p_max > 1e-6:
            pore_density = pore_density / p_max

    pore_density = np.clip(pore_density, 0, 1)
    pore_density[~face_mask] = 0

    return pore_density.astype(np.float32)
