from fastapi.testclient import TestClient

from fastapi import FastAPI
from fastapi.testclient import TestClient
import sys
from types import SimpleNamespace

from backend.models import Pattern


def test_list_patterns_endpoint(monkeypatch):
    sys.modules.setdefault(
        "supabase", SimpleNamespace(create_client=lambda *a, **k: None, Client=object)
    )
    from backend.routers import patterns as patterns_router

    app = FastAPI()
    app.include_router(patterns_router.router)
    async def fake_fetch_patterns(niche=None, limit=10):
        return [
            Pattern(
                id=1,
                niche="tech",
                hook="Bold claim",
                core_value_loop="Explain three tips",
                narrative_arc="informational",
                visual_formula="lofi",
                cta="Follow",
                prevalence=0.5,
                engagement_score=100.0,
            )
        ]

    monkeypatch.setattr(
        "backend.routers.patterns.fetch_patterns", fake_fetch_patterns
    )
    client = TestClient(app)
    resp = client.get("/api/patterns?niche=tech")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["hook"] == "Bold claim"
    assert data[0]["prevalence"] == 0.5
    assert data[0]["engagement_score"] == 100.0
