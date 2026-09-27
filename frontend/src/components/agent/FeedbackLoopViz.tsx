import React from 'react';
import { GlassCard } from '../ui/GlassCard';

export const FeedbackLoopViz: React.FC = () => {
  return (
    <GlassCard>
      <h3 className="text-lg font-semibold text-white mb-6">Agent Feedback Loop</h3>
      <div className="flex flex-col items-center py-4">
        <div className="flex items-center space-x-2">
          <div className="px-4 py-2 rounded-lg bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-sm font-medium">Analyze</div>
          <div className="text-slate-500">→</div>
          <div className="px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/30 text-purple-300 text-sm font-medium">Decide</div>
          <div className="text-slate-500">→</div>
          <div className="px-4 py-2 rounded-lg bg-amber-500/20 border border-amber-500/30 text-amber-300 text-sm font-medium">Validate</div>
        </div>
        
        <div className="flex mt-4">
          <svg width="200" height="60" viewBox="0 0 200 60" fill="none">
            <path d="M 180 10 Q 180 50 100 50 Q 20 50 20 10" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 4" fill="none" className="animate-pulse" />
            <polygon points="15,15 20,5 25,15" fill="#f59e0b" />
          </svg>
        </div>
        
        <div className="text-xs text-amber-400 font-medium bg-amber-500/10 px-3 py-1 rounded-full -mt-2 z-10 border border-amber-500/20">
          Self-Correction Loop (if validation fails)
        </div>
      </div>
    </GlassCard>
  );
};
