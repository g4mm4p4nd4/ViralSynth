"""Tests for the daily audio ranking CLI utilities."""

import asyncio
import os
from datetime import date
from types import SimpleNamespace

from backend.services import ingestion
from backend.services.metrics import audio_ranker


class VideosTable:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def eq(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def execute(self):
        return SimpleNamespace(data=self.rows)


class RankTable:
    def __init__(self, store):
        self.store = store
        self.last_conflict = None

    def upsert(self, row, on_conflict=None):
        self.last_conflict = on_conflict
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

    def select(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def eq(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def order(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def limit(self, *args, **kwargs):  # noqa: D401 - proxy method
        return self

    def execute(self):
        return SimpleNamespace(data=list(self.store))


class DummySupabase:
    def __init__(self, rows, store):
        self.rows = rows
        self.rank_table = RankTable(store)

    def table(self, name):
        if name == "videos":
            return VideosTable(self.rows)
        return self.rank_table


class FrozenDate(date):
    @classmethod
    def today(cls):
        return cls(2024, 1, 5)


def test_audio_ranker_cli_is_idempotent(monkeypatch):
    rows = [
        {"audio_id": "a1", "audio_url": "u1", "audio_hash": "h1", "niche": "tech", "likes": 10, "comments": 0},
        {"audio_id": "a2", "audio_url": "u2", "audio_hash": "h2", "niche": "tech", "likes": 20, "comments": 5},
    ]
    store = []
    dummy = DummySupabase(rows, store)
    monkeypatch.setattr(ingestion, "get_supabase_client", lambda: dummy)
    monkeypatch.setattr(audio_ranker, "date", FrozenDate)

    prior_env = os.environ.get("RANKING_DATE")
    try:
        first = asyncio.run(audio_ranker.run_audio_ranker(niches=["tech"], days=1, limit=5))
        snapshot = list(store)
        second = asyncio.run(audio_ranker.run_audio_ranker(niches=["tech"], days=1, limit=5))
    finally:
        if prior_env is None:
            os.environ.pop("RANKING_DATE", None)
        else:
            os.environ["RANKING_DATE"] = prior_env

    assert store == snapshot
    assert first == second
    assert dummy.rank_table.last_conflict == "ranking_date,niche,audio_id"
