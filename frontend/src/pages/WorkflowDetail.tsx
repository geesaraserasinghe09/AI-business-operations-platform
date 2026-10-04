import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RotateCcw,
  CheckCircle2,
  Clock,
  ShieldAlert,
  XCircle,
  FileDown,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { Workflow, Approval } from '../types';
import { WorkflowGraphView } from '../components/command/WorkflowGraphView';
import { ApprovalModal } from '../components/approvals/ApprovalModal';

export const WorkflowDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState<Approval | null>(null);

  const fetchDetail = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.workflows.get(id);
      setWorkflow(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const handleRetry = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const updated = await api.workflows.retry(id);
      setWorkflow(updated);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalAction = async (approvalId: string, action: 'approve' | 'reject', notes?: string) => {
    await api.approvals.action(approvalId, action, notes);
    fetchDetail();
  };

  const handleApprovalModify = async (approvalId: string, payload: Record<string, any>, notes?: string) => {
    await api.approvals.modify(approvalId, payload, notes);
    fetchDetail();
  };

  if (loading && !workflow) {
    return (
      <div className="p-12 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-brand-500" />
        <span>Loading workflow execution trace...</span>
      </div>
    );
  }

  if (!workflow) {
    return <div className="p-8 text-center text-xs text-rose-500">Workflow not found.</div>;
  }

  const pendingApproval = workflow.approvals?.find((a) => a.status === 'pending');

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Top Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/workflows')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Workflows</span>
        </button>

        <div className="flex items-center gap-3">
          {(workflow.status === 'failed' || workflow.status === 'waiting_for_human') && (
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-navy-900 hover:bg-slate-50 text-xs font-semibold text-slate-700 dark:text-slate-300 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Workflow</span>
            </button>
          )}
        </div>
      </div>

      {/* Workflow Meta Header */}
      <div className="bg-white dark:bg-navy-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-mono text-slate-400">ID: {workflow.id}</span>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white mt-1">{workflow.title}</h1>
          </div>
          <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 self-start">
            Status: {workflow.status.replace('_', ' ')}
          </span>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200/60 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
          <strong className="block text-[11px] text-slate-400 mb-1">Original Directive:</strong>
          {workflow.prompt}
        </div>
      </div>

      {/* Human Approval Callout if required */}
      {pendingApproval && (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-6 h-6 text-amber-500 shrink-0" />
            <div>
              <h4 className="text-xs font-bold text-amber-900 dark:text-amber-200">
                Action Requires Human Authorization
              </h4>
              <p className="text-[11px] text-amber-700 dark:text-amber-400">
                {pendingApproval.title} • Risk Level: {pendingApproval.risk_level.toUpperCase()}
              </p>
            </div>
          </div>
          <button
            onClick={() => setSelectedApproval(pendingApproval)}
            className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow"
          >
            Review & Decide
          </button>
        </div>
      )}

      {/* Pipeline View */}
      <WorkflowGraphView
        steps={workflow.steps}
        currentStepIndex={workflow.current_step_index}
      />

      {/* Summary / Final Report */}
      {workflow.summary_result && (
        <div className="bg-white dark:bg-navy-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Execution Summary & Synthesis</span>
          </h3>
          <div className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line p-4 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200/60 dark:border-slate-800">
            {workflow.summary_result}
          </div>
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
