"""Service for the Generative Strategy Core."""

from typing import Any, Dict, List

from openai import AsyncOpenAI

from . import supabase_client

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def derive_patterns(niches: List[str]) -> List[str]:
    """Analyze ingested content in Supabase and identify recurring patterns."""
    client = supabase_client.get_client()
    records: List[Dict[str, Any]] = []
    for niche in niches:
        res = client.table("ingestions").select("transcript,analysis").eq("niche", niche).execute()
        records.extend(res.data or [])
    corpus = "\n".join([r.get("transcript", "") for r in records])
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    prompt = (
        "From the following transcripts and analysis summaries, identify common content "
        "patterns or templates that make these videos successful. Return a bullet list.\n"
        + corpus
    )
    chat = await openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    return [line.strip("- ") for line in chat.choices[0].message.content.splitlines() if line]
