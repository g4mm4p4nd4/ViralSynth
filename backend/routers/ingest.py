"""Endpoints for ingesting trending content into ViralSynth."""

from fastapi import APIRouter

from ..models import IngestRequest, IngestResponse
from ..services.ingestion import ingest_niche

router = APIRouter(
    prefix="/api/ingest",
    tags=["ingest"],
)


@router.post("/", response_model=IngestResponse)
async def ingest_trending_content(request: IngestRequest) -> IngestResponse:
    """
    Placeholder endpoint for ingesting top-performing content from various niches.

    In a full implementation, this would call an external scraping service (e.g., Apify)
    to collect trending videos, transcribe audio, analyze visual style and pacing, and
    persist the results to a database for further analysis.
    """
    # Call the ingestion service for each niche. The provider can be specified in
    # the request or via the INGESTION_PROVIDER environment variable.
    for niche in request.niches:
        percentile = int(request.top_percentile * 100)
        await ingest_niche(niche, percentile, provider=request.provider)

    return IngestResponse(message="Ingest request received. Ingestion logic not yet implemented.")
