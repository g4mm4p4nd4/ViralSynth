"""Endpoints exposing trending audio rankings."""

from fastapi import APIRouter
from typing import List, Optional

from ..models import TrendingAudio
from ..services.ingestion import get_trending_audio

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/trending", response_model=List[TrendingAudio])
async def trending_audio(niche: Optional[str] = None, limit: int = 10) -> List[TrendingAudio]:
    """Return top trending audio clips optionally filtered by niche."""
    return await get_trending_audio(niche=niche, limit=limit)
