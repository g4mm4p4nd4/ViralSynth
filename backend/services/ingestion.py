"""Ingestion service for fetching videos and enriching them with analysis."""

from __future__ import annotations

import os
from datetime import date
from typing import Any, Dict, List, Optional
import hashlib

import httpx
from playwright.async_api import async_playwright
from pyppeteer import launch

from ..models import TrendingAudio, VideoRecord
from .supabase import get_supabase_client
from .transcription import transcribe_video
from .video_analysis import analyse_video, save_video_shots

APIFY_ACTOR_ID = os.environ.get("APIFY_ACTOR_ID", "your_apify_actor_id")
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")


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
                transcript_data = await transcribe_video(url, chunk_length=30)
                transcript = transcript_data.get("text", "")
            except Exception:
                transcript = ""

            pacing, brightness, contrast, onscreen_text, shots = analyse_video(url)
            visual_style = "cinematic" if contrast > 50 else "lo-fi"

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
                "brightness": brightness,
                "contrast": contrast,
                "trending_audio": trending_audio,
            }
            try:
                resp = supabase.table("videos").insert(row).execute()
                vid = resp.data[0]["id"] if resp.data else None
            except Exception:
                vid = None

            save_video_shots(vid, shots)

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
                    brightness=brightness,
                    contrast=contrast,
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
    niche: Optional[str] = None,
    limit: int = 10,
    ranking_date: Optional[str] = None,
) -> List[TrendingAudio]:
    """Aggregate audio usage across videos and store daily rankings."""

    limit = int(os.environ.get("TRENDING_AUDIO_LIMIT", limit))
    supabase = get_supabase_client()
    if not supabase:
        return []

    # If a ranking_date is provided, pull precomputed rankings
    if ranking_date:
        try:
            query = supabase.table("audio_daily_rankings").select(
                "audio_id,audio_hash,url,niche,count,avg_engagement,rank"
            ).eq("ranking_date", ranking_date)
            if niche:
                query = query.eq("niche", niche)
            resp = query.order("rank").limit(limit).execute()
            rows = resp.data or []
            return [
                TrendingAudio(
                    audio_id=r["audio_id"],
                    audio_hash=r.get("audio_hash") or "",
                    count=r.get("count") or 0,
                    avg_engagement=r.get("avg_engagement") or 0.0,
                    url=r.get("url"),
                    niche=r.get("niche"),
                )
                for r in rows
            ]
        except Exception:
            return []

    # Otherwise compute rankings from videos table
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
    today = os.environ.get("RANKING_DATE") or date.today().isoformat()
    for rank_idx, (aid, count) in enumerate(ranked, start=1):
        avg = engagements.get(aid, 0) / count if count else 0
        ta = TrendingAudio(
            audio_id=aid,
            audio_hash=hashes.get(aid) or "",
            count=count,
            avg_engagement=avg,
            url=urls.get(aid),
            niche=niches.get(aid),
        )
        results.append(ta)
        if today:
            try:
                supabase.table("audio_daily_rankings").upsert(
                    {
                        "ranking_date": today,
                        "niche": ta.niche,
                        "audio_id": ta.audio_id,
                        "audio_hash": ta.audio_hash,
                        "url": ta.url,
                        "count": ta.count,
                        "avg_engagement": ta.avg_engagement,
                        "rank": rank_idx,
                    }
                ).execute()
            except Exception:
                pass

    return results

