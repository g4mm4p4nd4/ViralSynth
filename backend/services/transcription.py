import asyncio
import os
from typing import Dict, Any

import httpx

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Default whisper model: whisper-large or whisper-turbo
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "whisper-large")

async def extract_audio_from_video(video_url: str, output_path: str) -> str:
    """
    Download the audio track from a video using ffmpeg.
    Returns the path to the extracted audio file.
    """
    # Use ffmpeg to download audio from the video URL.
    # ffmpeg must be installed in the running environment.
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
    """
    Transcribe an audio file using Groq's Whisper API.
    If use_turbo is True, uses the whisper-turbo model; otherwise whisper-large.
    Returns the JSON response from the Groq API.
    """
    # Determine which model to use
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
