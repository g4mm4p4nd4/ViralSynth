-- Migration: ensure patterns table has niche and stats columns
ALTER TABLE IF EXISTS patterns
    ADD COLUMN IF NOT EXISTS niche text,
    ADD COLUMN IF NOT EXISTS prevalence double precision,
    ADD COLUMN IF NOT EXISTS engagement_score double precision;
