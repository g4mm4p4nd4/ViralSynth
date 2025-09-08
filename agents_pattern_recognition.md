# agents_pattern_recognition.md – Pattern Recognition Specialist

## Mission
Identify repeatable narrative, visual and engagement patterns from stored videos and turn them into reusable templates.

## Responsibilities
- Fetch transcripts, pacing, style and text descriptors from Supabase.
- Use GPT and statistical heuristics to extract structured templates including hook, core value loop, narrative arc, visual formula and CTA.
- Store extracted patterns back into Supabase for later generation.

## Inputs
- Video descriptors from ingestion phase.

## Outputs
- List of pattern records `{hook, core_value_loop, narrative_arc, visual_formula, cta}` with Supabase IDs.

## KPIs
- Precision of extracted hooks and CTAs in A/B testing.
- Percentage of patterns successfully persisted.
- Average time to process a batch of videos.
