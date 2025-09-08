"""Service functions for generating content packages and storing them in Supabase."""

import os
import json
from typing import Dict, List
from openai import AsyncOpenAI

from ..models import (
    GenerateRequest,
    GenerateResponse,
    Pattern,
    PlatformVariation,
)
from .supabase import get_supabase_client
from .ingestion import get_trending_audio


async def generate_package(request: GenerateRequest) -> GenerateResponse:
    """Generate a script, storyboard and notes from stored patterns."""
    supabase = get_supabase_client()

    patterns: List[Pattern] = []
    trending_audio = None
    audio_url = None
    pacing_hint = None
    style_hint = None
    pattern_ids_used: List[int] = []
    if supabase:
        try:
            if request.pattern_ids:
                resp = supabase.table("patterns").select(
                    "id,hook,core_value_loop,narrative_arc,visual_formula,cta"
                ).in_("id", request.pattern_ids).execute()
            elif request.niche:
                resp = supabase.table("patterns").select(
                    "id,hook,core_value_loop,narrative_arc,visual_formula,cta"
                ).eq("niche", request.niche).execute()
            else:
                resp = None
            if resp:
                patterns = [Pattern(**r) for r in resp.data or []]
                pattern_ids_used = [p.id for p in patterns if p.id]
            else:
                pattern_ids_used = request.pattern_ids or []

            audio_list = await get_trending_audio(request.niche, 1)
            if audio_list:
                trending_audio = audio_list[0].audio_id
                audio_url = audio_list[0].url
                video_resp = (
                    supabase.table("videos")
                    .select("pacing, visual_style")
                    .eq("audio_id", trending_audio)
                    .limit(1)
                    .execute()
                )
                if video_resp.data:
                    pacing_hint = video_resp.data[0].get("pacing")
                    style_hint = video_resp.data[0].get("visual_style")
        except Exception:
            patterns = []

    pattern_lines = [
        f"Hook: {p.hook}; Value: {p.core_value_loop}; Narrative: {p.narrative_arc}; Visual: {p.visual_formula}; CTA: {p.cta}"
        for p in patterns
    ]
    patterns_text = "\n".join(pattern_lines)
    style_context = (
        f"Trending audio: {trending_audio}. " if trending_audio else ""
    ) + (
        f"Pacing target: {pacing_hint} sec per shot. " if pacing_hint else ""
    ) + (f"Visual style: {style_hint}." if style_hint else "")

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        completion = await client.chat.completions.create(
            model=os.environ.get("GENERATION_MODEL", "gpt-4o-mini"),
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
    variations: Dict[str, PlatformVariation] = {}
    try:
        var_prompt = (
            "Provide platform-specific hooks and CTAs for TikTok, Instagram and YouTube."
            f"\nScript: {script}\nReturn JSON object mapping platform to hook and cta."
        )
        var_completion = await client.chat.completions.create(
            model=os.environ.get("GENERATION_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": var_prompt}],
        )
        var_data = json.loads(var_completion.choices[0].message.content)
        for platform, data in var_data.items():
            variations[platform] = PlatformVariation(**data)
    except Exception:
        variations[request.platform] = PlatformVariation(
            hook=f"Hook optimized for {request.platform}",
            cta=f"CTA for {request.platform}",
        )

    package_record = {
        "prompt": request.prompt,
        "platform": request.platform,
        "niche": request.niche,
        "script": script,
        "storyboard": storyboard,
        "notes": notes,
        "variations": {k: v.dict() for k, v in variations.items()},
        "pattern_ids": pattern_ids_used,
        "audio_id": trending_audio,
        "audio_url": audio_url,
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
        audio_id=trending_audio,
        audio_url=audio_url,
        package_id=package_id,
        pattern_ids=pattern_ids_used,
    )
