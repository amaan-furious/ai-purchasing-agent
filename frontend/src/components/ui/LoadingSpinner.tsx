import React from 'react';
import { motion } from 'framer-motion';

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg', text?: string }> = ({ size = 'md', text }) => {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className={`relative ${sizeClasses[size]}`}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0 rounded-full border-t-2 border-r-2 border-indigo-500"
        />
        <motion.div
          animate={{ rotate: -360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="absolute inset-2 rounded-full border-b-2 border-l-2 border-purple-500"
        />
      </div>
      {text && <p className="text-slate-400 text-sm font-medium animate-pulse">{text}</p>}
    </div>
  );
};
