"""Endpoint for generating multi-modal content packages."""

from fastapi import APIRouter

from ..models import GenerateRequest, GenerateResponse
from ..services.generation import generate_package

router = APIRouter(
    prefix="/api/generate",
    tags=["generate"],
)


@router.post("/", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """Generate a multi-modal content package using stored patterns."""
    return await generate_package(request)
