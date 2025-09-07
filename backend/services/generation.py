"""Utilities for generating scripts, storyboards and production notes."""

import os
from typing import Any, Dict, List

from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DALL_E_API_KEY = os.getenv("DALL_E_API_KEY") or OPENAI_API_KEY
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def generate_script(prompt: str, niche: str | None = None) -> str:
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    messages = [
        {
            "role": "system",
            "content": "You write short-form video scripts with hooks and CTAs.",
        },
        {"role": "user", "content": f"Topic: {prompt}\nNiche: {niche or 'general'}"},
    ]
    chat = await openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )
    return chat.choices[0].message.content.strip()


async def generate_storyboard(prompt: str) -> List[str]:
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    images = []
    for i in range(2):
        img = await openai_client.images.generate(
            model="gpt-image-1",
            prompt=f"{prompt} storyboard frame {i+1}",
            size="512x512",
        )
        images.append(img.data[0].url)
    return images


async def platform_variations(prompt: str) -> Dict[str, str]:
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    messages = [
        {
            "role": "system",
            "content": "Create platform-specific hooks and CTAs for TikTok and Instagram Reels.",
        },
        {"role": "user", "content": prompt},
    ]
    chat = await openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )
    # naive parsing: assume two lines tiktok:..., instagram:...
    variations = {}
    for line in chat.choices[0].message.content.splitlines():
        if ":" in line:
            platform, text = line.split(":", 1)
            variations[platform.strip().lower()] = text.strip()
    return variations


async def generate_package(prompt: str, niche: str | None = None) -> Dict[str, Any]:
    script = await generate_script(prompt, niche)
    storyboard = await generate_storyboard(prompt)
    notes = [
        "Use upbeat background music",
        "Average shot length ~1s",
        "Include on-screen captions",
    ]
    variations = await platform_variations(prompt)
    return {
        "script": script,
        "storyboard": storyboard,
        "notes": notes,
        "variations": variations,
    }
