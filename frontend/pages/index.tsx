import { useEffect, useState } from 'react';

interface PlatformVariation {
  hook: string;
  cta: string;
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

interface GenerateResponse {
  script: string;
  storyboard: string[];
  notes: string[];
  variations: Record<string, PlatformVariation>;
  audio?: TrendingAudio;
  package_id?: number;
  pattern_ids?: number[];
  patterns?: Pattern[];
}

export default function Home() {
  const [niche, setNiche] = useState('');
  const [prompt, setPrompt] = useState('');
  const [activeTab, setActiveTab] = useState<'audio' | 'patterns' | 'generate'>('audio');
  const [audioList, setAudioList] = useState<TrendingAudio[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [selectedPatternId, setSelectedPatternId] = useState<string>('auto');
  const [response, setResponse] = useState<GenerateResponse | null>(null);

  useEffect(() => {
    if (activeTab === 'audio') {
      fetchAudio();
    } else if (activeTab === 'patterns') {
      fetchPatterns();
    }
  }, [activeTab, niche]);

  const fetchAudio = async () => {
    if (!niche) return;
    try {
      const res = await fetch(`http://localhost:8000/api/audio/trending?niche=${niche}`);
      const data = await res.json();
      setAudioList(data);
    } catch (err) {
      console.error('Failed to fetch audio', err);
    }
  };

  const fetchPatterns = async () => {
    if (!niche) return;
    try {
      const res = await fetch(`http://localhost:8000/api/patterns?niche=${niche}`);
      const data = await res.json();
      setPatterns(data);
    } catch (err) {
      console.error('Failed to fetch patterns', err);
    }
  };

  const handleGenerate = async () => {
    if (!prompt) return;
    if (!patterns.length && niche) await fetchPatterns();
    const payload: any = { prompt };
    if (niche) payload.niche = niche;
    if (selectedPatternId !== 'auto') {
      payload.pattern_ids = [Number(selectedPatternId)];
    }
    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error('Failed to generate', err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-4 text-center">ViralSynth</h1>
      <div className="max-w-3xl mx-auto">
        <div className="flex space-x-4 mb-4">
          {['audio', 'patterns', 'generate'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-2 rounded ${
                activeTab === tab ? 'bg-blue-600' : 'bg-gray-700'
              }`}
            >
              {tab === 'audio' && 'Trending Audio'}
              {tab === 'patterns' && 'Patterns'}
              {tab === 'generate' && 'Generate'}
            </button>
          ))}
        </div>

        <input
          className="w-full p-2 mb-4 rounded bg-gray-800 border border-gray-700"
          type="text"
          placeholder="Niche (e.g., tech, fitness)"
          value={niche}
          onChange={(e) => setNiche(e.target.value)}
        />

        {activeTab === 'audio' && (
          <div>
            <ul className="space-y-2">
              {audioList.map((a) => (
                <li key={a.audio_id} className="bg-gray-800 p-2 rounded text-sm">
                  <a href={a.url} target="_blank" rel="noreferrer" className="underline">
                    {a.audio_id}
                  </a>{' '}
                  – used {a.count} times
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'patterns' && (
          <div>
            <ul className="space-y-3">
              {patterns.map((p) => (
                <li key={p.id} className="bg-gray-800 p-3 rounded">
                  <div className="text-sm mb-2">ID: {p.id}</div>
                  <p className="text-xs">Hook: {p.hook}</p>
                  <button
                    className="mt-2 bg-blue-600 px-2 py-1 rounded"
                    onClick={() => setSelectedPatternId(String(p.id))}
                  >
                    Use this pattern
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'generate' && (
          <div>
            <input
              className="w-full p-2 mb-4 rounded bg-gray-800 border border-gray-700"
              type="text"
              placeholder="Enter your content idea..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <div className="mb-4">
              <label className="block text-sm mb-1">Pattern Override</label>
              <select
                className="w-full p-2 bg-gray-700 rounded"
                value={selectedPatternId}
                onChange={(e) => setSelectedPatternId(e.target.value)}
              >
                <option value="auto">Auto-select</option>
                {patterns.map((p) => (
                  <option key={p.id} value={p.id}>{p.id}</option>
                ))}
              </select>
            </div>
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded mb-6 w-full"
              onClick={handleGenerate}
            >
              Generate Content Package
            </button>

            {response && (
              <div className="bg-gray-800 p-4 rounded">
                {response.audio && (
                  <p className="text-xs mb-2">
                    Audio: <a href={response.audio.url} className="underline" target="_blank" rel="noreferrer">{response.audio.audio_id}</a>
                  </p>
                )}
                <h2 className="text-2xl font-semibold mb-2">Generated Script</h2>
                <p className="mb-4 whitespace-pre-line">{response.script}</p>
                <h2 className="text-2xl font-semibold mb-2">Storyboard</h2>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  {response.storyboard.map((img, idx) => (
                    <img key={idx} src={img} alt={`frame-${idx}`} className="rounded" />
                  ))}
                </div>
                <h2 className="text-2xl font-semibold mb-2">Production Notes</h2>
                <ul className="list-disc list-inside mb-4">
                  {response.notes.map((note, idx) => (
                    <li key={idx}>{note}</li>
                  ))}
                </ul>
                {response.variations && (
                  <div className="mb-4">
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
                {response.patterns && response.patterns.length > 0 && (
                  <div className="mb-4">
                    <h2 className="text-2xl font-semibold mb-2">Patterns Used</h2>
                    <ul className="list-disc list-inside text-sm">
                      {response.patterns.map((p) => (
                        <li key={p.id}>Hook: {p.hook}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {response.package_id && (
                  <p className="text-xs">Package ID: {response.package_id}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
