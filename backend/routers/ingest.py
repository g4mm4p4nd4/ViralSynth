"""Endpoints for ingesting trending content into ViralSynth."""

from typing import Any, Dict, List

from fastapi import APIRouter

from ..models import IngestRequest, IngestResponse
from ..services import ingestion as ingestion_service

router = APIRouter(
    prefix="/api/ingest",
    tags=["ingest"],
)


@router.post("/", response_model=IngestResponse)
async def ingest_trending_content(request: IngestRequest) -> IngestResponse:
    """Scrape and analyze top-performing videos for the requested niches."""
    items: List[Dict[str, Any]] = []
    for niche in request.niches:
        try:
            niche_items = await ingestion_service.ingest_niche(
                niche, int(request.top_percentile * 100)
            )
            items.extend(niche_items)
        except Exception as exc:
            items.append({"niche": niche, "error": str(exc)})
    return IngestResponse(message="ingestion_complete", items=items)
