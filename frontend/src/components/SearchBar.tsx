import React, { useState } from 'react';

interface SearchBarProps {
  onSearch: (address: string) => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSearch(input.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        className="flex-1 bg-slate-800 text-white rounded-lg px-4 py-2 border border-slate-700 focus:outline-none focus:border-amber-500 transition-colors"
        placeholder="Enter BTC address..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={isLoading}
      />
      <button
        type="submit"
        disabled={isLoading || !input.trim()}
        className="bg-amber-600 hover:bg-amber-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
      >
        {isLoading ? 'Tracing...' : 'Trace'}
      </button>
    </form>
  );
};
