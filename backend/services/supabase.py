"""Utility module for creating a Supabase client used across services."""

import os
from functools import lru_cache
from supabase import create_client, Client


@lru_cache()
def get_supabase_client() -> Client | None:
    """Return a cached Supabase client if credentials are provided."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)
