"""Tests for the deterministic chooser logic used during generation."""

import pytest

from backend.models import Pattern, TrendingAudio
from backend.services.generation.chooser import choose


def test_choose_selects_highest_weighted_pattern_and_audio():
    patterns = [
        Pattern(
            id=1,
            hook="Hook one",
            core_value_loop="Value",
            narrative_arc="Arc",
            visual_formula="Visual",
            cta="CTA",
            prevalence=0.2,
            engagement_score=0.8,
        ),
        Pattern(
            id=2,
            hook="Hook two",
            core_value_loop="Value",
            narrative_arc="Arc",
            visual_formula="Visual",
            cta="CTA",
            prevalence=0.5,
            engagement_score=0.5,
        ),
        Pattern(
            id=3,
            hook="Hook three",
            core_value_loop="Value",
            narrative_arc="Arc",
            visual_formula="Visual",
            cta="CTA",
            prevalence=0.7,
            engagement_score=0.6,
        ),
    ]
    audios = [
        TrendingAudio(
            audio_id="audio-a",
            audio_hash="hash-a",
            count=10,
            avg_engagement=50,
            url="https://example.com/a",
            niche="tech",
        ),
        TrendingAudio(
            audio_id="audio-b",
            audio_hash="hash-b",
            count=12,
            avg_engagement=80,
            url="https://example.com/b",
            niche="tech",
        ),
    ]

    pattern, audio, why = choose("tech", patterns, audios)

    assert pattern.id == 3
    assert audio.audio_id == "audio-b"
    assert why["pattern"]["pattern_id"] == 3
    assert why["audio"]["audio_id"] == "audio-b"
    assert why["pattern"]["score"] == pytest.approx(0.66, rel=1e-2)
    assert why["audio"]["score"] == pytest.approx(52.8, rel=1e-2)
    assert "Weighted prevalence" in why["pattern"]["explanation"]
    assert "Weighted usage" in why["audio"]["explanation"]


def test_choose_returns_fallbacks_when_empty():
    pattern, audio, why = choose(None, [], [])

    assert pattern.hook.startswith("High-performing hook")
    assert audio.audio_id == "fallback-audio"
    assert why["pattern"]["score"] == 0
    assert why["audio"]["score"] == 0
