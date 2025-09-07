"""Service functions for analyzing content patterns from Supabase."""

import os
from typing import List
from openai import AsyncOpenAI

from ..models import StrategyRequest, StrategyResponse
from .supabase import get_supabase_client


async def derive_patterns(request: StrategyRequest) -> StrategyResponse:
    """Fetch transcripts/descriptors from Supabase and extract patterns via GPT."""
    supabase = get_supabase_client()
    videos = []
    if supabase:
        try:
            if request.video_ids:
                query = supabase.table("videos").select(
                    "id, transcript, pacing, visual_style, onscreen_text, trending_audio, niche"
                ).in_("id", request.video_ids)
            else:
                query = supabase.table("videos").select(
                    "id, transcript, pacing, visual_style, onscreen_text, trending_audio, niche"
                ).in_("niche", request.niches)
            videos = query.execute().data or []
        except Exception:
            videos = []

    transcripts = [v.get("transcript", "") for v in videos if v.get("transcript")]
    pacing = [v.get("pacing") for v in videos if v.get("pacing")]
    styles = [v.get("visual_style") for v in videos if v.get("visual_style")]
    texts = [v.get("onscreen_text") for v in videos if v.get("onscreen_text")]
    audios = [v.get("trending_audio") for v in videos]

    prompt = (
        "You are an expert content strategist. From the following video data, derive concise patterns for hooks, core value loops, "
        "narrative arcs, visual formulas and CTAs."\
        f"\nTranscripts: {transcripts}"\
        f"\nPacing: {pacing}"\
        f"\nVisual Style: {styles}"\
        f"\nOn-screen Text: {texts}"\
        f"\nTrending Audio Flags: {audios}"
    )

    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_patterns = completion.choices[0].message.content.split("\n")
        patterns = [p.strip("- ") for p in raw_patterns if p.strip()]
    except Exception:
        patterns = [
            "Hook pattern: start with a bold question and match to trending audio",
            "Visual formula: lo-fi shots with high contrast text overlays",
            "CTA pattern: direct ask in final shot with on-screen text",
        ]

    pattern_ids: List[int] = []
    if supabase and patterns:
        rows = [{"niche": request.niches[0] if request.niches else None, "text": p} for p in patterns]
        try:
            resp = supabase.table("patterns").insert(rows).execute()
            pattern_ids = [r.get("id") for r in resp.data or []]
        except Exception:
            pass

    return StrategyResponse(patterns=patterns, pattern_ids=pattern_ids)
