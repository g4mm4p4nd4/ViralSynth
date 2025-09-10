# ViralSynth

ViralSynth is an autonomous content strategy & generation engine designed to help creators and marketers produce high performing short‑form video content. It ingests top‑performing Reels, TikToks and Shorts from specified niches, deconstructs their elements (audio, video pacing, on‑screen text, narrative) and synthesizes patterns. Using these patterns it generates complete content packages including scripts, storyboards and production notes.

## Monorepo Structure

This repository contains two services:

- `backend/` – a FastAPI application that exposes REST endpoints for ingesting trending content, analyzing strategies and generating content packages.
- `frontend/` – a Next.js webapp with Tailwind CSS that provides a tabbed dashboard for trending audio, patterns, and content generation with optional pattern overrides. The dashboard now surfaces trending audio metrics and structured pattern details.

Supporting agent specifications (`agents.md`, `agents_architect.md`, `agents_spec_writer.md`, `agents_project_manager.md`) outline the autonomous agents used to build the system. The `status.md` file tracks outstanding work.

## Backend Setup

1. Install Python 3.10+ and create a virtual environment.
2. Navigate to the `backend` directory and install dependencies. In addition to FastAPI, OpenAI, Supabase and the Playwright/Pyppeteer clients, the backend now relies on libraries for audio and video analysis such as OpenCV, SceneDetect, MoviePy, Librosa, Pytesseract and ffmpeg-python.

   ```bash
   pip install -r requirements.txt
   ```

3. Start the development server:

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

### API Endpoints

| Method | Endpoint        | Description                          |
|-------|-----------------|--------------------------------------|
| POST  | `/api/ingest`      | Ingest trending content data, analyze pacing, style, text and audio, store videos in Supabase and return pattern IDs, trending audio rankings and a sample package. |
| POST  | `/api/strategy`    | Analyze stored videos in Supabase and persist structured templates (hook, value loop, narrative arc, visual formula, CTA). |
| POST  | `/api/generate`    | Generate a full content package from stored patterns and trending audio hints. Accepts `niche` and optional `pattern_ids` overrides and returns the selected audio and pattern details. |
| GET   | `/api/audio/trending` | Retrieve top trending audio clips with usage counts and engagement. |
| GET   | `/api/patterns`       | Fetch stored patterns with prevalence and engagement stats for a given niche. |

These endpoints now persist videos, patterns and generated packages to Supabase. LLM and scraping integrations remain rudimentary and should be expanded for production use.

## Frontend Setup

1. Ensure you have Node.js (v18+) and npm installed.
2. Navigate to the `frontend` directory and install packages:

   ```bash
   npm install
   ```

3. Run the development server:

   ```bash
   npm run dev
   ```

   The dashboard will be available at `http://localhost:3000`.

The frontend includes a provider dropdown for ingestion requests and displays strategy results along with scripts, DALL‑E storyboard images, production notes and platform‑specific variations returned from the generation endpoint. Tailwind CSS is configured in `tailwind.config.js` and global styles are defined in `styles/globals.css`.

### Workflow

1. **Ingestion** – fetch trending videos for a niche, transcribe audio via Groq Whisper, analyse shot pacing with SceneDetect/OpenCV, classify visual style, run OCR for on‑screen text and aggregate audio usage to rank trending tracks with source links.
2. **Strategy** – video descriptors are mined to derive structured templates (hook, core value loop, narrative arc, visual formula, CTA) and aggregated into pattern stats (prevalence and average engagement) which are saved in Supabase.
3. **Generation** – using the extracted patterns, trending audio, pacing and visual style hints, GPT generates a script, DALL‑E storyboard, production notes and platform‑specific hook/CTA variations.

### Ingestion Providers

The ingestion service supports multiple scraping providers. Choose between Apify, Playwright, or Puppeteer by setting the `INGESTION_PROVIDER` environment variable or by sending a `provider` field in requests to `/api/ingest`. Ingestion responses include detected content patterns and a sample generated package.

### Transcription Service

Audio is extracted with `ffmpeg` and transcribed via the Groq Whisper API. Set `GROQ_API_KEY` and use the `use_turbo` flag when calling the transcription helper to switch between `whisper-large` and `whisper-turbo` models.

### Environment Variables

Copy `.env.example` to `.env` and populate it with API keys for Apify (including `APIFY_API_TOKEN` and `APIFY_ACTOR_ID`), Supabase (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`), OpenAI/DALL‑E and transcription services before running locally or deploying.

Set `PYTESSERACT_PATH` to the location of the `tesseract` binary if it is not on your system path.

Additional knobs:

- `TRENDING_AUDIO_LIMIT` – maximum number of audio tracks returned by the ranking service.
- `PATTERN_ANALYSIS_LIMIT` – cap on number of videos analyzed when mining patterns.
- `PATTERN_CHOOSE_LIMIT` – number of top patterns evaluated when auto-selecting during generation.

### System Dependencies

The ingestion pipeline expects `ffmpeg` and `tesseract-ocr` to be installed on the host system for audio extraction and OCR. On Debian/Ubuntu:

```bash
sudo apt-get install ffmpeg tesseract-ocr
```

Ensure the `PYTESSERACT_PATH` environment variable points to the installed binary when running inside containers or custom environments.

## Deployment

- **Frontend**: Deploy the Next.js application to Vercel for automatic builds and previews.
- **Backend**: Containerize the FastAPI service and deploy to a managed server (e.g. Google Cloud Run or AWS Fargate).
- **Database**: Use Supabase or Firebase for real‑time data storage and authentication.

## Contributing

1. Fork the repository and create a feature branch.
2. Commit your changes with descriptive messages.
3. Open a pull request; ensure CI checks pass and documentation is updated.

---

This README provides a starting point. Refer to the agent specification files for detailed responsibilities and to the `status.md` file for outstanding tasks.
