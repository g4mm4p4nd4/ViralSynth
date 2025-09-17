import { FormEvent, useState } from 'react';

import { GenerateRequestPayload, GenerateResponse } from '../../types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export default function GenerateDashboard() {
  const [prompt, setPrompt] = useState('Break down the latest AI automation trends.');
  const [niche, setNiche] = useState('tech');
  const [patternInput, setPatternInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<GenerateResponse | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    const payload: GenerateRequestPayload = { prompt };
    if (niche.trim()) payload.niche = niche.trim();
    if (patternInput.trim()) {
      const parsed = patternInput
        .split(',')
        .map((value) => Number(value.trim()))
        .filter((value) => !Number.isNaN(value));
      if (parsed.length > 0) payload.pattern_ids = parsed;
    }

    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`);
      }
      const data = (await res.json()) as GenerateResponse;
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
      setResponse(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Generate Package</h1>
        <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg p-6 space-y-4 shadow-lg">
          <label className="block text-sm">
            Prompt
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              className="mt-1 w-full rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Describe the content you want to generate"
              required
            />
          </label>
          <label className="block text-sm">
            Niche
            <input
              value={niche}
              onChange={(event) => setNiche(event.target.value)}
              className="mt-1 w-full rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. tech"
            />
          </label>
          <label className="block text-sm">
            Override Pattern IDs (comma separated)
            <input
              value={patternInput}
              onChange={(event) => setPatternInput(event.target.value)}
              className="mt-1 w-full rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. 12, 24"
            />
          </label>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-wait text-white font-semibold py-3 rounded"
          >
            {isLoading ? 'Generating...' : 'Generate Package'}
          </button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </form>

        {response && (
          <div className="mt-8 space-y-6">
            <section className="bg-gray-800 rounded-lg p-6 shadow">
              <h2 className="text-2xl font-semibold mb-3">Script</h2>
              <p className="whitespace-pre-wrap text-gray-100 text-sm leading-relaxed">{response.script}</p>
            </section>

            <section className="bg-gray-800 rounded-lg p-6 shadow">
              <h2 className="text-2xl font-semibold mb-3">Storyboard</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {response.storyboard.map((url, index) => (
                  <div key={url ?? index} className="bg-gray-900 rounded p-3 text-sm text-gray-300">
                    <span className="block font-semibold mb-2">Frame {index + 1}</span>
                    <a href={url} target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300 break-all">
                      {url}
                    </a>
                  </div>
                ))}
              </div>
            </section>

            <section className="bg-gray-800 rounded-lg p-6 shadow">
              <h2 className="text-2xl font-semibold mb-3">Production Notes</h2>
              <ul className="list-disc list-inside text-sm text-gray-200 space-y-1">
                {response.notes.map((note, index) => (
                  <li key={`${note}-${index}`}>{note}</li>
                ))}
              </ul>
            </section>

            {response.why && (
              <section className="bg-gray-800 rounded-lg p-6 shadow space-y-4">
                <h2 className="text-2xl font-semibold">Why these choices?</h2>
                <div className="grid gap-4 md:grid-cols-2 text-sm text-gray-200">
                  <div className="bg-gray-900 rounded p-4">
                    <h3 className="text-lg font-semibold mb-2">Pattern Selection</h3>
                    <p className="mb-1 text-gray-300">{response.why.pattern.explanation}</p>
                    <p className="text-xs text-gray-400">
                      Score: {response.why.pattern.score.toFixed(2)} • Prevalence: {response.why.pattern.prevalence.toFixed(2)} •
                      Engagement: {response.why.pattern.engagement_score.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-gray-900 rounded p-4">
                    <h3 className="text-lg font-semibold mb-2">Audio Selection</h3>
                    <p className="mb-1 text-gray-300">{response.why.audio.explanation}</p>
                    <p className="text-xs text-gray-400">
                      Score: {response.why.audio.score.toFixed(2)} • Usage: {response.why.audio.usage_count} • Engagement:
                      {response.why.audio.avg_engagement.toFixed(1)}
                    </p>
                  </div>
                </div>
              </section>
            )}

            <section className="bg-gray-800 rounded-lg p-6 shadow">
              <h2 className="text-2xl font-semibold mb-3">Platform Variations</h2>
              {Object.entries(response.variations).length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 text-sm text-gray-200">
                  {Object.entries(response.variations).map(([platform, variation]) => (
                    <div key={platform} className="bg-gray-900 rounded p-4">
                      <h3 className="text-lg font-semibold mb-2 capitalize">{platform}</h3>
                      <p className="mb-1 text-gray-300">Hook: {variation.hook}</p>
                      <p className="text-gray-300">CTA: {variation.cta}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">No platform variations returned.</p>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
