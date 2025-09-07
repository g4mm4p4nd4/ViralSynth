"""Supabase client wrapper for persistence."""

import os
from typing import Any, Dict, List

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

_supabase: Client | None = None


def get_client() -> Client:
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Supabase credentials not configured")
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase


def store_ingest_results(items: List[Dict[str, Any]]) -> None:
    client = get_client()
    # insert asynchronously is not supported; run synchronous insert
    client.table("ingestions").insert(items).execute()


def store_generated_package(data: Dict[str, Any]) -> None:
    client = get_client()
    client.table("generated_packages").insert(data).execute()
