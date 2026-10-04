import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  Edit3,
  Bot,
  Filter,
  RefreshCw,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';
import { Approval, RiskLevel } from '../types';
import { ApprovalModal } from '../components/approvals/ApprovalModal';

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('pending');
  const [loading, setLoading] = useState(true);
  const [activeApproval, setActiveApproval] = useState<Approval | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.approvals.list(statusFilter || undefined);
      setApprovals(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [statusFilter]);

  const handleAction = async (id: string, action: 'approve' | 'reject', notes?: string) => {
    await api.approvals.action(id, action, notes);
    fetchApprovals();
  };

  const handleModify = async (id: string, payload: Record<string, any>, notes?: string) => {
    await api.approvals.modify(id, payload, notes);
    fetchApprovals();
  };

  const getRiskColor = (risk: RiskLevel) => {
    switch (risk) {
      case 'critical':
        return 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-400 border-rose-300';
      case 'high':
        return 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400 border-amber-300';
      case 'medium':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400 border-blue-300';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-300';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Human-in-the-Loop Approvals
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
              Strict HITL Policy
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Autonomous AI actions with financial, customer communication, or database impact are paused until authorized by a manager.
          </p>
        </div>

        {/* Filter Toggle */}
        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-navy-900 text-slate-700 dark:text-slate-300 focus:outline-none"
          >
            <option value="pending">Pending Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="">All History</option>
          </select>
          <button
            onClick={fetchApprovals}
            className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Cards List */}
      {loading && approvals.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-400">Loading approval queue...</div>
      ) : approvals.length === 0 ? (
        <div className="p-16 text-center bg-white dark:bg-navy-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 space-y-2">
          <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto opacity-75" />
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">No Pending Approvals</h3>
          <p className="text-xs text-slate-400">All sensitive AI operational tasks have been authorized or reviewed.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {approvals.map((appr) => (
            <div
              key={appr.id}
              className={`p-6 rounded-2xl bg-white dark:bg-navy-900 border transition shadow-sm ${
                appr.status === 'pending'
                  ? 'border-amber-300 dark:border-amber-800 ring-1 ring-amber-400/20'
                  : 'border-slate-200 dark:border-slate-800'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border ${getRiskColor(appr.risk_level)}`}>
                      {appr.risk_level} Risk
                    </span>
                    <span className="text-xs font-mono text-slate-400 uppercase">[{appr.action_type}]</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white pt-1">{appr.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{appr.description}</p>
                </div>

                <div className="text-right shrink-0">
                  <span className="text-[11px] text-slate-400 block font-mono">
                    Requested: {new Date(appr.requested_at).toLocaleString()}
                  </span>
                  <span className="text-[11px] text-brand-600 dark:text-brand-400 font-semibold block mt-0.5">
                    Responsible: {appr.agent_name}
                  </span>
                </div>
              </div>

              {/* Rationale and payload preview */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200/60 dark:border-slate-800">
                  <div className="flex items-center gap-1.5 text-brand-600 dark:text-brand-400 font-semibold mb-1">
                    <Bot className="w-3.5 h-3.5" />
                    <span>AI Explanation & Rationale</span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 leading-relaxed mb-2">{appr.reason}</p>
                  <p className="text-[11px] text-slate-400 italic">{appr.ai_explanation}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-200/60 dark:border-slate-800">
                  <span className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">Action Data Payload:</span>
                  <pre className="p-2.5 bg-slate-900 text-slate-200 rounded-lg font-mono text-[10px] overflow-x-auto max-h-24">
                    {JSON.stringify(appr.data_payload || {}, null, 2)}
                  </pre>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2">
                <div className="text-xs">
                  {appr.status !== 'pending' && (
                    <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 font-medium">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Reviewed on {appr.reviewed_at ? new Date(appr.reviewed_at).toLocaleDateString() : 'N/A'}</span>
                    </span>
                  )}
                </div>

                {appr.status === 'pending' ? (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setActiveApproval(appr)}
                      className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow transition flex items-center gap-1.5"
                    >
                      <ShieldAlert className="w-3.5 h-3.5" />
                      <span>Review & Authorize</span>
                    </button>
                  </div>
                ) : (
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                    appr.status === 'approved'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                      : appr.status === 'modified'
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                      : 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                  }`}>
                    {appr.status}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Review Modal */}
      {activeApproval && (
        <ApprovalModal
          approval={activeApproval}
          onClose={() => setActiveApproval(null)}
          onAction={handleAction}
          onModify={handleModify}
        />
      )}
    </div>
  );
};
