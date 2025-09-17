CREATE TABLE IF NOT EXISTS audio_daily_rankings (
    id SERIAL PRIMARY KEY,
    ranking_date DATE NOT NULL,
    niche TEXT,
    audio_id TEXT NOT NULL,
    audio_hash TEXT,
    url TEXT,
    count INTEGER DEFAULT 0,
    avg_engagement DOUBLE PRECISION DEFAULT 0,
    rank INTEGER,
    UNIQUE (ranking_date, niche, audio_id)
);
