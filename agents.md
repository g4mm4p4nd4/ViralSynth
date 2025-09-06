# AGENTS.md – ViralSynth Platform Specification

> **Status:** Project specification v1.0 – compiled September 6, 2025 based on the ViralSynth project brief. This document defines the contract for the Codex agents to build the ViralSynth SaaS platform.

---

## Purpose & Mission

ViralSynth is a SaaS platform designed to move beyond simple content ideation and into autonomous content strategy and generation. It analyses viral trends across multiple social platforms in real time, deconstructs their core components (visual, narrative, and audio), and uses these patterns to generate complete, ready-to-produce content packages for creators and marketers. It aims to eliminate creative guesswork by transforming proven success into a generative formula.

## User Persona

The primary user is a high‑leverage content creator or a small marketing team. They are results‑driven, time‑poor, and need to produce consistently high‑performing content without spending hours on manual research. They are comfortable with AI and automation and value tools that provide a direct path from idea to execution.

## System Modules

### 1. Multi‑Modal Trend Ingestion Engine

This asynchronous pipeline continuously scrapes and processes the top 1–5 % performing content from specified niches (e.g., tech, fitness, finance) using services such as the Apify API. It must:

- Scrape reels, shorts and TikToks.
- Transcribe and tag trending audio and background music.
- Analyse video pacing (shot length and editing frequency).
- Identify the visual style (cinematic vs lo‑fi, colour palettes, etc.).
- Extract on‑screen text and annotate its purpose (hook, value point, call to action).

### 2. Generative Strategy Core

This core synthesises ingested data into actionable strategies rather than simple reports. Responsibilities:

- Recognise recurring patterns and formulas (e.g., “3 mistakes you’re making” in finance).
- Break each ingested video into a structured template: hook, core value loop, narrative arc, visual formula, CTA.
- Maintain a library of successful frameworks to be used when generating new content.
- Expose an API that, given a niche and type of output, returns a data structure describing the best‑performing patterns.

### 3. Multi‑Modal Content Package Generation

Given a simple user prompt (e.g., “an idea for my new AI SaaS product”), the system must assemble a complete content package using the patterns from Module 2:

- **Generated Script:** Spoken lines, on‑screen text, timing cues and narrative flow.
- **Visual Storyboard:** A set of AI‑generated images or placeholders illustrating key frames; these can be produced via DALL‑E 3 or a similar API.
- **Production Notes:** A bulleted list of instructions such as which trending audio to use, average shot length, camera style and CTA guidance.
- **Platform‑Specific Variations:** Variations of the hook and CTA tailored to TikTok vs Instagram Reels.

## Architecture Overview

### Backend – FastAPI

- Use Python and FastAPI to build an asynchronous backend service.
- Expose REST endpoints for each module, e.g., `/api/ingest`, `/api/strategy`, `/api/generate`.
- Define Pydantic models for incoming and outgoing data (scripts, storyboards, analytics).
- Integrate with external APIs: Apify for scraping, OpenAI or Anthropic for multi‑modal analysis, DALL‑E 3 API for images.
- Persist data and user sessions using a real‑time database such as Supabase or Firebase.

### Frontend – Next.js + Tailwind CSS

- Use Next.js (React) to build a dark‑themed dashboard.
- The dashboard should present:
  - A central input field for the user prompt.
  - A display area for generated scripts and image storyboards.
  - Controls to select niche and platform (TikTok, Reels).
- Use Tailwind CSS for rapid styling. The design should be clean, minimalist and include a single bright accent colour.
- Use fetch or Axios to call backend endpoints and display results.
- Authenticate users via Supabase/Firebase auth.

### Database

A cloud database (Supabase or Firebase) will store:

- User accounts and roles.
- Cached trend analytics and patterns.
- Generated content packages and storyboards.
- API tokens and configuration for third‑party services.

### AI Models

