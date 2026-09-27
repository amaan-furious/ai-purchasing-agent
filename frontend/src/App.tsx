import React, { useState } from 'react';
import { Header } from './components/dashboard/Header';
import { KPISection } from './components/dashboard/KPISection';
import { ScenarioSelector } from './components/dashboard/ScenarioSelector';
import { RecentDecisions } from './components/dashboard/RecentDecisions';
import { ScenarioRunner } from './components/agent/ScenarioRunner';
import { DataExplorer } from './components/data/DataExplorer';
import { AnimatePresence, motion } from 'framer-motion';
import { LayoutDashboard, Database, ArrowLeft } from 'lucide-react';
import { Button } from './components/ui/Button';

function App() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'scenario' | 'data'>('dashboard');
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);

  const handleSelectScenario = (id: string) => {
    setActiveScenarioId(id);
    setCurrentView('scenario');
  };

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary p-8">
      <div className="max-w-7xl mx-auto">
        <Header />

        <div className="flex space-x-4 mb-8">
          <Button 
            variant={currentView === 'dashboard' || currentView === 'scenario' ? 'primary' : 'ghost'} 
            onClick={() => setCurrentView('dashboard')}
            leftIcon={<LayoutDashboard className="w-4 h-4" />}
          >
            Dashboard
          </Button>
          <Button 
            variant={currentView === 'data' ? 'primary' : 'ghost'} 
            onClick={() => setCurrentView('data')}
            leftIcon={<Database className="w-4 h-4" />}
          >
            Data Explorer
          </Button>
        </div>

        <AnimatePresence mode="wait">
          {currentView === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <KPISection />
              <ScenarioSelector onSelectScenario={handleSelectScenario} />
              <RecentDecisions />
            </motion.div>
          )}

          {currentView === 'scenario' && activeScenarioId && (
            <motion.div
              key="scenario"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="mb-6">
                <Button 
                  variant="ghost" 
                  onClick={() => setCurrentView('dashboard')}
                  leftIcon={<ArrowLeft className="w-4 h-4" />}
                  className="!px-0 hover:!bg-transparent text-slate-400 hover:text-white"
                >
                  Back to Dashboard
                </Button>
              </div>
              <ScenarioRunner scenarioId={activeScenarioId} />
            </motion.div>
          )}

          {currentView === 'data' && (
            <motion.div
              key="data"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-6">Master Data Explorer</h2>
              <DataExplorer />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
