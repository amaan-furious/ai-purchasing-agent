import React from 'react';
import { Bot, Wifi, WifiOff } from 'lucide-react';
import { motion } from 'framer-motion';

export const Header: React.FC<{ isConnected?: boolean }> = ({ isConnected = true }) => {
  return (
    <header className="flex items-center justify-between py-6 border-b border-slate-800/50 mb-8 backdrop-blur-md sticky top-0 z-50 bg-bg-primary/80 px-8 -mx-8">
      <div className="flex items-center space-x-4">
        <motion.div 
          initial={{ rotate: -20, scale: 0.8 }}
          animate={{ rotate: 0, scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
          className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20"
        >
          <Bot className="w-7 h-7 text-white" />
        </motion.div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center">
            AI Purchasing Agent
          </h1>
          <p className="text-slate-400 text-sm font-medium mt-0.5">Intelligent Decision Automation</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-3 bg-slate-800/30 px-4 py-2 rounded-full border border-slate-700/50">
        <span className="text-sm font-medium text-slate-300">System Status</span>
        <div className={`flex items-center space-x-1.5 px-2 py-1 rounded-full text-xs font-semibold ${isConnected ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
          {isConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
    </header>
  );
};
