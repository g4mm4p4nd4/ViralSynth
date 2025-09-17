import asyncio
import glob
import os
from typing import Dict, Any, List

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


async def extract_audio_chunks(
    video_url: str, chunk_length: int = 30, prefix: str = "chunk"
) -> List[str]:
    """Split a video's audio into smaller segments using ffmpeg."""
    for f in glob.glob(f"{prefix}_*.mp3"):
        os.remove(f)
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-i",
        video_url,
        "-f",
        "segment",
        "-segment_time",
        str(chunk_length),
        "-vn",
        "-acodec",
        "mp3",
        f"{prefix}_%03d.mp3",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg chunking failed: {stderr.decode()}")
    return sorted(glob.glob(f"{prefix}_*.mp3"))

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


async def transcribe_video(
    video_url: str, use_turbo: bool = False, chunk_length: int = 0
) -> Dict[str, Any]:
    """Transcribe a video's audio track using Groq Whisper.

    When ``chunk_length`` is greater than zero the audio is split into roughly
    equal segments and each segment is transcribed separately. The resulting
    texts are concatenated. Without chunking the full audio track is processed
    in a single request.
    """
    if chunk_length and chunk_length > 0:
        chunks = await extract_audio_chunks(video_url, chunk_length)
        texts: List[str] = []
        try:
            for c in chunks:
                data = await transcribe_audio(c, use_turbo=use_turbo)
                txt = data.get("text", "")
                if txt:
                    texts.append(txt)
            return {"text": "\n".join(texts)}
        finally:
            for c in chunks:
                if os.path.exists(c):
                    os.remove(c)
    else:
        audio_path = "temp_audio.mp3"
        try:
            await extract_audio_from_video(video_url, audio_path)
            return await transcribe_audio(audio_path, use_turbo=use_turbo)
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
