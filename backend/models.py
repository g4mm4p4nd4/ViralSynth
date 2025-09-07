"""Pydantic data models used across the ViralSynth backend."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class IngestRequest(BaseModel):
    """Request model for ingesting trending content data."""
    niches: List[str] = Field(..., description="List of content niches to ingest, e.g., ['tech', 'fitness'].")
    top_percentile: float = Field(0.05, description="Top percentile threshold (0-1) for selecting high performing content.")
    provider: Optional[str] = Field(
        None,
        description="Optional scraping provider: apify, playwright, or puppeteer."
    )


class IngestResponse(BaseModel):
    """Response confirming that an ingest request was received."""
    message: str


class StrategyRequest(BaseModel):
    """Request model for analyzing content patterns."""
    niches: List[str]


class StrategyResponse(BaseModel):
    patterns: List[str] = Field(default_factory=list, description="Identified successful content patterns.")


class GenerateRequest(BaseModel):
    """Request model for generating content packages."""
    prompt: str = Field(..., description="User-provided idea or topic for the content.")
    platform: Optional[str] = Field("tiktok", description="Target platform: tiktok, instagram, or youtube.")
    niche: Optional[str] = Field(None, description="Content niche, e.g., tech, fitness, finance.")


class GenerateResponse(BaseModel):
    """Response model for generated content packages."""
    script: str
    storyboard: List[str]
    notes: List[str]
    variations: Dict[str, str] = Field(
        default_factory=dict,
        description="Platform-specific hook and CTA variations",
    )
