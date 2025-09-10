import asyncio
from backend.services import transcription


async def fake_extract(video_url, chunk_length=30, prefix="chunk"):
    return ["c1.mp3", "c2.mp3"]


async def fake_transcribe(path, use_turbo=False):
    return {"text": f"text_{path}"}


async def run_test():
    res = await transcription.transcribe_video("url", chunk_length=30)
    assert res["text"] == "text_c1.mp3\ntext_c2.mp3"


def test_transcribe_video(monkeypatch):
    monkeypatch.setattr(transcription, "extract_audio_chunks", fake_extract)
    monkeypatch.setattr(transcription, "transcribe_audio", fake_transcribe)
    asyncio.run(run_test())
