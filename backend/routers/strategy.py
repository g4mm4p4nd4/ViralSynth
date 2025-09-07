"""Endpoints that expose content strategy insights."""

from fastapi import APIRouter

from ..models import StrategyRequest, StrategyResponse
from ..services.strategy import derive_patterns

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"],
)


@router.post("/", response_model=StrategyResponse)
async def analyze_strategy(request: StrategyRequest) -> StrategyResponse:
    """Analyze stored videos and extract patterns using GPT."""
    return await derive_patterns(request)
