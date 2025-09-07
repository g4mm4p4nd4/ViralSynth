"""Audio transcription and video analysis utilities."""

import io
import os
from typing import Any, Dict

import httpx
from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


async def transcribe_audio(audio_url: str) -> str:
    """Transcribe audio from a remote file using OpenAI Whisper."""
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    async with httpx.AsyncClient() as client:
        audio_bytes = (await client.get(audio_url)).content
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.mp3"
    transcript = await openai_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcript.text


async def analyze_video(transcript: str) -> Dict[str, Any]:
    """Use an LLM to estimate pacing, visual style and on-screen text."""
    if not openai_client:
        raise RuntimeError("OPENAI_API_KEY is not set")
    prompt = (
        "You are a video analysis engine. Given the transcript of a short-form video, "
        "estimate the average shot length in seconds, describe the visual style, and "
        "list any on-screen text with its purpose (hook/value/cta). Return JSON with "
        "keys 'pacing', 'style', 'on_screen_text'. Transcript:\n" + transcript
    )
    chat = await openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
    )
    try:
        import json

        return json.loads(chat.choices[0].message.content)
    except Exception:
        return {
            "pacing": "unknown",
            "style": "unknown",
            "on_screen_text": [],
        }
