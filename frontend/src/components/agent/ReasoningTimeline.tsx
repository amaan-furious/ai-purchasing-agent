import React from 'react';
import { ReasoningStep } from '../../lib/types';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Wrench, Brain, CheckCircle, Shield, Zap, CheckCheck, XCircle, AlertTriangle } from 'lucide-react';

const iconMap = {
  investigate: { icon: Search, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
  tool_call: { icon: Wrench, color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/20' },
  analyze: { icon: Brain, color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/20' },
  decide: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  validate: { icon: Shield, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  execute: { icon: Zap, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/20' },
  verify: { icon: CheckCheck, color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/20' },
  error: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  escalate: { icon: AlertTriangle, color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/20' }
};

export const ReasoningTimeline: React.FC<{ steps: ReasoningStep[] }> = ({ steps }) => {
  return (
    <div className="relative border-l border-slate-700/50 ml-4 py-2 space-y-8">
      <AnimatePresence>
        {steps.map((step, index) => {
          const typeStyle = iconMap[step.type] || iconMap.analyze;
          const Icon = typeStyle.icon;
          const isActive = step.status === 'active';
          const isFailed = step.status === 'failed';

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="relative pl-8"
            >
              <div className={`absolute -left-[17px] top-1 w-8 h-8 rounded-full border-2 ${isActive ? 'border-indigo-500 bg-bg-primary' : isFailed ? 'border-red-500 bg-bg-primary' : 'border-emerald-500 bg-bg-primary'} flex items-center justify-center`}>
                {isActive ? (
                  <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />
                ) : isFailed ? (
                  <XCircle className="w-4 h-4 text-red-500" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                )}
              </div>

              <div className={`p-4 rounded-xl border ${isActive ? 'border-indigo-500/30 bg-indigo-500/5 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'border-slate-700/50 bg-slate-800/20'} transition-all duration-300`}>
                <div className="flex items-center mb-2">
                  <div className={`p-1.5 rounded-lg mr-3 ${typeStyle.bg} ${typeStyle.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <h4 className={`font-semibold ${isActive ? 'text-indigo-300' : 'text-slate-200'}`}>{step.title}</h4>
                  <span className="ml-auto text-xs text-slate-500">
                    {new Date(step.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-slate-400 mt-2 ml-10">
                  {step.description}
                </p>
                {step.data && !isActive && (
                  <div className="mt-4 ml-10 p-3 rounded-lg bg-black/40 border border-slate-700/50 overflow-x-auto text-xs text-slate-400 font-mono">
                    <pre>{JSON.stringify(step.data, null, 2)}</pre>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};
