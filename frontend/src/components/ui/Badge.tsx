import React from 'react';
import { motion } from 'framer-motion';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  animated?: boolean;
  className?: string;
}

const variants = {
  success: 'bg-green-500/10 text-green-400 border-green-500/20',
  warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  error: 'bg-red-500/10 text-red-400 border-red-500/20',
  info: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  neutral: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
};

const dotColors = {
  success: 'bg-green-400',
  warning: 'bg-amber-400',
  error: 'bg-red-400',
  info: 'bg-indigo-400',
  neutral: 'bg-gray-400',
};

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', animated = false, className = '' }) => {
  return (
    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant]} ${className}`}>
      {animated && (
        <span className="relative flex h-2 w-2 mr-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColors[variant]}`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${dotColors[variant]}`}></span>
        </span>
      )}
      {children}
    </div>
  );
};
