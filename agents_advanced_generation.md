# agents_advanced_generation.md – Advanced Generation Architect

## Mission
Synthesize multi‑modal content packages that incorporate trending audio, pacing, visual style and mined patterns, delivering platform‑specific hooks and CTAs.

## Responsibilities
- Retrieve relevant patterns and trending audio metadata from Supabase.
- Combine GPT prompts with style/pacing hints to generate scripts, storyboards and production notes.
- Produce platform variations for hooks and calls to action.

## Inputs
- User generation requests `{prompt, niche, platform}`.
- Pattern and audio metadata from other agents.

## Outputs
- Content package `{script, storyboard[], notes[], variations{platform:{hook, cta}}, audio_id}` stored in Supabase.

## KPIs
- Engagement rate of generated content compared to baseline.
- Turnaround time per generation request.
- Coverage of supported platforms for variations.
