import React, { useState } from 'react';
import {
  Sparkles,
  Play,
  Clock,
  ShieldAlert,
  CheckCircle2,
  FileDown,
  Terminal,
  RefreshCw,
  HelpCircle,
  Cpu
} from 'lucide-react';
import { api } from '../services/api';
import { Workflow, Approval } from '../types';
import { WorkflowGraphView } from '../components/command/WorkflowGraphView';
import { ApprovalModal } from '../components/approvals/ApprovalModal';

const PRESET_DIRECTIVES = [
  {
    label: "Comprehensive Q3 Executive Audit",
    prompt: "Analyze this month's sales data, identify top five products, summarize pending customer complaints, and prepare an executive report."
  },
  {
    label: "Customer Escalation & SLA Protocol",
    prompt: "Scan open customer support tickets, identify SLA breach risks on ticket TK-8402, and draft an executive engineering escalation email."
  },
  {
    label: "Financial Anomalies & High-Value Refunds",
    prompt: "Perform audit on financial records, detect high-value refund anomalies in APAC region, and propose ledger adjustments."
  },
  {
    label: "RAG Policy & Compliance Verification",
    prompt: "Query internal business operations policy documents regarding customer refund thresholds and summarize compliance rules."
  }
];

export const CommandCenter: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<Approval | null>(null);

  const handleExecute = async (directivePrompt?: string) => {
    const textToRun = directivePrompt || prompt;
    if (!textToRun.trim() || isExecuting) return;

    setIsExecuting(true);
    try {
      const wf = await api.workflows.create(textToRun);
      setCurrentWorkflow(wf);

      // Poll workflow status if running or waiting
      if (wf.status === 'running' || wf.status === 'waiting_for_human') {
        pollWorkflow(wf.id);
      }
    } catch (err) {
      console.error('Failed to initiate workflow', err);
    } finally {
      setIsExecuting(false);
    }
  };

  const pollWorkflow = async (workflowId: string) => {
    try {
      const updated = await api.workflows.get(workflowId);
      setCurrentWorkflow(updated);
      if (updated.status === 'running') {
        setTimeout(() => pollWorkflow(workflowId), 1500);
      }
    } catch {
      // stop polling on error
    }
  };

  const handleApprovalAction = async (id: string, action: 'approve' | 'reject', notes?: string) => {
    await api.approvals.action(id, action, notes);
    if (currentWorkflow) {
      pollWorkflow(currentWorkflow.id);
    }
  };

  const handleApprovalModify = async (id: string, payload: Record<string, any>, notes?: string) => {
    await api.approvals.modify(id, payload, notes);
    if (currentWorkflow) {
      pollWorkflow(currentWorkflow.id);
    }
  };

  const pendingApproval = currentWorkflow?.approvals?.find((a) => a.status === 'pending');

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      {/* Title & Architecture Summary */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-600 dark:text-brand-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Central LangGraph Orchestrator</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          AI Business Command Center
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          Submit high-level natural language operational directives. The AI Orchestrator decomposes
          goals into specialized agent tasks, executes authorized tools, and enforces Human-in-the-Loop checkpoints.
        </p>
      </div>

      {/* Directive Command Bar */}
      <div className="bg-white dark:bg-navy-900 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 shadow-lg shadow-slate-200/50 dark:shadow-none">
        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your business directive (e.g. 'Analyze this month's sales data, identify top five products, summarize pending customer complaints, and prepare a management report.')..."
            rows={3}
            className="w-full p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-white placeholder:text-slate-400 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 transition resize-none"
          />
          <div className="flex items-center justify-between mt-3 px-1">
            <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-500" />
              <span>Agents: Planner • Finance • Support • Document • Reporting</span>
            </span>
            <button
              onClick={() => handleExecute()}
              disabled={isExecuting || !prompt.trim()}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md shadow-brand-500/25 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isExecuting ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Orchestrating...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Execute Directive</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Preset Prompt Buttons */}
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block mb-2">Preset Enterprise Scenarios:</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {PRESET_DIRECTIVES.map((item, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setPrompt(item.prompt);
                  handleExecute(item.prompt);
                }}
                className="text-left p-2.5 rounded-lg border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:border-brand-300 dark:hover:border-brand-700 transition group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200 group-hover:text-brand-600 transition">
                    {item.label}
                  </span>
                  <Sparkles className="w-3 h-3 text-slate-400 group-hover:text-brand-500" />
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{item.prompt}</p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Human Approval Alert Banner if paused */}
      {pendingApproval && (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 flex items-center justify-between animate-fadeIn">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-500 text-white flex items-center justify-center font-bold">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-amber-900 dark:text-amber-200">
                Workflow Checkpoint: Human Approval Required
              </h4>
              <p className="text-[11px] text-amber-700 dark:text-amber-400">
                {pendingApproval.agent_name} triggered action '{pendingApproval.action_type}' requiring manager authorization.
              </p>
            </div>
          </div>
          <button
            onClick={() => setSelectedApproval(pendingApproval)}
            className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow transition"
          >
            Review Action & Authorize
          </button>
        </div>
      )}

      {/* LangGraph Pipeline View */}
      {currentWorkflow && (
        <div className="space-y-6">
          <WorkflowGraphView
            steps={currentWorkflow.steps}
            currentStepIndex={currentWorkflow.current_step_index}
          />

          {/* Final Synthesized Output Card */}
          {currentWorkflow.summary_result && (
            <div className="bg-white dark:bg-navy-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 mb-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    Executive Operations Briefing Output
                  </h3>
                </div>
                <button
                  onClick={() => window.open(`/reports`, '_blank')}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 text-xs font-semibold transition"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  <span>Download Report</span>
                </button>
              </div>

              <div className="prose dark:prose-invert max-w-none text-xs text-slate-700 dark:text-slate-300 leading-relaxed space-y-3 whitespace-pre-line">
                {currentWorkflow.summary_result}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Approval Modal */}
      {selectedApproval && (
        <ApprovalModal
          approval={selectedApproval}
          onClose={() => setSelectedApproval(null)}
          onAction={handleApprovalAction}
          onModify={handleApprovalModify}
        />
      )}
    </div>
  );
};
