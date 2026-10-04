import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
  Cpu,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { WorkflowStep, StepStatus, AgentType } from '../../types';

interface WorkflowGraphViewProps {
  steps: WorkflowStep[];
  currentStepIndex: number;
}

export const WorkflowGraphView: React.FC<WorkflowGraphViewProps> = ({
  steps,
  currentStepIndex,
}) => {
  const [expandedStepId, setExpandedStepId] = useState<string | null>(null);

  const getAgentColor = (agent: AgentType) => {
    switch (agent) {
      case 'planner':
        return 'from-purple-500 to-indigo-600 border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400';
      case 'finance':
        return 'from-emerald-500 to-teal-600 border-emerald-200 dark:border-emerald-800 text-emerald-600 dark:text-emerald-400';
      case 'support':
        return 'from-amber-500 to-orange-600 border-amber-200 dark:border-amber-800 text-amber-600 dark:text-amber-400';
      case 'document':
        return 'from-blue-500 to-cyan-600 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400';
      case 'reporting':
        return 'from-rose-500 to-pink-600 border-rose-200 dark:border-rose-800 text-rose-600 dark:text-rose-400';
      default:
        return 'from-slate-500 to-slate-700 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400';
    }
  };

  const getStatusBadge = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
            Done
          </span>
        );
      case 'running':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 agent-active-pulse">
            <Sparkles className="w-3 h-3 text-blue-500 animate-spin" />
            Active
          </span>
        );
      case 'waiting_approval':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 animate-pulse">
            <ShieldAlert className="w-3 h-3 text-amber-500" />
            HITL Approval
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-300">
            <XCircle className="w-3 h-3 text-rose-500" />
            Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
    }
  };

  if (!steps || steps.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-navy-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800">
        <Cpu className="w-8 h-8 text-slate-400 mx-auto mb-2 opacity-50" />
        <p className="text-xs text-slate-500 dark:text-slate-400">
          Enter a prompt above to generate and inspect the multi-agent task execution graph.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-navy-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>LangGraph Agent Execution Pipeline</span>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              {steps.length} Stages
            </span>
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Sequential & conditional multi-agent coordination with autonomous failure protection
          </p>
        </div>
      </div>

      {/* Nodes Timeline & Graph */}
      <div className="space-y-4">
        {steps.map((step, idx) => {
          const isExpanded = expandedStepId === step.id;
          const isLast = idx === steps.length - 1;

          return (
            <div key={step.id || idx} className="relative">
              {!isLast && (
                <div
                  className={`absolute left-5 top-12 bottom-0 w-0.5 -mb-4 transition-colors ${
                    step.status === 'completed'
                      ? 'bg-emerald-400 dark:bg-emerald-600'
                      : 'bg-slate-200 dark:bg-slate-800'
                  }`}
                />
              )}

              <div
                className={`p-4 rounded-xl border transition-all ${
                  step.status === 'running'
                    ? 'border-brand-500 bg-brand-50/20 dark:bg-brand-950/20 shadow-md ring-1 ring-brand-400/40'
                    : step.status === 'waiting_approval'
                    ? 'border-amber-400 bg-amber-50/20 dark:bg-amber-950/20 shadow-md ring-1 ring-amber-400/40'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-navy-950/30'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getAgentColor(
                        step.agent_type
                      )} flex items-center justify-center text-white shadow-sm shrink-0 font-bold text-xs`}
                    >
                      {step.step_order}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900 dark:text-white">
                          {step.name}
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                          [{step.agent_type} agent]
                        </span>
                      </div>
                      {step.description && (
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">
                          {step.description}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {step.execution_time_ms > 0 && (
                      <span className="text-[10px] text-slate-400 font-mono">
                        {step.execution_time_ms} ms
                      </span>
                    )}
                    {getStatusBadge(step.status)}
                    <button
                      onClick={() => setExpandedStepId(isExpanded ? null : step.id)}
                      className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Output / Payload Inspector */}
                {isExpanded && (
                  <div className="mt-4 pt-3 border-t border-slate-200/60 dark:border-slate-800/60">
                    <h4 className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                      Agent Output State & Telemetry:
                    </h4>
                    <pre className="p-3 bg-slate-900 text-slate-200 rounded-lg text-[11px] font-mono overflow-x-auto max-h-56">
                      {JSON.stringify(step.output_data || {}, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
