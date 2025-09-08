import { useState } from 'react';

interface PlatformVariation {
  hook: string;
  cta: string;
}

interface GenerateResponse {
  script: string;
  storyboard: string[];
  notes: string[];
  variations: Record<string, PlatformVariation>;
  audio_id?: string;
  audio_url?: string;
  package_id?: number;
  pattern_ids?: number[];
}

interface VideoRecord {
  id?: number;
  url?: string;
  pacing?: number;
  visual_style?: string;
  onscreen_text?: string;
  audio_id?: string;
  audio_url?: string;
   audio_hash?: string;
   likes?: number;
   comments?: number;
  trending_audio?: boolean;
}

interface Pattern {
  id?: number;
  hook: string;
  core_value_loop: string;
  narrative_arc: string;
  visual_formula: string;
  cta: string;
  prevalence?: number;
  engagement_score?: number;
}

interface TrendingAudio {
  audio_id: string;
  audio_hash: string;
  count: number;
  avg_engagement: number;
  url?: string;
  niche?: string;
}

interface IngestResponse {
  message: string;
  video_ids: number[];
  videos: VideoRecord[];
  patterns: Pattern[];
  pattern_ids: number[];
  trending_audios: TrendingAudio[];
  generated?: GenerateResponse;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [niche, setNiche] = useState('');
  const [provider, setProvider] = useState('apify');
  const [ingestData, setIngestData] = useState<IngestResponse | null>(null);
  const [response, setResponse] = useState<GenerateResponse | null>(null);
  const [selectedPatternId, setSelectedPatternId] = useState<string>('auto');

  const selectedPattern =
    selectedPatternId !== 'auto'
      ? ingestData?.patterns.find((p) => p.id === Number(selectedPatternId))
      : null;

  // Calls the backend to generate a placeholder content package
  const handleGenerate = async () => {
    if (!prompt) return;
    try {
      const payload: any = { prompt };
      if (niche) payload.niche = niche;
      if (selectedPatternId !== 'auto') {
        payload.pattern_ids = [Number(selectedPatternId)];
      } else if (ingestData?.pattern_ids?.length) {
        payload.pattern_ids = ingestData.pattern_ids;
      }
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Failed to generate content package:', error);
    }
  };

