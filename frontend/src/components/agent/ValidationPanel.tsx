import React from 'react';
import { GlassCard } from '../ui/GlassCard';
import { ValidationResult, ExecutionResult } from '../../lib/types';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ValidationPanelProps {
  validations: ValidationResult[];
  execution: ExecutionResult | null;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({ validations, execution }) => {
  const allPassed = validations.every(v => v.passed);

  return (
    <GlassCard>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Validation Gates</h3>
        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${
          allPassed 
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
            : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
        }`}>
          {allPassed ? 'ALL PASSED' : 'VALIDATION FAILED'}
        </div>
      </div>

      <div className="space-y-4">
        {validations.map((val, i) => {
          const ruleTitle = val.rule_name || val.ruleName || val.ruleId || `Rule #${i + 1}`;
          
          return (
            <motion.div 
              key={val.ruleId || val.rule_name || i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`p-4 rounded-xl border ${val.passed ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-rose-500/20 bg-rose-500/5'}`}
            >
              <div className="flex items-start">
                {val.passed ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-500 mr-3 shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-5 h-5 text-rose-500 mr-3 shrink-0 mt-0.5" />
                )}
                <div>
                  <h4 className={`text-sm font-medium capitalize ${val.passed ? 'text-emerald-200' : 'text-rose-200'}`}>
                    {ruleTitle.replace('_', ' ')}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1">{val.details}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {execution && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 pt-6 border-t border-slate-700/50"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Execution Status</h3>
          <div className={`p-4 rounded-xl border flex items-start ${
            execution.success 
              ? 'border-indigo-500/20 bg-indigo-500/10 text-indigo-200' 
              : 'border-orange-500/20 bg-orange-500/10 text-orange-200'
          }`}>
            {execution.success ? (
              <CheckCircle2 className="w-5 h-5 text-indigo-400 mr-3 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-orange-400 mr-3 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="font-medium">
                {execution.actionTaken || (execution.success ? 'Purchase Order Created' : 'Execution Warning')}
              </div>
              <div className="text-sm opacity-80 mt-1">
                {execution.details || (execution.actions ? `${execution.actions.length} database action(s) committed successfully` : 'System state updated')}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </GlassCard>
  );
};
