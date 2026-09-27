import React, { useEffect, useState } from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Badge } from '../ui/Badge';
import { getAgentDecisions } from '../../lib/api';
import { AgentDecision } from '../../lib/types';
import { formatDistanceToNow } from 'date-fns';

export const RecentDecisions: React.FC = () => {
  const [decisions, setDecisions] = useState<AgentDecision[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const data = await getAgentDecisions();
        setDecisions(data);
      } catch (error) {
        console.error("Error fetching decisions", error);
      } finally {
        setLoading(false);
      }
    };
    fetchDecisions();
  }, []);

  const getDecisionBadge = (decisionStr?: string) => {
    const dec = (decisionStr || 'ACCEPT').toUpperCase();
    switch (dec) {
      case 'ACCEPT': return <Badge variant="success">ACCEPT</Badge>;
      case 'MODIFY': return <Badge variant="warning">MODIFY</Badge>;
      case 'REJECT': return <Badge variant="error">REJECT</Badge>;
      case 'ESCALATE': return <Badge variant="info">ESCALATE</Badge>;
      default: return <Badge>{dec}</Badge>;
    }
  };

  return (
    <GlassCard className="mb-8">
      <h2 className="text-xl font-bold text-white mb-6">Recent Agent Decisions</h2>
      
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-slate-800/50 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-700/50 text-slate-400 text-sm">
                <th className="py-3 px-4 font-medium">Scenario</th>
                <th className="py-3 px-4 font-medium">Product</th>
                <th className="py-3 px-4 font-medium">Decision</th>
                <th className="py-3 px-4 font-medium">Status</th>
                <th className="py-3 px-4 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {decisions.map((dec) => {
                const scenario = dec.scenario_type || dec.scenarioId || 'General Review';
                const product = dec.productId || dec.product_id || dec.final_decision?.product_id || 'PRD-001';
                const decisionStr = dec.decision_type || dec.decision || 'ACCEPT';
                const timeStr = dec.created_at || dec.timestamp || new Date().toISOString();
                
                return (
                  <tr key={dec.id} className="border-b border-slate-700/20 hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-4 text-sm text-slate-300 capitalize">{scenario.replace('_', ' ')}</td>
                    <td className="py-4 px-4 text-sm font-medium text-white">{product}</td>
                    <td className="py-4 px-4">{getDecisionBadge(decisionStr)}</td>
                    <td className="py-4 px-4 text-sm text-slate-300">
                      <span className="capitalize">{dec.status || 'executed'}</span>
                    </td>
                    <td className="py-4 px-4 text-sm text-slate-400">
                      {formatDistanceToNow(new Date(timeStr), { addSuffix: true })}
                    </td>
                  </tr>
                );
              })}
              {decisions.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No recent decisions found. Run a scenario to see agent decisions here!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </GlassCard>
  );
};
