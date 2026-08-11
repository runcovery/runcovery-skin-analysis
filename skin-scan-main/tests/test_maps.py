"""Tests for skin analysis map algorithms."""
import pytest
import numpy as np
import cv2

from src.pipeline.maps.redness import redness_map
from src.pipeline.maps.oiliness import oiliness_map
from src.pipeline.maps.texture import texture_map
from src.pipeline.maps.pores import pores_map
from src.pipeline.maps.blemishes import blemish_map
from src.pipeline.maps.hydration import hydration_map
from src.pipeline.maps.pigment import pigment_map
from src.pipeline.compose import condition_scores_from_indices, intensity_index_from_map


@pytest.fixture
def sample_image():
    """Create a synthetic test image."""
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    return img


@pytest.fixture
def sample_masks():
    """Create sample region masks."""
    h, w = 512, 512
    masks = {
        "forehead": np.zeros((h, w), dtype=np.uint8),
        "cheeks": np.zeros((h, w), dtype=np.uint8),
        "nose": np.zeros((h, w), dtype=np.uint8),
        "chin": np.zeros((h, w), dtype=np.uint8),
    }

    # Create circular regions
    center = (w // 2, h // 2)
    cv2.circle(masks["forehead"], (center[0], h // 4), 50, 255, -1)
    cv2.circle(masks["cheeks"], center, 80, 255, -1)
    cv2.circle(masks["nose"], (center[0], center[1] + 20), 40, 255, -1)
    cv2.circle(masks["chin"], (center[0], 3 * h // 4), 60, 255, -1)

    return masks


def test_redness_map(sample_image, sample_masks):
    """Test redness map generation."""
    result = redness_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_oiliness_map(sample_image, sample_masks):
    """Test oiliness map generation."""
    result = oiliness_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_texture_map(sample_image, sample_masks):
    """Test texture map generation."""
    result = texture_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_pores_map(sample_image, sample_masks):
    """Test pore detection map."""
    result = pores_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_blemish_map(sample_image, sample_masks):
    """Test blemish detection map."""
    result = blemish_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_hydration_map(sample_image, sample_masks):
    """Test hydration map generation."""
    result = hydration_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_hydration_smooth_surface_scores_higher_than_noisy_surface():
    """A smooth, even image should have a higher hydration proxy than noise."""
    shape = (128, 128)
    masks = {"face": np.full(shape, 255, dtype=np.uint8)}
    smooth = np.full((*shape, 3), 160, dtype=np.uint8)
    rng = np.random.default_rng(42)
    noisy = np.clip(
        160 + rng.normal(0, 30, (*shape, 3)),
        0,
        255,
    ).astype(np.uint8)

    smooth_hydration = hydration_map(smooth, masks).mean()
    noisy_hydration = hydration_map(noisy, masks).mean()

    assert smooth_hydration == pytest.approx(1.0)
    assert noisy_hydration < smooth_hydration


def test_hydration_empty_masks_return_zero(sample_image):
    """No detected face region means no hydration proxy measurement."""
    assert np.all(hydration_map(sample_image, {}) == 0.0)

def test_pigment_map(sample_image, sample_masks):
    """Test pigmentation map."""
    result = pigment_map(sample_image, sample_masks)

    assert result.shape == sample_image.shape[:2]
    assert result.dtype == np.float32
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_empty_masks(sample_image):
    """Test maps with empty masks."""
    empty_masks = {}

    result = redness_map(sample_image, empty_masks)
    assert np.all(result == 0.0)

@pytest.mark.parametrize(
    ("normalized_value", "expected_index"),
    [
        (0.0, 0),
        (0.01, 1),
        (0.39, 39),
        (0.999, 100),
        (1.0, 100),
    ],
)
def test_intensity_index_from_map_uses_0_to_100_scale(normalized_value, expected_index):
    """Convert normalized map averages to relative indices from 0 to 100."""
    map_data = np.full((2, 2), normalized_value, dtype=np.float32)
    masks = {"face": np.full((2, 2), 255, dtype=np.uint8)}

    assert intensity_index_from_map(map_data, masks) == expected_index


def test_intensity_index_from_map_empty_mask_returns_zero():
    """An empty detected region has no measurable feature intensity."""
    map_data = np.ones((2, 2), dtype=np.float32)

    assert intensity_index_from_map(map_data, {}) == 0

def test_condition_scores_use_consistent_higher_is_better_direction():
    """Invert concern intensities while preserving the hydration direction."""
    indices = {
        "redness": 39,
        "oiliness": 24,
        "texture": 11,
        "pores": 0,
        "blemishes": 21,
        "hydration": 16,
        "pigment": 15,
    }

    assert condition_scores_from_indices(indices) == {
        "redness": 61,
        "oiliness": 76,
        "texture": 89,
        "pores": 100,
        "blemishes": 79,
        "hydration": 16,
        "pigment": 85,
    }


def test_condition_scores_reject_unknown_direction():
    """Require an explicit direction decision whenever a category is added."""
    with pytest.raises(ValueError, match="wrinkles"):
        condition_scores_from_indices({"wrinkles": 50})