- Use GPT‑4o or Claude 3.5 Sonnet for multi‑modal reasoning and pattern recognition.
- Use DALL‑E 3 (or Midjourney) API for generating storyboards.
- The AI prompts for UI generation should be produced via v0.dev to design the dashboard quickly.

### Deployment

- Host the frontend on Vercel for automatic builds and previews.
- Deploy the backend as a container on Google Cloud Run or a similar serverless compute platform.
- Manage secrets via environment variables and the deployment platform’s secret manager.

## Execution Plan for Codex Agents

This project will be delivered by multiple Codex agents under this specification. Agents should adhere strictly to the tasks below.

### Phase 1 – Project Scaffolding

1. **Create repository structure**  
   - At the root, create a `backend/` directory for the FastAPI service and a `frontend/` directory for the Next.js application.  
   - Include a top‑level `README.md` with setup instructions.

2. **Backend scaffolding**  
   - Initialise a Python package in `backend/`.  
   - Create `main.py` that instantiates a FastAPI app with CORS enabled.  
   - Add a `models.py` defining Pydantic models for request/response schemas.  
   - Create `routers/` directory with placeholders for `ingest.py`, `strategy.py` and `generate.py`. Each router should register its endpoints with the main app.  
   - Add `requirements.txt` specifying FastAPI, uvicorn[standard], httpx, pydantic, async packages and any other dependencies such as supabase client libraries.

3. **Frontend scaffolding**  
   - Initialise a Next.js 14 project with TypeScript support inside `frontend/`.  
   - Configure Tailwind CSS with a dark theme.  
   - Create a main page (`pages/index.tsx`) containing:  
     - An input form for the user’s content idea.  
     - Buttons or selectors for niche and platform.  
     - Sections to display generated scripts and images.  
   - Add a service module to call the backend API.

4. **Database setup**  
   - Add configuration files for Supabase/Firebase if required.  
   - Provide an environment variable template `.env.example` listing required keys (Supabase URL, API keys, AI model keys).

### Phase 2 – Core Features

5. **Ingestion Endpoint**  
   - Implement `/api/ingest` to accept a `POST` with niche and optional platform.  
   - Use placeholder logic (e.g., stubs) to call Apify and return mock analytics until integration is implemented.  
   - Document the endpoint in the README.

6. **Strategy Endpoint**  
   - Implement `/api/strategy` to process ingest data and return recognised patterns and templates.  
   - For now, return fixed sample patterns derived from the project brief.

7. **Generation Endpoint**  
   - Implement `/api/generate` that accepts a user prompt and optional niche/platform.  
   - Compose a JSON response with keys: `script`, `storyboard`, `notes`, and `variations`.  
   - Use GPT‑4o or similar to generate placeholder content.

8. **Frontend Integration**  
   - Build a page that sends the prompt to `/api/generate` and renders the returned script and storyboard.  
   - Use React state to display loading status and results.  
   - Style the UI using Tailwind.

### Phase 3 – Documentation & Deployment

9. **Write README.md**  
   - Provide clear setup instructions for backend and frontend: prerequisites, installation commands, environment variables, and how to run locally.  
   - Document all API endpoints with request and response examples.  
   - Outline deployment steps for Vercel and Cloud Run.

10. **Dev & Prod Configuration**  
   - Add a `Dockerfile` for the backend and a `vercel.json` or similar for the frontend.  
   - Ensure the project can run locally with `docker-compose` (optional).

### DefinDition of Done

- The repository builds and runs locally with a working backend and frontend skeleton.
- All endpoints return valid JSON with placeholder content.
- The README explains how to install dependencies, set up environment variables and run both services.
- The UI allows a user to input a prompt and see the generated placeholders.

### Future Work

- Replace ingestion stubs with real scraping via Apify.
- Implement pattern recognition and generation logic using AI models.
- Integrate DALL‑E 3 for storyboard generation.
- Add authentication and user accounts via Supabase/Firebase.

---

Adhere to this specification when generating code. All agents should produce clear, maintainable code with proper separation of concerns and comments where necessary.
