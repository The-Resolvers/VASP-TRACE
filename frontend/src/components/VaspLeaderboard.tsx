import React from 'react';
import { LeaderboardEntry } from '../types/trace.types';

interface VaspLeaderboardProps {
  candidates: LeaderboardEntry[];
}

export const VaspLeaderboard: React.FC<VaspLeaderboardProps> = ({ candidates }) => {
  if (candidates.length === 0) {
    return <p className="text-slate-500 text-sm">No exchanges found in trace.</p>;
  }

  return (
    <div className="space-y-4">
      {candidates.map((candidate, idx) => (
        <div key={candidate.address} className="bg-slate-900 rounded-lg p-4 border border-slate-700">
          <div className="flex justify-between items-start mb-2">
            <div>
              <span className="text-xs font-mono text-slate-500 block">#{idx + 1} Candidate</span>
              <h3 className="text-lg font-bold text-green-400">{candidate.vasp_name}</h3>
            </div>
            <div className="text-right">
              <span className="text-2xl font-bold text-white">{(candidate.confidence * 100).toFixed(1)}%</span>
              <span className="text-xs text-slate-400 block">{candidate.hop} hops away</span>
            </div>
          </div>
          
          <div className="text-xs font-mono text-slate-400 truncate mb-3">
            {candidate.address}
          </div>

          {candidate.shap_features && Object.keys(candidate.shap_features).length > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-800">
              <span className="text-xs text-slate-500 mb-1 block">Key Drivers (SHAP)</span>
              {Object.entries(candidate.shap_features).map(([feature, value]) => (
                <div key={feature} className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">{feature}</span>
                  <span className={value > 0 ? 'text-green-500' : 'text-red-500'}>
                    {value > 0 ? '+' : ''}{value.toFixed(3)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
