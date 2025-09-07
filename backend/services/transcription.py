import asyncio
import os
from typing import Dict, Any

import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

async def extract_audio_from_video(video_url: str, output_path: str) -> str:
    """Download a video's audio track using ffmpeg.

    Returns the path to the extracted audio file. The ``ffmpeg`` binary must be
    available on the system path.
    """
    # Use ffmpeg to download audio from the video URL.
    process = await asyncio.create_subprocess_exec(
        "ffmpeg", "-i", video_url, "-vn", "-acodec", "mp3", output_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        # raise an error if ffmpeg fails
        raise RuntimeError(f"ffmpeg failed: {stderr.decode()}")
    return output_path

async def transcribe_audio(audio_path: str, use_turbo: bool = False) -> Dict[str, Any]:
    """Transcribe an audio file using Groq's Whisper API.

    If ``use_turbo`` is True, the ``whisper-turbo`` model is used; otherwise the
    ``whisper-large`` model is selected. Returns the JSON response from the Groq
    API.
    """
    model = "whisper-turbo" if use_turbo else "whisper-large"
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    # Read the audio file and send it as multipart/form-data
    with open(audio_path, "rb") as audio_file:
        files = {"file": ("audio.mp3", audio_file, "audio/mpeg")}
        data = {"model": model}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, data=data, files=files, timeout=60)
            resp.raise_for_status()
            return resp.json()


async def transcribe_video(video_url: str, use_turbo: bool = False) -> Dict[str, Any]:
    """Extract a video's audio with ffmpeg and transcribe it via Groq Whisper.

    This high-level helper downloads the audio track with ``extract_audio_from_video``
    and then calls ``transcribe_audio``. Temporary audio files are cleaned up after
    transcription.
    """
    audio_path = "temp_audio.mp3"
    try:
        await extract_audio_from_video(video_url, audio_path)
        return await transcribe_audio(audio_path, use_turbo=use_turbo)
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
