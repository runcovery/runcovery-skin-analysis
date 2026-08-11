"""Pipeline composition - orchestrates the full skin scan analysis."""
import numpy as np
from typing import Dict

from .preprocess import preprocess
from .face_mesh import FaceMeshDetector, make_region_masks
from .maps.redness import redness_map
from .maps.oiliness import oiliness_map
from .maps.texture import texture_map
from .maps.pores import pores_map
from .maps.blemishes import blemish_map
from .maps.hydration import hydration_map
from .maps.pigment import pigment_map
from .visualize import generate_all_overlays
from ..app.utils_io import encode_png_base64


def intensity_index_from_map(map_data: np.ndarray, masks: dict[str, np.ndarray]) -> int:
    """
    Compute a relative feature-intensity index from a normalized map.

    Args:
        map_data: Normalized map [0, 1]
        masks: Region masks

    Returns:
        Integer feature-intensity index [0, 100]
    """
    # Create combined face mask
    face_mask = np.zeros(map_data.shape, dtype=bool)
    for region_mask in masks.values():
        face_mask |= region_mask > 0

    if not face_mask.any():
        return 0

    # Express the normalized face-map average as a relative 0-100 index.
    # This is a per-image feature intensity, not a percentage, percentile,
    # diagnosis, or calibrated skin-health score.
    face_vals = map_data[face_mask]
    normalized_intensity = float(np.clip(np.mean(face_vals), 0.0, 1.0))
    return max(0, min(100, round(normalized_intensity * 100)))


INVERTED_CONDITION_CATEGORIES = frozenset({
    "redness",
    "oiliness",
    "texture",
    "pores",
    "blemishes",
    "pigment",
})


def condition_scores_from_indices(indices: dict[str, int]) -> dict[str, int]:
    """Convert feature intensities to relative condition scores where higher is better."""
    expected_categories = INVERTED_CONDITION_CATEGORIES | {"hydration"}
    unknown_categories = set(indices) - expected_categories
    if unknown_categories:
        names = ", ".join(sorted(unknown_categories))
        raise ValueError(f"Condition-score direction is not defined for: {names}")

    scores = {}
    for name, index in indices.items():
        bounded_index = max(0, min(100, index))
        scores[name] = (
            100 - bounded_index
            if name in INVERTED_CONDITION_CATEGORIES
            else bounded_index
        )
    return scores


def run_scan(img: np.ndarray) -> Dict:
    """
    Run complete skin scan pipeline.

    Args:
        img: Input BGR image

    Returns:
        Dict with keys:
        - indices: dict[str, int] (relative feature intensity, 0-100)
        - condition_scores: dict[str, int] (higher is better, 0-100)
        - overlays: dict[str, str] (base64 PNG)
        - regions: list[str]
    """
    # Preprocess
    img_processed = preprocess(img, max_size=1024)

    # Detect face landmarks
    detector = FaceMeshDetector()
    landmarks = detector.detect(img_processed)

    if landmarks is None:
        raise ValueError("No face detected in image")

    # Create region masks
    masks = make_region_masks(landmarks, img_processed.shape)

    if not masks:
        raise ValueError("Could not create region masks from landmarks")

    # Run all map analyses
    maps = {
        "redness": redness_map(img_processed, masks),
        "oiliness": oiliness_map(img_processed, masks),
        "texture": texture_map(img_processed, masks),
        "pores": pores_map(img_processed, masks),
        "blemishes": blemish_map(img_processed, masks),
        "hydration": hydration_map(img_processed, masks),
        "pigment": pigment_map(img_processed, masks),
    }

    # Compute relative feature-intensity indices
    indices = {name: intensity_index_from_map(map_data, masks) for name, map_data in maps.items()}

    # Convert to relative condition scores with a consistent higher-is-better direction
    condition_scores = condition_scores_from_indices(indices)

    # Generate overlay visualizations
    overlay_images = generate_all_overlays(maps, alpha=0.6)

    # Convert overlays to base64 PNG
    overlays = {
        name: encode_png_base64(overlay_rgba)
        for name, overlay_rgba in overlay_images.items()
    }

    # Get region names
    regions = list(masks.keys())

    return {
        "indices": indices,
        "condition_scores": condition_scores,
        "overlays": overlays,
        "regions": regions,
    }
