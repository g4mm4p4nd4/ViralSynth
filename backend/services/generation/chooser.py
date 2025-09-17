"""Deterministic chooser for selecting optimal patterns and audio."""

from __future__ import annotations

from typing import Any

from ...models import Pattern, TrendingAudio

_PATTERN_PREVALENCE_WEIGHT = 0.6
_PATTERN_ENGAGEMENT_WEIGHT = 0.4
_AUDIO_USAGE_WEIGHT = 0.4
_AUDIO_ENGAGEMENT_WEIGHT = 0.6


def _pattern_score(pattern: Pattern) -> float:
    prevalence = pattern.prevalence or 0.0
    engagement = pattern.engagement_score or 0.0
    return (prevalence * _PATTERN_PREVALENCE_WEIGHT) + (
        engagement * _PATTERN_ENGAGEMENT_WEIGHT
    )


def _audio_score(audio: TrendingAudio) -> float:
    usage = audio.count or 0
    engagement = audio.avg_engagement or 0.0
    return (usage * _AUDIO_USAGE_WEIGHT) + (
        engagement * _AUDIO_ENGAGEMENT_WEIGHT
    )


def _pattern_reason(pattern: Pattern, score: float) -> dict[str, Any]:
    return {
        "pattern_id": pattern.id,
        "hook": pattern.hook,
        "prevalence": pattern.prevalence or 0.0,
        "engagement_score": pattern.engagement_score or 0.0,
        "score": score,
        "explanation": (
            "Weighted prevalence (60%) and engagement (40%) produced the top pattern"
        ),
    }


def _audio_reason(audio: TrendingAudio, score: float) -> dict[str, Any]:
    return {
        "audio_id": audio.audio_id,
        "usage_count": audio.count,
        "avg_engagement": audio.avg_engagement,
        "score": score,
        "explanation": (
            "Weighted usage (40%) and engagement (60%) yielded the top audio"
        ),
    }


def choose(
    niche: str | None,
    patterns: list[Pattern],
    audios: list[TrendingAudio],
) -> tuple[Pattern, TrendingAudio, dict[str, Any]]:
    """Select the best pattern and audio and describe why they were chosen."""

    if not patterns:
        patterns = [
            Pattern(
                id=None,
                hook=f"High-performing hook for {niche or 'general'} creators",
                core_value_loop="Deliver three rapid-fire insights with proof points.",
                narrative_arc="Start with a bold claim, validate with evidence, close with CTA.",
                visual_formula="Talking head with dynamic text overlays",
                cta="Follow for more breakdowns",
                prevalence=0.0,
                engagement_score=0.0,
            )
        ]
    if not audios:
        audios = [
            TrendingAudio(
                audio_id="fallback-audio",
                audio_hash="",
                count=0,
                avg_engagement=0.0,
                url=None,
                niche=niche,
            )
        ]

    best_pattern = max(patterns, key=_pattern_score)
    best_audio = max(audios, key=_audio_score)

    pattern_score = _pattern_score(best_pattern)
    audio_score = _audio_score(best_audio)

    why: dict[str, Any] = {
        "pattern": _pattern_reason(best_pattern, pattern_score),
        "audio": _audio_reason(best_audio, audio_score),
    }

    return best_pattern, best_audio, why
