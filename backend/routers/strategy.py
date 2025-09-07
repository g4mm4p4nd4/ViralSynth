"""Endpoints that expose content strategy insights."""

from fastapi import APIRouter

from ..models import StrategyRequest, StrategyResponse
from ..services import strategy as strategy_service

router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"],
)


@router.post("/", response_model=StrategyResponse)
async def analyze_strategy(request: StrategyRequest) -> StrategyResponse:
    """Identify successful content patterns for the given niches."""
    patterns = await strategy_service.derive_patterns(request.niches)
    return StrategyResponse(patterns=patterns)
