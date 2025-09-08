"""Service functions for analyzing content patterns from Supabase."""

import os
import json
from typing import List, Optional
from openai import AsyncOpenAI

from ..models import Pattern, StrategyRequest, StrategyResponse
from .supabase import get_supabase_client
from .ingestion import get_trending_audio


async def derive_patterns(request: StrategyRequest) -> StrategyResponse:
    """Fetch transcripts/descriptors from Supabase and extract patterns via GPT."""
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

    transcripts = [v.get("transcript", "") for v in videos if v.get("transcript")]
    pacing = [v.get("pacing") for v in videos if v.get("pacing")]
    styles = [v.get("visual_style") for v in videos if v.get("visual_style")]
    texts = [v.get("onscreen_text") for v in videos if v.get("onscreen_text")]
    audios = [v.get("trending_audio") for v in videos]
    engagements = [
        (v.get("likes") or 0) + (v.get("comments") or 0) for v in videos
    ]
    avg_engagement = sum(engagements) / len(engagements) if engagements else 0.0
    prevalence = float(len(videos)) if videos else 0.0

    prompt = (
        "From the following video data derive recurring patterns. Return JSON with a list of objects each containing"
        " keys: hook, core_value_loop, narrative_arc, visual_formula, cta."\
        f"\nTranscripts: {transcripts}"\
        f"\nPacing: {pacing}"\
        f"\nVisual Style: {styles}"\
        f"\nOn-screen Text: {texts}"\
    )

    patterns: List[Pattern] = []
    try:
        client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        completion = await client.chat.completions.create(
            model=os.environ.get("PATTERN_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
        )
        data = json.loads(completion.choices[0].message.content)
        for p in data.get("patterns", []):
            patterns.append(Pattern(**p))
    except Exception:
        patterns = [
            Pattern(
                hook="Ask a bold question over trending audio",
                core_value_loop="Provide three rapid tips",
                narrative_arc="Problem-solution reveal",
                visual_formula="Lo-fi selfie clips with captions",
                cta="Follow for more hacks",
            )
        ]

    for p in patterns:
        p.prevalence = prevalence
        p.engagement_score = avg_engagement

    pattern_ids: List[int] = []
    if supabase and patterns:
        rows = [
            {
                "niche": request.niches[0] if request.niches else None,
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

    niche = request.niches[0] if request.niches else None
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
            "id,hook,core_value_loop,narrative_arc,visual_formula,cta,prevalence,engagement_score"
        )
        if niche:
            query = query.eq("niche", niche)
        resp = query.order("prevalence", desc=True).limit(limit).execute()
        return [Pattern(**r) for r in (resp.data or [])]
    except Exception:
        return []
