import time
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import TrendingAudio
from backend.routers import audio as audio_router


async def fake_get_trending_audio(niche=None, limit=10, ranking_date=None):
    return [
        TrendingAudio(audio_id="a1", audio_hash="h1", count=1, avg_engagement=0.0, url="u1", niche=niche)
    ]


def test_trending_endpoint(monkeypatch):
    monkeypatch.setattr(audio_router, "get_trending_audio", fake_get_trending_audio)
    client = TestClient(app)
    start = time.perf_counter()
    resp = client.get("/api/audio/trending")
    elapsed = time.perf_counter() - start
    assert resp.status_code == 200
    assert resp.json()[0]["audio_id"] == "a1"
    assert elapsed < 0.5
