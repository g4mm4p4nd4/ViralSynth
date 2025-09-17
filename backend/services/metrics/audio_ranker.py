"""CLI entrypoint for computing daily trending audio rankings."""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import date, timedelta
from typing import Iterable, Optional

from ..ingestion import get_trending_audio


async def run_audio_ranker(
    niches: Optional[Iterable[Optional[str]]] = None,
    days: int = 7,
    limit: int = 10,
) -> dict[str, dict[str, list[str]]]:
    """Compute rankings for each day and niche and persist them via Supabase."""

    niche_list = list(niches) if niches else [None]
    base_env = os.environ.get("RANKING_DATE")
    summary: dict[str, dict[str, list[str]]] = {}

    try:
        for day_offset in range(days):
            target_date = date.today() - timedelta(days=day_offset)
            iso_date = target_date.isoformat()
            os.environ["RANKING_DATE"] = iso_date
            summary.setdefault(iso_date, {})

            for niche in niche_list:
                audios = await get_trending_audio(niche=niche, limit=limit)
                key = niche or "all"
                summary[iso_date][key] = [audio.audio_id for audio in audios]
    finally:
        if base_env is not None:
            os.environ["RANKING_DATE"] = base_env
        else:
            os.environ.pop("RANKING_DATE", None)

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__ or "Audio ranking job")
    parser.add_argument(
        "--niche",
        action="append",
        dest="niches",
        help="Specify one or more niches to rank. Can be repeated.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days (including today) to compute rankings for.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of audio tracks to compute per niche/day.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> dict[str, dict[str, list[str]]]:
    args = build_parser().parse_args(argv)
    return asyncio.run(
        run_audio_ranker(niches=args.niches, days=args.days, limit=args.limit)
    )


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    summary = main()
    for ranking_date, per_niche in summary.items():
        print(f"{ranking_date}:")
        for niche, audio_ids in per_niche.items():
            joined = ", ".join(audio_ids) or "<no results>"
            print(f"  {niche}: {joined}")