  // Calls the backend ingestion endpoint with selected provider
  const handleIngest = async () => {
    if (!niche) return;
    try {
      const res = await fetch('http://localhost:8000/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niches: [niche], top_percentile: 0.05, provider }),
      });
      const data = await res.json();
      setIngestData(data);
    } catch (error) {
      console.error('Failed to ingest content:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-4 text-center">ViralSynth</h1>
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <input
            className="w-full p-3 mb-4 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
            type="text"
            placeholder="Enter a niche (e.g. tech)..."
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
          />
          <select
            className="w-full p-3 mb-4 rounded bg-gray-800 border border-gray-700 focus:outline-none"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          >
            <option value="apify">Apify</option>
            <option value="playwright">Playwright</option>
            <option value="puppeteer">Puppeteer</option>
          </select>
          <button
            className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded w-full transition-colors"
            onClick={handleIngest}
          >
            Ingest Trending Content
          </button>
          {ingestData?.message && (
            <p className="mt-2 text-sm text-center">{ingestData.message}</p>
          )}
          {ingestData?.video_ids && ingestData.video_ids.length > 0 && (
            <p className="mt-1 text-xs text-center">Stored videos: {ingestData.video_ids.join(', ')}</p>
          )}
          {ingestData?.trending_audios && ingestData.trending_audios.length > 0 && (
            <div className="mt-2 text-xs text-center">
              Top audio:
              {ingestData.trending_audios.map((a, idx) => (
                <span key={a.audio_id} className="block">
                  {idx + 1}. <a href={a.url} className="underline" target="_blank" rel="noreferrer">{a.audio_id}</a> ({a.count} uses, avg engagement {a.avg_engagement.toFixed(1)})
                </span>
              ))}
            </div>
          )}
          {ingestData?.videos && ingestData.videos.length > 0 && (
            <div className="mt-4 bg-gray-800 p-4 rounded">
              <h2 className="text-2xl font-semibold mb-2">Video Analysis</h2>
              <ul className="list-disc list-inside">
                {ingestData.videos.map((v, idx) => (
                  <li key={idx} className="mb-2">
                    <div>
                      Pacing: {v.pacing ?? 'n/a'}s, Style: {v.visual_style ?? 'n/a'}{v.trending_audio ? ' (Trending audio)' : ''}
                    </div>
                    {v.audio_id && (
                      <div className="text-xs">
                        Audio: <a href={v.audio_url} className="underline" target="_blank" rel="noreferrer">{v.audio_id}</a>
                      </div>
                    )}
                    {v.onscreen_text && <div className="text-xs">Text: {v.onscreen_text}</div>}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {ingestData?.patterns && ingestData.patterns.length > 0 && (
            <div className="mt-4 bg-gray-800 p-4 rounded">
              <h2 className="text-2xl font-semibold mb-2">Strategy Results</h2>
              {ingestData.patterns.map((p, idx) => (
                <div key={idx} className="mb-3">
                  <div className="font-semibold">Pattern {p.id ?? idx + 1}</div>
                  <ul className="list-disc list-inside text-sm">
                    <li>Hook: {p.hook}</li>
                    <li>Value Loop: {p.core_value_loop}</li>
                    <li>Narrative: {p.narrative_arc}</li>
                    <li>Visual: {p.visual_formula}</li>
                    <li>CTA: {p.cta}</li>
                    {p.prevalence && (
                      <li>Prevalence: {p.prevalence}</li>
                    )}
                    {p.engagement_score && (
                      <li>Engagement: {p.engagement_score.toFixed(1)}</li>
                    )}
                  </ul>
                </div>
              ))}
              <select
                className="w-full p-2 mt-2 bg-gray-700 rounded"
                value={selectedPatternId}
                onChange={(e) => setSelectedPatternId(e.target.value)}
              >
                <option value="auto">Auto-select pattern</option>
                {ingestData.patterns.map((p) => (
                  <option key={p.id} value={p.id}>{p.id}</option>
                ))}
              </select>
            </div>
          )}
          {ingestData?.generated && (
            <div className="mt-4 bg-gray-800 p-4 rounded">
              <h2 className="text-2xl font-semibold mb-2">Generated Script</h2>
              {ingestData.generated.audio_id && (
                <p className="text-xs mb-2">
                  Audio: <a href={ingestData.generated.audio_url} className="underline" target="_blank" rel="noreferrer">{ingestData.generated.audio_id}</a>
                </p>
              )}
              <p className="mb-4 whitespace-pre-line">{ingestData.generated.script}</p>
              <h2 className="text-2xl font-semibold mb-2">Storyboard</h2>
              <div className="grid grid-cols-2 gap-4 mb-4">
                {ingestData.generated.storyboard.map((img, idx) => (
                  <img key={idx} src={img} alt={`ingest-frame-${idx}`} className="rounded" />
                ))}
              </div>
              <h2 className="text-2xl font-semibold mb-2">Production Notes</h2>
              <ul className="list-disc list-inside mb-4">
                {ingestData.generated.notes.map((note, idx) => (
                  <li key={idx}>{note}</li>
                ))}
              </ul>
              {ingestData.generated.variations && (
                <div>
                  <h2 className="text-2xl font-semibold mb-2">Platform Variations</h2>
                  <ul className="list-disc list-inside">
                    {Object.entries(ingestData.generated.variations).map(
                      ([platform, pv]) => (
                        <li key={platform}>
                          <strong>{platform}:</strong> Hook - {pv.hook}; CTA - {pv.cta}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}
              {ingestData.generated.package_id && (
                <p className="text-xs mt-2">Package ID: {ingestData.generated.package_id}</p>
              )}
            </div>
          )}
        </div>

        <input
          className="w-full p-3 mb-4 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          type="text"
          placeholder="Enter your content idea..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded mb-6 w-full transition-colors"
          onClick={handleGenerate}
        >
          Generate Content Package
        </button>

            {response && (
              <div className="bg-gray-800 p-4 rounded">
            {response.audio_id && (
              <p className="text-sm mb-2">
                Audio: <a href={response.audio_url} className="underline" target="_blank" rel="noreferrer">{response.audio_id}</a>
              </p>
            )}
            <h2 className="text-2xl font-semibold mb-2">Generated Script</h2>
            <p className="mb-4 whitespace-pre-line">{response.script}</p>
            <h2 className="text-2xl font-semibold mb-2">Storyboard</h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              {response.storyboard && response.storyboard.map((img: string, idx: number) => (
                <img key={idx} src={img} alt={`frame-${idx}`} className="rounded" />
              ))}
            </div>
            <h2 className="text-2xl font-semibold mb-2">Production Notes</h2>
            <ul className="list-disc list-inside mb-4">
              {response.notes && response.notes.map((note: string, idx: number) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
            {response.variations && (
              <div>
                <h2 className="text-2xl font-semibold mb-2">Platform Variations</h2>
                <ul className="list-disc list-inside">
                  {Object.entries(response.variations).map(([platform, pv]) => (
                    <li key={platform}>
                      <strong>{platform}:</strong> Hook - {pv.hook}; CTA - {pv.cta}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {selectedPattern && (
              <div className="mt-4">
                <h2 className="text-2xl font-semibold mb-2">Selected Pattern</h2>
                <ul className="list-disc list-inside text-sm">
                  <li>Hook: {selectedPattern.hook}</li>
                  <li>Value Loop: {selectedPattern.core_value_loop}</li>
                  <li>Narrative: {selectedPattern.narrative_arc}</li>
                  <li>Visual: {selectedPattern.visual_formula}</li>
                  <li>CTA: {selectedPattern.cta}</li>
                </ul>
              </div>
            )}
            {response.package_id && (
              <p className="text-xs mt-2">Package ID: {response.package_id}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
