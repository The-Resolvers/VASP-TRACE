import React, { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { GraphVisualizer } from './components/visualization/GraphVisualizer';
import { VaspLeaderboard } from './components/VaspLeaderboard';
import { TraceResult } from './types/trace.types';
import mockData from './data/mock_trace.json';

function App() {
  const [traceData, setTraceData] = useState<TraceResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (address: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/trace/${address}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTraceData(data as TraceResult);
    } catch (error) {
      console.error("Failed to fetch trace from backend:", error);
      alert("Failed to connect to backend API. Please make sure the Python server is running.");
      // Fallback to mock data for demonstration
      setTraceData(mockData as TraceResult);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-400 to-orange-500">
            VASP Trace Engine
          </h1>
          <div className="w-1/3">
            <SearchBar onSearch={handleSearch} isLoading={loading} />
          </div>
        </header>

        {traceData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[800px]">
            <div className="col-span-2 bg-slate-800 rounded-xl p-4 shadow-xl border border-slate-700">
              <h2 className="text-xl font-semibold mb-4 text-slate-300">Transaction Graph</h2>
              <GraphVisualizer data={traceData} />
            </div>
            
            <div className="col-span-1 bg-slate-800 rounded-xl p-4 shadow-xl border border-slate-700 overflow-y-auto">
              <h2 className="text-xl font-semibold mb-4 text-slate-300">VASP Candidates</h2>
              <VaspLeaderboard candidates={traceData.leaderboard} />
            </div>
          </div>
        )}

        {!traceData && !loading && (
          <div className="h-[600px] flex items-center justify-center border-2 border-dashed border-slate-700 rounded-xl">
            <p className="text-slate-500 text-lg">Enter a wallet address to begin tracing.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
