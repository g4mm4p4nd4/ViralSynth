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
    trending_audio = None
    pacing_hint = None
    style_hint = None
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

            audio_resp = (
                supabase.table("videos")
                .select("audio_id, pacing, visual_style")
                .eq("trending_audio", True)
                .limit(1)
                .execute()
            )
            if audio_resp.data:
                trending_audio = audio_resp.data[0].get("audio_id")
                pacing_hint = audio_resp.data[0].get("pacing")
                style_hint = audio_resp.data[0].get("visual_style")
        except Exception:
            patterns = []

    patterns_text = "\n".join(patterns)
    style_context = (
        f"Trending audio: {trending_audio}. " if trending_audio else ""
    ) + (
        f"Pacing target: {pacing_hint} sec per shot. " if pacing_hint else ""
    ) + (f"Visual style: {style_hint}." if style_hint else "")

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        completion = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Using these patterns:\n{patterns_text}\n{style_context}\nGenerate a viral video script for: {request.prompt}",
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

    notes = [f"Pattern used: {p}" for p in patterns[:3]] if patterns else []
    if trending_audio:
        notes.append(f"Use trending audio {trending_audio}")
    if pacing_hint:
        notes.append(f"Aim for average shot length of {pacing_hint:.2f}s")
    if style_hint:
        notes.append(f"Maintain {style_hint} visual style")
    if not notes:
        notes = [
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
