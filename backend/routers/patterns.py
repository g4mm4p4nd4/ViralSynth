"""Endpoints to fetch stored content patterns."""

from fastapi import APIRouter
from typing import List, Optional

from ..models import Pattern
from ..services.strategy import fetch_patterns

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


@router.get("/", response_model=List[Pattern])
async def list_patterns(niche: Optional[str] = None, limit: int = 10) -> List[Pattern]:
    """List stored patterns ordered by prevalence."""
    return await fetch_patterns(niche=niche, limit=limit)
