"""Client utilities for interacting with the Apify API."""

import os
from typing import Any, Dict, List

import httpx

APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")
APIFY_ACTOR = "apify/social-video-scraper"  # default Apify actor for social video scraping


async def fetch_trending_videos(niche: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch top performing videos for a given niche using Apify.

    Parameters
    ----------
    niche: str
        Topic or hashtag to search for.
    limit: int
        Maximum number of videos to return.
    """
    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_API_TOKEN is not set")

    run_url = (
        f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync" f"?token={APIFY_TOKEN}"
    )
    payload = {
        "queries": [niche],
        "resultsLimit": limit,
    }
    async with httpx.AsyncClient(timeout=None) as client:
        run_resp = await client.post(run_url, json=payload)
        run_resp.raise_for_status()
        run_data = run_resp.json()
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            return []
        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
        items_resp = await client.get(items_url)
        items_resp.raise_for_status()
        return items_resp.json()
