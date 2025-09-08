"""Pydantic data models used across the ViralSynth backend."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class TrendingAudio(BaseModel):
    """Representation of an audio track ranked by usage."""

    audio_id: str = Field(..., description="Identifier for the audio track")
    count: int = Field(..., description="Number of videos using this audio")
    url: Optional[str] = Field(None, description="Source link for the audio")


class Pattern(BaseModel):
    """Structured template extracted from analyzed videos."""

    id: Optional[int] = Field(None, description="Supabase ID of the pattern")
    hook: str = Field(..., description="Opening hook used to grab attention")
    core_value_loop: str = Field(..., description="Main value delivery loop")
    narrative_arc: str = Field(..., description="Narrative arc or storyline")
    visual_formula: str = Field(..., description="Visual style or formula")
    cta: str = Field(..., description="Call to action at the end")


class GenerateRequest(BaseModel):
    """Request model for generating content packages."""

    prompt: str = Field(..., description="User-provided idea or topic for the content.")
    platform: Optional[str] = Field("tiktok", description="Target platform: tiktok, instagram, or youtube.")
    niche: Optional[str] = Field(None, description="Content niche, e.g., tech, fitness, finance.")
    pattern_ids: Optional[List[int]] = Field(
        None, description="Optional Supabase pattern IDs to condition generation.",
    )


class PlatformVariation(BaseModel):
    """Hook and CTA pair tailored to a platform."""

    hook: str
    cta: str


class GenerateResponse(BaseModel):
    """Response model for generated content packages."""

    script: str
    storyboard: List[str]
    notes: List[str]
    variations: Dict[str, PlatformVariation] = Field(
        default_factory=dict,
        description="Platform-specific hook and CTA variations",
    )
    audio_id: Optional[str] = Field(
        None, description="Trending audio identifier used for generation",
    )
    audio_url: Optional[str] = Field(
        None, description="Source link for the selected audio",
    )
    package_id: Optional[int] = Field(
        None, description="Supabase ID for the stored generated package.",
    )


class VideoRecord(BaseModel):
    """Model representing an analyzed video stored in Supabase."""

    id: Optional[int] = Field(None, description="Supabase ID for the video record")
    url: Optional[str] = Field(None, description="Source URL of the video")
    niche: Optional[str] = Field(None, description="Niche associated with the video")
    provider: Optional[str] = Field(None, description="Scraping provider used")
    transcript: Optional[str] = Field(None, description="Transcribed audio text")
    pacing: Optional[float] = Field(
        None, description="Average shot length in seconds derived from scenedetect/opencv",
    )
    visual_style: Optional[str] = Field(
        None, description="Basic visual style classification such as cinematic or lo-fi",
    )
    onscreen_text: Optional[str] = Field(
        None, description="Detected on-screen text via OCR",
    )
    audio_id: Optional[str] = Field(
        None, description="Identifier for the video's audio track",
    )
    audio_url: Optional[str] = Field(
        None, description="Source link for the video's audio track",
    )
    trending_audio: bool = Field(
        False, description="Flag indicating if the audio track is trending",
    )


class IngestRequest(BaseModel):
    """Request model for ingesting trending content data."""

    niches: List[str] = Field(..., description="List of content niches to ingest, e.g., ['tech', 'fitness'].")
    top_percentile: float = Field(
        0.05, description="Top percentile threshold (0-1) for selecting high performing content.",
    )
    provider: Optional[str] = Field(
        None,
        description="Optional scraping provider: apify, playwright, or puppeteer.",
    )


class IngestResponse(BaseModel):
    """Response confirming that an ingest request was processed."""

    message: str
    video_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs of stored video records.",
    )
    videos: List[VideoRecord] = Field(
        default_factory=list,
        description="Enriched video records stored in Supabase",
    )
    patterns: List[Pattern] = Field(
        default_factory=list, description="Identified content patterns from ingestion.",
    )
    pattern_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs of stored patterns.",
    )
    trending_audios: List[TrendingAudio] = Field(
        default_factory=list, description="Ranked trending audio tracks across dataset",
    )
    generated: Optional[GenerateResponse] = Field(
        None,
        description="Generated sample content based on identified patterns.",
    )


class StrategyRequest(BaseModel):
    """Request model for analyzing content patterns."""

    niches: List[str]
    video_ids: Optional[List[int]] = Field(
        None, description="Specific Supabase video IDs to analyze.",
    )


class StrategyResponse(BaseModel):
    patterns: List[Pattern] = Field(
        default_factory=list, description="Identified successful content patterns.",
    )
    pattern_ids: List[int] = Field(
        default_factory=list, description="Supabase IDs for stored patterns.",
    )
