import { useState } from 'react';

interface GenerateResponse {
  script: string;
  storyboard: string[];
  notes: string[];
  variations: Record<string, string>;
}

interface IngestItem {
  title?: string;
  url?: string;
  transcript?: string;
  analysis?: Record<string, any>;
  error?: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [niche, setNiche] = useState('');
  const [response, setResponse] = useState<GenerateResponse | null>(null);
  const [ingestItems, setIngestItems] = useState<IngestItem[]>([]);
  const [patterns, setPatterns] = useState<string[]>([]);

  const handleIngest = async () => {
    if (!niche) return;
    try {
      const res = await fetch('http://localhost:8000/api/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niches: [niche], top_percentile: 0.05 }),
      });
      const data = await res.json();
      setIngestItems(data.items || []);
    } catch (err) {
      console.error('Ingest failed', err);
    }
  };

  const handleStrategy = async () => {
    if (!niche) return;
    try {
      const res = await fetch('http://localhost:8000/api/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niches: [niche] }),
      });
      const data = await res.json();
      setPatterns(data.patterns || []);
    } catch (err) {
      console.error('Strategy failed', err);
    }
  };

  const handleGenerate = async () => {
    if (!prompt) return;
    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, niche }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      console.error('Failed to generate content package:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-3xl font-bold mb-4 text-center">ViralSynth</h1>
      <div className="max-w-2xl mx-auto">
        <input
          className="w-full p-3 mb-4 rounded bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          type="text"
          placeholder="Niche (e.g. tech, fitness)"
          value={niche}
          onChange={(e) => setNiche(e.target.value)}
        />
        <div className="flex gap-2 mb-6">
          <button
            className="flex-1 bg-purple-600 hover:bg-purple-700 py-2 px-4 rounded"
            onClick={handleIngest}
          >
            Ingest Trends
          </button>
          <button
            className="flex-1 bg-green-600 hover:bg-green-700 py-2 px-4 rounded"
            onClick={handleStrategy}
          >
            Analyze Strategy
          </button>
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

        {ingestItems.length > 0 && (
          <div className="bg-gray-800 p-4 rounded mb-6">
            <h2 className="text-2xl font-semibold mb-2">Ingested Videos</h2>
            <ul className="list-disc list-inside space-y-2">
              {ingestItems.map((item, idx) => (
                <li key={idx}>
                  <a href={item.url} target="_blank" rel="noreferrer" className="text-blue-400 underline">
                    {item.title || item.url}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        {patterns.length > 0 && (
          <div className="bg-gray-800 p-4 rounded mb-6">
            <h2 className="text-2xl font-semibold mb-2">Strategy Patterns</h2>
            <ul className="list-disc list-inside space-y-1">
              {patterns.map((p, idx) => (
                <li key={idx}>{p}</li>
              ))}
            </ul>
          </div>
        )}

        {response && (
          <div className="bg-gray-800 p-4 rounded">
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
                  {Object.entries(response.variations).map(([platform, text]) => (
                    <li key={platform}>
                      <strong>{platform}:</strong> {text}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
