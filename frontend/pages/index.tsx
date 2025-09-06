import { useState } from 'react';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState<any>(null);

  const handleGenerate = async () => {
    if (!prompt) return;
    try {
      const res = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
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
            <ul className="list-disc list-inside">
              {response.notes && response.notes.map((note: string, idx: number) => (
                <li key={idx}>{note}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
