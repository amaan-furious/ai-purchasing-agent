import React from 'react';
import { GlassCard } from './GlassCard';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  subtitle?: string;
  colorAccent?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'purple';
  loading?: boolean;
}

const colorMap = {
  indigo: 'text-indigo-400 bg-indigo-500/10',
  emerald: 'text-emerald-400 bg-emerald-500/10',
  amber: 'text-amber-400 bg-amber-500/10',
  rose: 'text-rose-400 bg-rose-500/10',
  purple: 'text-purple-400 bg-purple-500/10',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  subtitle,
  colorAccent = 'indigo',
  loading = false
}) => {
  if (loading) {
    return (
      <GlassCard className="animate-pulse">
        <div className="h-6 bg-slate-700/50 rounded w-1/3 mb-4"></div>
        <div className="h-10 bg-slate-700/50 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-slate-700/50 rounded w-2/3"></div>
      </GlassCard>
    );
  }

  return (
    <GlassCard>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-slate-400 text-sm font-medium">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
          
          {(trend || subtitle) && (
            <div className="flex items-center mt-2 space-x-2 text-sm">
              {trend && (
                <span className={`inline-flex items-center ${trend.isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
                </span>
              )}
              {subtitle && <span className="text-slate-500">{subtitle}</span>}
            </div>
          )}
        </div>
        
        <div className={`p-3 rounded-xl ${colorMap[colorAccent]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </GlassCard>
  );
};
