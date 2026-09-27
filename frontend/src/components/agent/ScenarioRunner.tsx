import React, { useState, useEffect } from 'react';
import { GlassCard } from '../ui/GlassCard';
import { Button } from '../ui/Button';
import { ReasoningTimeline } from './ReasoningTimeline';
import { DecisionCard } from './DecisionCard';
import { ValidationPanel } from './ValidationPanel';
import { ReasoningStep, AgentDecision, ValidationResult, ExecutionResult } from '../../lib/types';
import { runScenario, resetScenario } from '../../lib/api';
import { Play, RotateCcw } from 'lucide-react';

interface ScenarioRunnerProps {
  scenarioId: string;
}

export const ScenarioRunner: React.FC<ScenarioRunnerProps> = ({ scenarioId }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [isFinished, setIsFinished] = useState(false);
  const [steps, setSteps] = useState<ReasoningStep[]>([]);
  const [decision, setDecision] = useState<AgentDecision | null>(null);
  const [validations, setValidations] = useState<ValidationResult[]>([]);
  const [execution, setExecution] = useState<ExecutionResult | null>(null);

  const startScenario = () => {
    setIsRunning(true);
    setIsFinished(false);
    setSteps([]);
    setDecision(null);
    setValidations([]);
    setExecution(null);

    const eventSource = runScenario(scenarioId, {});

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'step') {
        setSteps(prev => [...prev.filter(s => s.id !== data.step.id), data.step]);
      } else if (data.type === 'decision') {
        setDecision(data.decision);
      } else if (data.type === 'validation') {
        setValidations(data.validations);
      } else if (data.type === 'execution') {
        setExecution(data.execution);
      } else if (data.type === 'done') {
        setIsRunning(false);
        setIsFinished(true);
        eventSource.close();
      } else if (data.type === 'error') {
        console.error("Scenario error:", data.message);
        setIsRunning(false);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      console.error("SSE connection error");
      setIsRunning(false);
      eventSource.close();
    };
  };

  const handleReset = async () => {
    await resetScenario(scenarioId);
    setSteps([]);
    setDecision(null);
    setValidations([]);
    setExecution(null);
    setIsFinished(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 space-y-6">
        <GlassCard className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Scenario Execution</h2>
            <p className="text-slate-400 text-sm">Watch the agent reasoning process in real-time.</p>
          </div>
          <div className="space-x-4">
            <Button 
              onClick={startScenario} 
              disabled={isRunning} 
              leftIcon={<Play className="w-4 h-4" />}
            >
              Run Agent
            </Button>
            <Button 
              variant="outline" 
              onClick={handleReset} 
              disabled={isRunning || (!isFinished && steps.length === 0)}
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              Reset
            </Button>
          </div>
        </GlassCard>

        {steps.length > 0 && (
          <GlassCard>
            <h3 className="text-lg font-semibold text-white mb-6">Reasoning Timeline</h3>
            <ReasoningTimeline steps={steps} />
          </GlassCard>
        )}
      </div>

      <div className="space-y-6">
        {decision && (
          <DecisionCard decision={decision} />
        )}
        
        {validations.length > 0 && (
          <ValidationPanel validations={validations} execution={execution} />
        )}
      </div>
    </div>
  );
};
