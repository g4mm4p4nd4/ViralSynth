"""Pydantic data models used across the ViralSynth backend."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class GenerateRequest(BaseModel):
    """Request model for generating content packages."""
    prompt: str = Field(..., description="User-provided idea or topic for the content.")
    platform: Optional[str] = Field("tiktok", description="Target platform: tiktok, instagram, or youtube.")
    niche: Optional[str] = Field(None, description="Content niche, e.g., tech, fitness, finance.")
    pattern_ids: Optional[List[int]] = Field(
        None, description="Optional Supabase pattern IDs to condition generation."
    )


class GenerateResponse(BaseModel):
    """Response model for generated content packages."""
    script: str
    storyboard: List[str]
    notes: List[str]
    variations: Dict[str, str] = Field(
        default_factory=dict,
        description="Platform-specific hook and CTA variations",
    )
    package_id: Optional[int] = Field(
        None, description="Supabase ID for the stored generated package."
    )


class VideoRecord(BaseModel):
    """Model representing an analyzed video stored in Supabase."""

    id: Optional[int] = Field(None, description="Supabase ID for the video record")
    url: Optional[str] = Field(None, description="Source URL of the video")
    niche: Optional[str] = Field(None, description="Niche associated with the video")
    provider: Optional[str] = Field(None, description="Scraping provider used")
    transcript: Optional[str] = Field(None, description="Transcribed audio text")
    pacing: Optional[float] = Field(
        None, description="Average shot length in seconds derived from scenedetect/opencv"
    )
    visual_style: Optional[str] = Field(
        None, description="Basic visual style classification such as cinematic or lo-fi"
    )
    onscreen_text: Optional[str] = Field(
        None, description="Detected on-screen text via OCR"
    )
    audio_id: Optional[str] = Field(
        None, description="Identifier for the video's audio track"
    )
    trending_audio: bool = Field(
        False, description="Flag indicating if the audio track is trending"
    )


class IngestRequest(BaseModel):
    """Request model for ingesting trending content data."""
    niches: List[str] = Field(..., description="List of content niches to ingest, e.g., ['tech', 'fitness'].")
    top_percentile: float = Field(0.05, description="Top percentile threshold (0-1) for selecting high performing content.")
    provider: Optional[str] = Field(
        None,
        description="Optional scraping provider: apify, playwright, or puppeteer.",
    )


class IngestResponse(BaseModel):
    """Response confirming that an ingest request was processed."""

    message: str
    video_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs of stored video records."
    )
    videos: List[VideoRecord] = Field(
        default_factory=list,
        description="Enriched video records stored in Supabase",
    )
    patterns: List[str] = Field(
        default_factory=list, description="Identified content patterns from ingestion."
    )
    pattern_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs of stored patterns."
    )
    generated: Optional[GenerateResponse] = Field(
        None,
        description="Generated sample content based on identified patterns.",
    )


class StrategyRequest(BaseModel):
    """Request model for analyzing content patterns."""
    niches: List[str]
    video_ids: Optional[List[int]] = Field(
        None, description="Specific Supabase video IDs to analyze."
    )


class StrategyResponse(BaseModel):
    patterns: List[str] = Field(
        default_factory=list, description="Identified successful content patterns."
    )
    pattern_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs for stored patterns."
    )
