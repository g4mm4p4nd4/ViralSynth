"""Ingestion service for fetching videos and enriching them with analysis."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import hashlib

import cv2
import numpy as np
import httpx
import pytesseract
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from playwright.async_api import async_playwright
from pyppeteer import launch

from ..models import VideoRecord, TrendingAudio
from .supabase import get_supabase_client
from .transcription import transcribe_video

APIFY_ACTOR_ID = os.environ.get("APIFY_ACTOR_ID", "your_apify_actor_id")
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")
pytesseract.pytesseract.tesseract_cmd = os.environ.get("PYTESSERACT_PATH", "tesseract")


async def _ingest_niche_apify(niche: str, percentile: int) -> List[Dict[str, Any]]:
    """Fetch trending videos for a niche using the Apify actor API (placeholder)."""

    url = f"https://api.apify.com/v2/actors/{APIFY_ACTOR_ID}/runs"
    payload = {"niche": niche, "percentile": percentile}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {APIFY_TOKEN}"}
    async with httpx.AsyncClient() as client:
        try:
            # resp = await client.post(url, json=payload, headers=headers)
            # data = resp.json()
            # return data.get("items", [])
            return []
        except Exception as exc:  # pragma: no cover - network failure
            return [{"error": str(exc)}]


async def _ingest_niche_playwright(niche: str, percentile: int) -> List[Dict[str, Any]]:
    """Scrape trending videos for a niche using Playwright (placeholder)."""

    items: List[Dict[str, Any]] = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(f"https://www.tiktok.com/tag/{niche}")
            # TODO: Extract video metadata here
            await browser.close()
    except Exception as exc:  # pragma: no cover - network failure
        return [{"error": str(exc)}]
    return items


async def _ingest_niche_puppeteer(niche: str, percentile: int) -> List[Dict[str, Any]]:
    """Scrape trending videos for a niche using Pyppeteer (placeholder)."""

    items: List[Dict[str, Any]] = []
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(f"https://www.tiktok.com/tag/{niche}")
        # TODO: Extract video metadata here
        await browser.close()
    except Exception as exc:  # pragma: no cover - network failure
        return [{"error": str(exc)}]
    return items


def _analyse_pacing(video_path: str) -> float:
    """Estimate average shot length using scenedetect and OpenCV."""

    try:
        vm = VideoManager([video_path])
        sm = SceneManager()
        sm.add_detector(ContentDetector())
        vm.set_downscale_factor()
        vm.start()
        sm.detect_scenes(frame_source=vm)
        scenes = sm.get_scene_list()
        durations = [
            (end.get_frames() - start.get_frames()) / vm.get_framerate()
            for start, end in scenes
        ]
        return float(np.mean(durations)) if durations else 0.0
    except Exception:  # pragma: no cover - best effort
        return 0.0


def _classify_visual_style(video_path: str) -> str:
    """Very rough visual style classification based on contrast."""

    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "unknown"
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return "cinematic" if gray.std() > 50 else "lo-fi"
    except Exception:  # pragma: no cover
        return "unknown"


def _extract_onscreen_text(video_path: str) -> str:
    """Extract on-screen text via pytesseract from the first frame."""

    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return ""
        return pytesseract.image_to_string(frame)
    except Exception:  # pragma: no cover
        return ""


async def ingest_niche(
    niche: str, percentile: int, provider: Optional[str] = None
) -> List[VideoRecord]:
    """Ingest a niche using the requested provider and enrich video records."""

    provider_name = (provider or os.environ.get("INGESTION_PROVIDER", "apify")).lower()
    if provider_name == "playwright":
        items = await _ingest_niche_playwright(niche, percentile)
    elif provider_name == "puppeteer":
        items = await _ingest_niche_puppeteer(niche, percentile)
    else:
        items = await _ingest_niche_apify(niche, percentile)

    supabase = get_supabase_client()
    records: List[VideoRecord] = []
    audio_counts: Dict[str, int] = {}

    if supabase and items:
        for item in items:
            url = item.get("url", "")
            audio_id = item.get("audio_id", "audio")
            audio_url = item.get("audio_url", f"https://audio.example/{audio_id}")
            likes = int(item.get("likes", 0) or 0)
            comments = int(item.get("comments", 0) or 0)
            audio_hash = hashlib.md5(audio_id.encode()).hexdigest()

            try:
                transcript_data = await transcribe_video(url)
                transcript = transcript_data.get("text", "")
            except Exception:
                transcript = ""

            pacing = _analyse_pacing(url)
            visual_style = _classify_visual_style(url)
            onscreen_text = _extract_onscreen_text(url)

            audio_counts[audio_id] = audio_counts.get(audio_id, 0) + 1
            trending_audio = audio_counts[audio_id] > 1

            row = {
                "niche": niche,
                "provider": provider_name,
                "url": url,
                "audio_id": audio_id,
                "audio_url": audio_url,
                "audio_hash": audio_hash,
                "likes": likes,
                "comments": comments,
                "transcript": transcript,
                "pacing": pacing,
                "visual_style": visual_style,
                "onscreen_text": onscreen_text,
                "trending_audio": trending_audio,
            }
            try:
                resp = supabase.table("videos").insert(row).execute()
                vid = resp.data[0]["id"] if resp.data else None
            except Exception:
                vid = None

            records.append(
                VideoRecord(
                    id=vid,
                    url=url,
                    niche=niche,
                    provider=provider_name,
                    transcript=transcript,
                    pacing=pacing,
                    visual_style=visual_style,
                    onscreen_text=onscreen_text,
                    audio_id=audio_id,
                    audio_url=audio_url,
                    audio_hash=audio_hash,
                    likes=likes,
                    comments=comments,
                    trending_audio=trending_audio,
                )
            )

    return records


async def get_trending_audio(
    niche: Optional[str] = None, limit: int = 10
) -> List[TrendingAudio]:
    """Aggregate audio usage across all videos and return top results."""

    limit = int(os.environ.get("TRENDING_AUDIO_LIMIT", limit))
    supabase = get_supabase_client()
    if not supabase:
        return []
    try:
        query = supabase.table("videos").select(
            "audio_id,audio_url,audio_hash,niche,likes,comments"
        )
        if niche:
            query = query.eq("niche", niche)
        resp = query.execute()
        rows = resp.data or []
    except Exception:
        return []

    counts: Dict[str, int] = {}
    urls: Dict[str, str] = {}
    hashes: Dict[str, str] = {}
    niches: Dict[str, str] = {}
    engagements: Dict[str, int] = {}
    for r in rows:
        aid = r.get("audio_id") or ""
        if not aid:
            continue
        counts[aid] = counts.get(aid, 0) + 1
        urls.setdefault(aid, r.get("audio_url") or r.get("url"))
        hashes.setdefault(aid, r.get("audio_hash") or "")
        niches.setdefault(aid, r.get("niche"))
        engagements[aid] = engagements.get(aid, 0) + (
            (r.get("likes") or 0) + (r.get("comments") or 0)
        )

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    results: List[TrendingAudio] = []
    for aid, count in ranked:
        avg = engagements.get(aid, 0) / count if count else 0
        results.append(
            TrendingAudio(
                audio_id=aid,
                audio_hash=hashes.get(aid) or "",
                count=count,
                avg_engagement=avg,
                url=urls.get(aid),
                niche=niches.get(aid),
            )
        )
    return results

