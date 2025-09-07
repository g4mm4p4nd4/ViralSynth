"""Endpoints for ingesting trending content into ViralSynth."""

from fastapi import APIRouter

from ..models import (
    IngestRequest,
    IngestResponse,
    StrategyRequest,
    GenerateRequest,
)
from ..services.ingestion import ingest_niche
from .strategy import analyze_strategy
from .generate import generate_content

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

    # After ingestion, analyze patterns across niches.
    strategy_resp = await analyze_strategy(StrategyRequest(niches=request.niches))

    # Generate a sample content package using the first niche as context.
    sample_prompt = (
        f"Generate a viral video idea for the {request.niches[0]} niche"
        if request.niches
        else "Generate a viral video idea"
    )
    generate_resp = await generate_content(GenerateRequest(prompt=sample_prompt))

    return IngestResponse(
        message="Ingestion complete",
        patterns=strategy_resp.patterns,
        generated=generate_resp,
    )
