import { useMemo, useState } from 'react';
import useSWR from 'swr';

import { TrendingAudio } from '../../types/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }
  return response.json();
};

export default function AudioDashboard() {
  const [niche, setNiche] = useState('');
  const [limit, setLimit] = useState(10);
  const [days, setDays] = useState(1);

  const query = useMemo(() => {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    if (niche) params.set('niche', niche);
    if (days > 0) {
      const target = new Date();
      target.setDate(target.getDate() - (days - 1));
      params.set('date', target.toISOString().slice(0, 10));
    }
    return `${API_BASE}/api/audio/trending?${params.toString()}`;
  }, [niche, limit, days]);

  const { data, error, isLoading } = useSWR<TrendingAudio[]>(query, fetcher, {
    revalidateOnFocus: false,
  });

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Trending Audio</h1>
        <div className="grid gap-4 md:grid-cols-3 mb-6 bg-gray-800 rounded-lg p-4">
          <label className="flex flex-col text-sm">
            Niche
            <input
              value={niche}
              onChange={(event) => setNiche(event.target.value)}
              placeholder="e.g. tech"
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="flex flex-col text-sm">
            Limit
            <input
              type="number"
              min={1}
              max={50}
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value) || 1)}
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
          <label className="flex flex-col text-sm">
            Lookback Days
            <input
              type="number"
              min={1}
              max={30}
              value={days}
              onChange={(event) => setDays(Math.max(1, Number(event.target.value) || 1))}
              className="mt-1 rounded bg-gray-900 border border-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>
        </div>

        {isLoading && <p className="text-gray-300">Loading trending audio...</p>}
        {error && (
          <p className="text-red-400 text-sm">Failed to load audio. Please verify the backend is running.</p>
        )}

        {data && data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-800">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-gray-400">
                  <th className="px-4 py-2">Rank</th>
                  <th className="px-4 py-2">Audio ID</th>
                  <th className="px-4 py-2">Niche</th>
                  <th className="px-4 py-2">Usage Count</th>
                  <th className="px-4 py-2">Avg Engagement</th>
                  <th className="px-4 py-2">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {data.map((audio, index) => (
                  <tr key={`${audio.audio_id}-${index}`} className="hover:bg-gray-800/70">
                    <td className="px-4 py-2 text-sm">{index + 1}</td>
                    <td className="px-4 py-2 text-sm font-semibold">{audio.audio_id}</td>
                    <td className="px-4 py-2 text-sm">{audio.niche ?? '—'}</td>
                    <td className="px-4 py-2 text-sm">{audio.count}</td>
                    <td className="px-4 py-2 text-sm">{audio.avg_engagement.toFixed(1)}</td>
                    <td className="px-4 py-2 text-sm">
                      {audio.url ? (
                        <a
                          href={audio.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-400 hover:text-blue-300"
                        >
                          Open
                        </a>
                      ) : (
                        <span className="text-gray-500">n/a</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !isLoading && !error && (
            <p className="text-gray-400">No audio rankings available for the selected filters.</p>
          )
        )}
      </div>
    </div>
  );
}
