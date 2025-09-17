export interface PlatformVariation {
  hook: string;
  cta: string;
}

export interface Pattern {
  id?: number;
  hook: string;
  core_value_loop: string;
  narrative_arc: string;
  visual_formula: string;
  cta: string;
  prevalence?: number;
  engagement_score?: number;
}

export interface TrendingAudio {
  audio_id: string;
  audio_hash: string;
  count: number;
  avg_engagement: number;
  url?: string;
  niche?: string;
}

export interface PatternWhy {
  pattern_id: number | null;
  hook: string;
  prevalence: number;
  engagement_score: number;
  score: number;
  explanation: string;
}

export interface AudioWhy {
  audio_id: string;
  usage_count: number;
  avg_engagement: number;
  score: number;
  explanation: string;
}

export interface GenerateWhy {
  pattern: PatternWhy;
  audio: AudioWhy;
}

export interface GenerateResponse {
  script: string;
  storyboard: string[];
  notes: string[];
  variations: Record<string, PlatformVariation>;
  audio_id?: string;
  audio_url?: string;
  package_id?: number;
  pattern_ids?: number[];
  why?: GenerateWhy;
}

export interface GenerateRequestPayload {
  prompt: string;
  niche?: string;
  pattern_ids?: number[];
}

export interface PaginatedError {
  message: string;
}
