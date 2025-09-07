"""Service layer for the trend ingestion engine."""

from typing import Any, Dict, List

from . import apify_client, analysis, supabase_client


async def ingest_niche(niche: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Scrape videos for a niche and enrich them with transcripts and analysis."""
    videos = await apify_client.fetch_trending_videos(niche, limit=limit)
    enriched: List[Dict[str, Any]] = []
    for video in videos:
        audio_url = video.get("musicUrl") or video.get("videoUrl")
        transcript = None
        if audio_url:
            try:
                transcript = await analysis.transcribe_audio(audio_url)
            except Exception:
                transcript = ""
        video_analysis = await analysis.analyze_video(transcript or "")
        item = {
            "niche": niche,
            "title": video.get("title"),
            "url": video.get("url"),
            "transcript": transcript,
            "analysis": video_analysis,
        }
        enriched.append(item)
    try:
        supabase_client.store_ingest_results(enriched)
    except Exception:
        pass
    return enriched
