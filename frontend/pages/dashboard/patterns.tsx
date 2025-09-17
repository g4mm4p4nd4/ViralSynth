import { useMemo, useState } from 'react';
import useSWR from 'swr';

import { Pattern } from '../../types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
};

export default function PatternsDashboard() {
  const [niche, setNiche] = useState('');
  const [limit, setLimit] = useState(20);
  const [sortKey, setSortKey] = useState<'prevalence' | 'engagement'>('prevalence');

  const query = useMemo(() => {
    const params = new URLSearchParams();
    if (niche) params.set('niche', niche);
    params.set('limit', String(limit));
    return `${API_BASE}/api/patterns?${params.toString()}`;
  }, [niche, limit]);

  const { data, error, isLoading } = useSWR<Pattern[]>(query, fetcher, {
    revalidateOnFocus: false,
  });

  const sorted = useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => {
      const aValue = sortKey === 'prevalence' ? a.prevalence ?? 0 : a.engagement_score ?? 0;
      const bValue = sortKey === 'prevalence' ? b.prevalence ?? 0 : b.engagement_score ?? 0;
      return bValue - aValue;
    });
  }, [data, sortKey]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Pattern Insights</h1>
        <div className="grid gap-4 md:grid-cols-3 mb-6 bg-gray-800 rounded-lg p-4">
          <label className="flex flex-col text-sm">
            Niche
            <input
              value={niche}
              onChange={(event) => setNiche(event.target.value)}
              placeholder="e.g. fitness"
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="flex flex-col text-sm">
            Limit
            <input
              type="number"
              min={1}
              max={100}
              value={limit}
              onChange={(event) => setLimit(Math.max(1, Number(event.target.value) || 1))}
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="flex flex-col text-sm">
            Sort By
            <select
              value={sortKey}
              onChange={(event) => setSortKey(event.target.value as 'prevalence' | 'engagement')}
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="prevalence">Prevalence</option>
              <option value="engagement">Engagement</option>
            </select>
          </label>
        </div>

        {isLoading && <p className="text-gray-300">Loading patterns...</p>}
        {error && <p className="text-red-400 text-sm">Failed to load patterns. Ensure the backend API is reachable.</p>}

        {sorted.length > 0 ? (
          <div className="grid gap-4">
            {sorted.map((pattern) => (
              <div key={pattern.id ?? pattern.hook} className="bg-gray-800 rounded-lg p-4 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-xl font-semibold">{pattern.hook}</h2>
                  <div className="text-sm text-gray-400">
                    <span className="mr-4">Prevalence: {(pattern.prevalence ?? 0).toFixed(2)}</span>
                    <span>Engagement: {(pattern.engagement_score ?? 0).toFixed(2)}</span>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-gray-200">
                  <div>
                    <span className="font-semibold">Value Loop:</span> {pattern.core_value_loop}
                  </div>
                  <div>
                    <span className="font-semibold">Narrative Arc:</span> {pattern.narrative_arc}
                  </div>
                  <div>
                    <span className="font-semibold">Visual Formula:</span> {pattern.visual_formula}
                  </div>
                  <div>
                    <span className="font-semibold">CTA:</span> {pattern.cta}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          !isLoading && !error && <p className="text-gray-400">No patterns found for the selected filters.</p>
        )}
      </div>
    </div>
  );
}
