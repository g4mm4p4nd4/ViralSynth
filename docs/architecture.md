# ViralSynth Architecture

ViralSynth consists of three primary modules:

1. **Multi-Modal Trend Ingestion Engine** – uses Apify to scrape top videos for a niche, transcribes audio with OpenAI Whisper, analyses pacing and style via GPT and stores results in Supabase.
2. **Generative Strategy Core** – queries ingested records from Supabase and uses GPT to derive common patterns and templates.
3. **Multi-Modal Content Package Generation** – generates scripts, DALL-E storyboards, production notes and platform variations using OpenAI APIs. Packages are persisted to Supabase for reuse.

The backend is a FastAPI service exposing `/api/ingest`, `/api/strategy`, and `/api/generate`. The frontend is a Next.js application that allows users to trigger these APIs and visualise results. Supabase provides PostgreSQL storage and can later supply authentication.
