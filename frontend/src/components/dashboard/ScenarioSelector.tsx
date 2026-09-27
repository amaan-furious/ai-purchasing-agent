import React from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Button } from '../ui/Button';
import { ClipboardCheck, AlertTriangle, TrendingUp, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

interface ScenarioSelectorProps {
  onSelectScenario: (scenarioId: string) => void;
}

const scenarios = [
  {
    id: 'scen-001',
    title: 'Purchase Recommendation Review',
    description: 'Evaluate whether a system recommendation of 800 units should be accepted, modified, or rejected.',
    icon: ClipboardCheck,
    colorAccent: 'indigo'
  },
  {
    id: 'scen-002',
    title: 'Supplier Partial Fulfillment',
    description: 'Handle a situation where a supplier can only fulfill 250 of 500 ordered units.',
    icon: AlertTriangle,
    colorAccent: 'amber'
  },
  {
    id: 'scen-003',
    title: 'Demand Spike Response',
    description: 'Respond to a 3x increase in actual demand versus forecast.',
    icon: TrendingUp,
    colorAccent: 'emerald'
  },
  {
    id: 'scen-004',
    title: 'Purchasing Constraint',
    description: 'Navigate budget and storage constraints that prevent the ideal purchase.',
    icon: ShieldAlert,
    colorAccent: 'rose'
  }
];

const colorStyles = {
  indigo: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
  amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
  emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
  rose: 'text-rose-400 bg-rose-500/10 border-rose-500/20'
};

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({ onSelectScenario }) => {
  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-white mb-6 flex items-center">
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
          Agent Scenarios
        </span>
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scenarios.map((scenario, index) => {
          const Icon = scenario.icon;
          return (
            <motion.div
              key={scenario.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <GlassCard className="flex flex-col h-full hover:border-slate-600 transition-colors">
                <div className="flex items-start mb-4">
                  <div className={`p-3 rounded-xl border ${colorStyles[scenario.colorAccent as keyof typeof colorStyles]} mr-4`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{scenario.title}</h3>
                    <p className="text-sm text-slate-400">{scenario.description}</p>
                  </div>
                </div>
                <div className="mt-auto pt-4 flex justify-end">
                  <Button 
                    variant="secondary" 
                    size="sm"
                    onClick={() => onSelectScenario(scenario.id)}
                  >
                    Run Scenario
                  </Button>
                </div>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
