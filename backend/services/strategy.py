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
                query = supabase.table("videos").select("id, transcript, descriptors, niche").in_("id", request.video_ids)
            else:
                query = supabase.table("videos").select("id, transcript, descriptors, niche").in_("niche", request.niches)
            videos = query.execute().data or []
        except Exception:
            videos = []

    transcripts = [v.get("transcript", "") for v in videos if v.get("transcript")]
    descriptors = [v.get("descriptors", "") for v in videos if v.get("descriptors")]
    prompt = (
        "Derive 3 concise content patterns from the following transcripts and visual descriptors."
        f"\nTranscripts:\n{transcripts}\nDescriptors:\n{descriptors}"
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
            "Example pattern: 'Problem-Agitate-Solve' narrative arc",
            "Example pattern: Use of fast cuts (~0.8s) with on-screen text",
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
