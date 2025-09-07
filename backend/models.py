from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class IngestRequest(BaseModel):
    niches: List[str] = Field(..., description="List of content niches to ingest, e.g., ['tech', 'fitness'].")
    top_percentile: float = Field(0.05, description="Top percentile threshold (0-1) for selecting high performing content.")

class IngestResponse(BaseModel):
    message: str
    items: List[Dict[str, Any]] = Field(default_factory=list, description="Enriched video metadata and analysis")

class StrategyRequest(BaseModel):
    niches: List[str]

class StrategyResponse(BaseModel):
    patterns: List[str] = Field(default_factory=list, description="Identified successful content patterns.")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="User-provided idea or topic for the content.")
    platform: Optional[str] = Field("tiktok", description="Target platform: tiktok, instagram, or youtube.")
    niche: Optional[str] = Field(None, description="Content niche, e.g., tech, fitness, finance.")

class GenerateResponse(BaseModel):
    script: str
    storyboard: List[str]
    notes: List[str]
    variations: Dict[str, str] = Field(default_factory=dict, description="Platform-specific hook and CTA variations")
