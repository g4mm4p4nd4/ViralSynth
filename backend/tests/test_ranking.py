import asyncio
from types import SimpleNamespace

from backend.services import ingestion


class VideosTable:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class RankTable:
    def __init__(self, store):
        self.store = store

    def upsert(self, row, on_conflict=None):
        key = (row.get("ranking_date"), row.get("niche"), row.get("audio_id"))
        for idx, existing in enumerate(self.store):
            existing_key = (
                existing.get("ranking_date"),
                existing.get("niche"),
                existing.get("audio_id"),
            )
            if key == existing_key:
                self.store[idx] = row
                break
        else:
            self.store.append(row)
        return self

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=self.store)


class DummySupabase:
    def __init__(self, rows, store):
        self.rows = rows
        self.store = store

    def table(self, name):
        if name == "videos":
            return VideosTable(self.rows)
        return RankTable(self.store)


def test_get_trending_audio(monkeypatch):
    rows = [
        {"audio_id": "a1", "audio_url": "u1", "audio_hash": "h1", "niche": "tech", "likes": 10, "comments": 0},
        {"audio_id": "a1", "audio_url": "u1", "audio_hash": "h1", "niche": "tech", "likes": 5, "comments": 0},
        {"audio_id": "a2", "audio_url": "u2", "audio_hash": "h2", "niche": "tech", "likes": 1, "comments": 0},
    ]
    store = []
    dummy = DummySupabase(rows, store)
    monkeypatch.setattr(ingestion, "get_supabase_client", lambda: dummy)

    results = asyncio.run(ingestion.get_trending_audio(niche="tech", limit=2))
    assert results[0].audio_id == "a1"
    assert len(store) == len(results)
