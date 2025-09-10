"""Pattern mining utilities for ViralSynth.

This service extracts hooks, core value loops, narrative arcs,
visual formulas and CTAs from transcripts and shot graphs and computes
prevalence/engagement statistics per niche.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

from ..models import Pattern


def _split_sentences(text: str) -> List[str]:
    """Naive sentence splitter used for hook/core/cta extraction."""
    if not text:
        return []
    return [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]


def _extract_components(record: Dict) -> Tuple[str, str, str, str, str]:
    """Extract pattern components from a single video record."""
    transcript = record.get("transcript", "")
    visual_style = record.get("visual_style", "") or "unspecified"
    sentences = _split_sentences(transcript)

    hook = sentences[0] if sentences else ""
    cta = sentences[-1] if len(sentences) > 1 else ""
    core = " ".join(sentences[1:-1]) if len(sentences) > 2 else ""

    narrative_arc = "informational"
    if any(word in transcript.lower() for word in ["story", "journey", "once"]):
        narrative_arc = "story"

    visual_formula = visual_style

    return hook, core, narrative_arc, visual_formula, cta


def mine_patterns_from_records(records: List[Dict], niche: str) -> List[Pattern]:
    """Group video records into unique patterns and compute statistics."""
    total = len(records)
    groups: Dict[Tuple[str, str, str, str, str], Dict[str, float]] = defaultdict(
        lambda: {"count": 0, "engagement": 0.0}
    )

    for rec in records:
        hook, core, arc, visual, cta = _extract_components(rec)
        key = (hook, core, arc, visual, cta)
        engagement = float((rec.get("likes") or 0) + (rec.get("comments") or 0))
        groups[key]["count"] += 1
        groups[key]["engagement"] += engagement

    patterns: List[Pattern] = []
    for key, stats in groups.items():
        count = stats["count"]
        engagement_avg = stats["engagement"] / count if count else 0.0
        prevalence = count / total if total else 0.0
        patterns.append(
            Pattern(
                hook=key[0],
                core_value_loop=key[1],
                narrative_arc=key[2],
                visual_formula=key[3],
                cta=key[4],
                prevalence=prevalence,
                engagement_score=engagement_avg,
                niche=niche,
            )
        )

    return patterns


async def mine_and_store_patterns(niche: str) -> List[Pattern]:
    """Fetch video records for a niche, mine patterns and persist them."""
    from .supabase import get_supabase_client

    supabase = get_supabase_client()
    records: List[Dict] = []
    if supabase:
        try:
            resp = (
                supabase.table("videos")
                .select(
                    "transcript,visual_style,onscreen_text,likes,comments"
                )
                .eq("niche", niche)
                .execute()
            )
            records = resp.data or []
        except Exception:
            records = []

    patterns = mine_patterns_from_records(records, niche)

    if supabase and patterns:
        rows = [
            {
                "niche": p.niche,
                "hook": p.hook,
                "core_value_loop": p.core_value_loop,
                "narrative_arc": p.narrative_arc,
                "visual_formula": p.visual_formula,
                "cta": p.cta,
                "prevalence": p.prevalence,
                "engagement_score": p.engagement_score,
            }
            for p in patterns
        ]
        try:
            resp = supabase.table("patterns").insert(rows).execute()
            if resp.data:
                for pat, row in zip(patterns, resp.data):
                    pat.id = row.get("id")
        except Exception:
            pass

    return patterns
