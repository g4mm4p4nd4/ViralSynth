"""Endpoints exposing trending audio rankings."""

from fastapi import APIRouter
from typing import Optional

from ..models import TrendingAudio
from ..services.ingestion import get_trending_audio

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.get("/trending")
async def trending_audio(
    niche: Optional[str] = None,
    limit: int = 10,
    date: Optional[str] = None,
):
    """Return top trending audio clips optionally filtered by niche and date."""
    return await get_trending_audio(niche=niche, limit=limit, ranking_date=date)
