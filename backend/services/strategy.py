"""Service functions for analyzing content patterns from Supabase."""

import os
import json
from typing import List
from openai import AsyncOpenAI

from ..models import Pattern, StrategyRequest, StrategyResponse
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

    return StrategyResponse(patterns=patterns, pattern_ids=pattern_ids)
