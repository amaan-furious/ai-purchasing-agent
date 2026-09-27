import React from 'react';
import { GlassCard } from '../ui/GlassCard';
import { AgentDecision } from '../../lib/types';
import { Check } from 'lucide-react';
import { motion } from 'framer-motion';

export const DecisionCard: React.FC<{ decision: AgentDecision }> = ({ decision }) => {
  const decType = (decision.decision_type || decision.decision || 'ACCEPT').toUpperCase();
  const confidence = decision.confidenceScore ?? decision.final_decision?.confidence ?? 0.95;
  const reasoningList: string[] = decision.reasoning ?? decision.final_decision?.reasoning ?? (decision.final_decision?.rationale ? [decision.final_decision.rationale] : ['Decision evaluated by AI agent against operational constraints']);
  
  const origQty = decision.originalQuantity ?? decision.original_recommendation?.quantity;
  const modQty = decision.modifiedQuantity ?? decision.final_decision?.quantity;

  const getDecisionStyles = () => {
    switch (decType) {
      case 'ACCEPT': return 'from-emerald-500/20 to-emerald-900/20 border-emerald-500/30 text-emerald-400';
      case 'MODIFY': return 'from-amber-500/20 to-amber-900/20 border-amber-500/30 text-amber-400';
      case 'REJECT': return 'from-rose-500/20 to-rose-900/20 border-rose-500/30 text-rose-400';
      case 'ESCALATE': return 'from-indigo-500/20 to-indigo-900/20 border-indigo-500/30 text-indigo-400';
      default: return 'from-slate-500/20 to-slate-900/20 border-slate-500/30 text-slate-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', damping: 20 }}
    >
      <GlassCard className={`bg-gradient-to-br ${getDecisionStyles()} border-2`}>
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="text-sm font-medium text-slate-300 uppercase tracking-wider mb-1">Agent Decision</h3>
            <div className="text-3xl font-bold tracking-tight">{decType}</div>
          </div>
          
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="4" fill="none" className="opacity-20" />
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="4" fill="none" 
                strokeDasharray="175" strokeDashoffset={175 - (175 * confidence)}
                className="transition-all duration-1000 ease-out" 
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-xs font-bold">
              {Math.round(confidence * 100)}%
            </div>
          </div>
        </div>

        {decType === 'MODIFY' && modQty && (
          <div className="mb-6 p-4 rounded-xl bg-black/20 border border-black/10 flex justify-between items-center">
            <div className="text-center">
              <div className="text-xs text-slate-400 mb-1">Original</div>
              <div className="text-lg font-mono line-through opacity-50">{origQty || '—'}</div>
            </div>
            <div className="text-slate-500">→</div>
            <div className="text-center">
              <div className="text-xs text-slate-400 mb-1">Modified</div>
              <div className="text-lg font-mono font-bold text-white">{modQty}</div>
            </div>
          </div>
        )}

        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-slate-200">Key Reasoning Factors</h4>
          <ul className="space-y-2">
            {reasoningList.map((reason: string, i: number) => (
              <motion.li 
                key={i}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + (i * 0.1) }}
                className="flex items-start text-sm text-slate-300"
              >
                <Check className="w-4 h-4 mr-2 mt-0.5 shrink-0 opacity-70" />
                <span>{reason}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      </GlassCard>
    </motion.div>
  );
};
