import math

from backend.services.pattern_miner import mine_patterns_from_records


def test_mine_patterns_from_records_groups_and_stats():
    records = [
        {
            "transcript": "Try this growth hack. Step one post daily. Follow for more tips.",
            "visual_style": "lofi",
            "likes": 10,
            "comments": 5,
        },
        {
            "transcript": "Try this growth hack. Step one post daily. Follow for more tips.",
            "visual_style": "lofi",
            "likes": 20,
            "comments": 10,
        },
        {
            "transcript": "Here is my story. I failed once. Now I teach others. Subscribe for more.",
            "visual_style": "cinematic",
            "likes": 5,
            "comments": 0,
        },
    ]

    patterns = mine_patterns_from_records(records, niche="marketing")
    assert len(patterns) == 2

    # Find first pattern with hook 'Try this growth hack'
    p1 = next(p for p in patterns if p.hook == "Try this growth hack")
    assert math.isclose(p1.prevalence, 2 / 3, rel_tol=1e-5)
    assert math.isclose(p1.engagement_score, 22.5, rel_tol=1e-5)
    assert p1.narrative_arc == "informational"
    assert p1.visual_formula == "lofi"

    # Second pattern stats
    p2 = next(p for p in patterns if p.hook == "Here is my story")
    assert math.isclose(p2.prevalence, 1 / 3, rel_tol=1e-5)
    assert math.isclose(p2.engagement_score, 5.0, rel_tol=1e-5)
    assert p2.narrative_arc == "story"
