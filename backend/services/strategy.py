"""Service functions for analyzing content patterns from Supabase."""

import os
from typing import List, Optional

from ..models import Pattern, StrategyRequest, StrategyResponse
from .supabase import get_supabase_client
from .pattern_miner import mine_patterns_from_records


async def derive_patterns(request: StrategyRequest) -> StrategyResponse:
    """Fetch video descriptors from Supabase and mine recurring patterns."""
    supabase = get_supabase_client()
    videos = []
    if supabase:
        try:
            if request.video_ids:
                query = supabase.table("videos").select(
                    "id, transcript, pacing, visual_style, onscreen_text, trending_audio, niche, likes, comments"
                ).in_("id", request.video_ids)
            else:
                query = supabase.table("videos").select(
                    "id, transcript, pacing, visual_style, onscreen_text, trending_audio, niche, likes, comments"
                ).in_("niche", request.niches)
            limit = int(os.environ.get("PATTERN_ANALYSIS_LIMIT", 50))
            videos = query.limit(limit).execute().data or []
        except Exception:
            videos = []

    niche = request.niches[0] if request.niches else "general"
    patterns: List[Pattern] = mine_patterns_from_records(videos, niche)

    pattern_ids: List[int] = []
    if supabase and patterns:
        rows = [
            {
                "niche": p.niche,
                "hook": p.hook,
                "core_value_loop": p.core_value_loop,
                "narrative_arc": p.narrative_arc,
                "visual_formula": p.visual_formula,
                "cta": p.cta,
                "prevalence": p.prevalence,
                "engagement_score": p.engagement_score,
            }
            for p in patterns
        ]
        try:
            resp = supabase.table("patterns").insert(rows).execute()
            if resp.data:
                for pat, row in zip(patterns, resp.data):
                    pat.id = row.get("id")
                pattern_ids = [r.get("id") for r in resp.data]
        except Exception:
            pass

    from .ingestion import get_trending_audio

    trending_audios = await get_trending_audio(niche=niche)
    return StrategyResponse(
        patterns=patterns, pattern_ids=pattern_ids, trending_audios=trending_audios
    )


async def fetch_patterns(niche: Optional[str] = None, limit: int = 10) -> List[Pattern]:
    """Retrieve stored patterns from Supabase ordered by prevalence."""

    supabase = get_supabase_client()
    if not supabase:
        return []
    try:
        query = supabase.table("patterns").select(
            "id,niche,hook,core_value_loop,narrative_arc,visual_formula,cta,prevalence,engagement_score"
        )
        if niche:
            query = query.eq("niche", niche)
        resp = query.order("prevalence", desc=True).limit(limit).execute()
        return [Pattern(**r) for r in (resp.data or [])]
    except Exception:
        return []
