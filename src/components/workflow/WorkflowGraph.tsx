import React from 'react';
import { WorkflowState, WorkflowStep } from '@/workflow/state/types';
import { CheckCircle, Clock, AlertCircle, PlayCircle, Loader2 } from 'lucide-react';
import clsx from 'clsx';

interface WorkflowGraphProps {
  state: WorkflowState | null;
  onNodeClick?: (step: WorkflowStep) => void;
}

export function WorkflowGraph({ state, onNodeClick }: WorkflowGraphProps) {
  if (!state || !state.plan) {
    return <div className="p-8 text-center text-slate-500">No active workflow. Enter an objective to begin.</div>;
  }

  const steps = state.plan;

  return (
    <div className="flex flex-col gap-4 relative">
      {/* Visual Line connecting nodes */}
      <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-slate-200 z-0"></div>

      {steps.map((step, index) => {
        const isCurrent = state.currentStepId === step.id;
        let Icon = Clock;
        let iconColor = "text-slate-400 bg-slate-100";
        let bgColor = "bg-white border-slate-200";

        if (step.status === 'COMPLETED') {
          Icon = CheckCircle;
          iconColor = "text-green-500 bg-green-50";
        } else if (step.status === 'FAILED') {
          Icon = AlertCircle;
          iconColor = "text-red-500 bg-red-50";
          bgColor = "bg-red-50 border-red-200";
        } else if (step.status === 'RUNNING' || isCurrent) {
          Icon = Loader2;
          iconColor = "text-blue-500 bg-blue-50 animate-spin-slow";
          bgColor = "bg-blue-50 border-blue-200";
        } else if (step.status === 'SKIPPED') {
          iconColor = "text-slate-300 bg-slate-50";
        }

        return (
          <div 
            key={step.id} 
            className={clsx(
              "flex gap-4 relative z-10 p-4 rounded-xl border shadow-sm transition-all cursor-pointer hover:shadow-md",
              bgColor
            )}
            onClick={() => onNodeClick?.(step)}
          >
            <div className={clsx("flex items-center justify-center w-12 h-12 rounded-full", iconColor)}>
              <Icon className="w-6 h-6" />
            </div>
            
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-slate-900">{step.name}</h4>
                  <p className="text-sm text-slate-500 mt-1">{step.description}</p>
                </div>
                <div className="text-xs font-medium px-2 py-1 rounded bg-white/50 border">
                  {step.status}
                </div>
              </div>
              
              {step.resultSummary && (
                <div className="mt-3 text-sm bg-white/60 p-3 rounded-lg border border-slate-100 text-slate-700">
                  {step.resultSummary}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
