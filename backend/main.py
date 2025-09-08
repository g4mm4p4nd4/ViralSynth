"""Entry point for the ViralSynth FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ingest, strategy, generate, audio, patterns

app = FastAPI(title="ViralSynth API")

# CORS settings for local development; adjust origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ingest.router)
app.include_router(strategy.router)
app.include_router(generate.router)
app.include_router(audio.router)
app.include_router(patterns.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to ViralSynth API"}
