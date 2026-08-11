"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel


class ScanResponse(BaseModel):
    """Response schema for skin scan analysis."""

    indices: dict[str, int]  # relative feature-intensity indices from 0 to 100
    condition_scores: dict[str, int]  # relative condition scores; higher is better
    overlays: dict[str, str]  # base64 encoded PNG images
    regions: list[str]


class HealthResponse(BaseModel):
    """Health check response."""

    ok: bool
