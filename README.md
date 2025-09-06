# ViralSynth

ViralSynth is an autonomous content strategy & generation engine designed to help creators and marketers produce high performing short‑form video content. It ingests top‑performing Reels, TikToks and Shorts from specified niches, deconstructs their elements (audio, video pacing, on‑screen text, narrative) and synthesizes patterns. Using these patterns it generates complete content packages including scripts, storyboards and production notes.

## Monorepo Structure

This repository contains two services:

- `backend/` – a FastAPI application that exposes REST endpoints for ingesting trending content, analyzing strategies and generating content packages.
- `frontend/` – a Next.js webapp with Tailwind CSS that provides a dashboard for entering prompts and viewing generated scripts, images and notes.

Supporting agent specifications (`agents.md`, `agents_architect.md`, `agents_spec_writer.md`, `agents_project_manager.md`) outline the autonomous agents used to build the system. The `status.md` file tracks outstanding work.

## Backend Setup

1. Install Python 3.10+ and create a virtual environment.
2. Navigate to the `backend` directory and install dependencies:

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
| POST  | `/ingest/`      | Ingest trending content data for analysis. |
| POST  | `/strategy/`    | Analyze patterns and strategies from ingested data. |
| POST  | `/generate/`    | Generate a full content package (script, storyboard, notes) based on a prompt. |

These endpoints currently return placeholder responses and should be extended with logic to call scraping services, transcription models and generative models.

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

The frontend fetches data from the backend’s `/generate` endpoint, displays the generated script and production notes, and renders image storyboards. Tailwind CSS is configured in `tailwind.config.js` and global styles are defined in `styles/globals.css`.

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
