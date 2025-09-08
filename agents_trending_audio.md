# agents_trending_audio.md – Trending Audio Analyst

## Mission
Track and evaluate the popularity of audio tracks across the ViralSynth dataset so content creators can leverage the most effective sounds.

## Responsibilities
- Aggregate audio identifiers from ingested videos and compute usage counts.
- Rank audio tracks by frequency and expose top results with source links.
- Surface audio metadata to other agents for strategy and generation.

## Inputs
- Video records stored in Supabase including `audio_id` and `url`.

## Outputs
- Ordered list of trending audio objects `{audio_id, count, url}`.

## KPIs
- Accuracy of ranking compared to ground‑truth datasets.
- Latency of aggregation queries.
- Availability of source links for each trending audio record.
