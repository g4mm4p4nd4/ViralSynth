"""Utilities for selecting top audio and patterns for generation."""

import os
from typing import List, Optional, Tuple

from ..models import Pattern, TrendingAudio
from .supabase import get_supabase_client
from .ingestion import get_trending_audio


async def choose_assets(
    niche: Optional[str] = None, pattern_ids: Optional[List[int]] = None
) -> Tuple[Optional[TrendingAudio], List[Pattern]]:
    """Select a trending audio clip and high-performing patterns.

    If ``pattern_ids`` are provided, those specific patterns are retrieved. Otherwise,
    the top patterns for the niche are returned ordered by engagement score.
    """

    supabase = get_supabase_client()
    patterns: List[Pattern] = []
    limit = int(os.environ.get("PATTERN_CHOOSE_LIMIT", 5))
    if supabase:
        try:
            query = supabase.table("patterns").select(
                "id,hook,core_value_loop,narrative_arc,visual_formula,cta,prevalence,engagement_score"
            )
            if pattern_ids:
                query = query.in_("id", pattern_ids)
            elif niche:
                query = (
                    query.eq("niche", niche)
                    .order("engagement_score", desc=True)
                    .limit(limit)
                )
            resp = query.execute()
            patterns = [Pattern(**r) for r in resp.data or []]
        except Exception:
            patterns = []

    if not patterns:
        # Fallback pattern when database is unavailable
        patterns = [
            Pattern(
                hook="Ask a bold question over trending audio",
                core_value_loop="Provide three rapid tips",
                narrative_arc="Problem-solution reveal",
                visual_formula="Lo-fi selfie clips with captions",
                cta="Follow for more hacks",
            )
        ]

    audio_obj: Optional[TrendingAudio] = None
    try:
        audio_list = await get_trending_audio(niche=niche, limit=1)
        audio_obj = audio_list[0] if audio_list else None
    except Exception:
        audio_obj = None

    return audio_obj, patterns
