"""Endpoint for generating multi-modal content packages."""

from fastapi import APIRouter

from ..models import GenerateRequest, GenerateResponse
from ..services import generation as generation_service, supabase_client

router = APIRouter(
    prefix="/api/generate",
    tags=["generate"],
)


@router.post("/", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest) -> GenerateResponse:
    """Generate a script, storyboard, notes and platform variations."""
    package = await generation_service.generate_package(
        request.prompt, request.niche
    )
    try:
        supabase_client.store_generated_package({**package, "prompt": request.prompt})
    except Exception:
        pass
    return GenerateResponse(**package)
