"""Endpoints for ingesting trending content into ViralSynth."""

from fastapi import APIRouter
from typing import List

from ..models import (
    IngestRequest,
    IngestResponse,
    StrategyRequest,
    GenerateRequest,
)
from ..services.ingestion import ingest_niche
from ..services.strategy import derive_patterns
from ..services.generation import generate_package

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
    video_records = []
    for niche in request.niches:
        percentile = int(request.top_percentile * 100)
        records = await ingest_niche(niche, percentile, provider=request.provider)
        video_records.extend(records)
    video_ids = [v.id for v in video_records if v.id]

    # After ingestion, analyze patterns across the stored videos.
    strategy_resp = await derive_patterns(
        StrategyRequest(niches=request.niches, video_ids=video_ids)
    )

    # Generate a sample content package using the first niche as context.
    sample_prompt = (
        f"Generate a viral video idea for the {request.niches[0]} niche"
        if request.niches
        else "Generate a viral video idea"
    )
    generate_resp = await generate_package(
        GenerateRequest(
            prompt=sample_prompt,
            niche=request.niches[0] if request.niches else None,
            pattern_ids=strategy_resp.pattern_ids,
        )
    )

    return IngestResponse(
        message="Ingestion complete",
        video_ids=video_ids,
        videos=video_records,
        patterns=strategy_resp.patterns,
        pattern_ids=strategy_resp.pattern_ids,
        generated=generate_resp,
    )
