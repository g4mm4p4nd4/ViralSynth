import os
import sys
import types
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.models import Pattern, TrendingAudio


class DummyTable:
    def __init__(self, data):
        self._data = data

    def select(self, *args, **kwargs):
        return self

    def in_(self, field, values):
        return self

    def eq(self, field, value):
        return self

    def order(self, *args, **kwargs):
        column = args[0] if args else kwargs.get("column")
        desc = kwargs.get("desc", False)
        self._data = sorted(self._data, key=lambda d: d.get(column), reverse=desc)
        return self

    def limit(self, n):
        return self

    def execute(self):
        return types.SimpleNamespace(data=self._data)


class DummySupabase:
    def __init__(self, data):
        self._data = data

    def table(self, name):
        assert name == "patterns"
        return DummyTable(self._data)


def test_choose_assets_prefers_high_engagement(monkeypatch):
    sys.modules['supabase'] = types.SimpleNamespace(create_client=lambda *a, **k: None, Client=object)

    async def fake_audio(niche, limit):
        return [
            TrendingAudio(
                audio_id="aud1",
                audio_hash="h1",
                count=5,
                avg_engagement=1.0,
                url="http://example.com",
                niche=niche,
            )
        ]

    sys.modules['backend.services.ingestion'] = types.SimpleNamespace(get_trending_audio=fake_audio)
    from backend.services.chooser import choose_assets

    patterns = [
        {
            "id": 1,
            "hook": "A",
            "core_value_loop": "",
            "narrative_arc": "",
            "visual_formula": "",
            "cta": "",
            "engagement_score": 10,
        },
        {
            "id": 2,
            "hook": "B",
            "core_value_loop": "",
            "narrative_arc": "",
            "visual_formula": "",
            "cta": "",
            "engagement_score": 20,
        },
    ]

    monkeypatch.setattr("backend.services.chooser.get_supabase_client", lambda: DummySupabase(patterns))

    async def run_test():
        audio, selected_patterns = await choose_assets("tech")
        assert audio.audio_id == "aud1"
        assert len(selected_patterns) == 2
        assert selected_patterns[0].id == 2

        _, patterns_override = await choose_assets("tech", pattern_ids=[1])
        assert patterns_override[0].id == 1

    asyncio.run(run_test())
