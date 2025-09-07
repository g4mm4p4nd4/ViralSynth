import { useState } from 'react';

interface GenerateResponse {
  script: string;
  storyboard: string[];
  notes: string[];
  variations: Record<string, string>;
  package_id?: number;
}

interface IngestResponse {
  message: string;
  video_ids: number[];
  patterns: string[];
  pattern_ids: number[];
  generated?: GenerateResponse;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [niche, setNiche] = useState('');
  const [provider, setProvider] = useState('apify');
  const [ingestData, setIngestData] = useState<IngestResponse | null>(null);
  const [response, setResponse] = useState<GenerateResponse | null>(null);

  // Calls the backend to generate a placeholder content package
  const handleGenerate = async () => {
    if (!prompt) return;
    try {
      const payload: any = { prompt };
      if (niche) payload.niche = niche;
      if (ingestData?.pattern_ids?.length) {
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
          {ingestData?.patterns && ingestData.patterns.length > 0 && (
            <div className="mt-4 bg-gray-800 p-4 rounded">
              <h2 className="text-2xl font-semibold mb-2">Strategy Results</h2>
              <ul className="list-disc list-inside">
                {ingestData.patterns.map((pattern, idx) => (
                  <li key={idx}>{pattern}</li>
                ))}
              </ul>
              {ingestData.pattern_ids && ingestData.pattern_ids.length > 0 && (
                <p className="text-xs mt-2">Pattern IDs: {ingestData.pattern_ids.join(', ')}</p>
              )}
            </div>
          )}
          {ingestData?.generated && (
            <div className="mt-4 bg-gray-800 p-4 rounded">
              <h2 className="text-2xl font-semibold mb-2">Generated Script</h2>
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
                      ([platform, text]) => (
                        <li key={platform}>
                          <strong>{platform}:</strong> {text}
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
            {response.package_id && (
              <p className="text-xs mt-2">Package ID: {response.package_id}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
