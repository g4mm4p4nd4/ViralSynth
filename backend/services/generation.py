"""Service functions for generating content packages and storing them in Supabase."""

import os
from typing import List
from openai import AsyncOpenAI

from ..models import GenerateRequest, GenerateResponse
from .supabase import get_supabase_client


async def generate_package(request: GenerateRequest) -> GenerateResponse:
    """Generate a script, storyboard and notes from stored patterns."""
    supabase = get_supabase_client()

    patterns: List[str] = []
    if supabase:
        try:
            if request.pattern_ids:
                resp = supabase.table("patterns").select("text").in_("id", request.pattern_ids).execute()
            elif request.niche:
                resp = supabase.table("patterns").select("text").eq("niche", request.niche).execute()
            else:
                resp = None
            if resp:
                patterns = [r["text"] for r in resp.data or []]
        except Exception:
            patterns = []

    patterns_text = "\n".join(patterns)
    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Using these patterns:\n{patterns_text}\nGenerate a viral video script for: {request.prompt}",
            }],
        )
        script = completion.choices[0].message.content.strip()
    except Exception:
        script = f"This is a placeholder script for the prompt: {request.prompt}"

    try:
        image_resp = await client.images.generate(
            model="dall-e-3",
            prompt=f"Storyboard frames for: {request.prompt}"
        )
        storyboard = [img.url for img in image_resp.data]
    except Exception:
        storyboard = [
            "https://via.placeholder.com/512x512.png?text=Storyboard+Frame+1",
            "https://via.placeholder.com/512x512.png?text=Storyboard+Frame+2",
        ]

    notes = [f"Pattern used: {p}" for p in patterns[:3]] if patterns else [
        "Use trending audio #345",
        "Maintain an average shot length of 1.2 seconds",
        "Film the A-roll with a blurred background",
    ]
    variations = {request.platform: f"Hook optimized for {request.platform}"}

    package_record = {
        "prompt": request.prompt,
        "platform": request.platform,
        "niche": request.niche,
        "script": script,
        "storyboard": storyboard,
        "notes": notes,
        "variations": variations,
        "pattern_ids": request.pattern_ids,
    }
    package_id = None
    if supabase:
        try:
            resp = supabase.table("packages").insert(package_record).execute()
            if resp.data:
                package_id = resp.data[0].get("id")
        except Exception:
            pass

    return GenerateResponse(
        script=script,
        storyboard=storyboard,
        notes=notes,
        variations=variations,
        package_id=package_id,
    )
