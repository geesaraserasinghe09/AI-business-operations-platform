import React, { useState } from 'react';
import {
  X,
  ShieldAlert,
  CheckCircle,
  XCircle,
  Edit3,
  Bot,
  AlertCircle
} from 'lucide-react';
import { Approval } from '../../types';

interface ApprovalModalProps {
  approval: Approval | null;
  onClose: () => void;
  onAction: (id: string, action: 'approve' | 'reject', notes?: string) => Promise<void>;
  onModify: (id: string, payload: Record<string, any>, notes?: string) => Promise<void>;
}

export const ApprovalModal: React.FC<ApprovalModalProps> = ({
  approval,
  onClose,
  onAction,
  onModify,
}) => {
  if (!approval) return null;

  const [notes, setNotes] = useState('');
  const [isModifying, setIsModifying] = useState(false);
  const [jsonText, setJsonText] = useState(JSON.stringify(approval.data_payload || {}, null, 2));
  const [jsonError, setJsonError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'critical':
        return 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-400 border-rose-300';
      case 'high':
        return 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-400 border-amber-300';
      case 'medium':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-400 border-blue-300';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-300';
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      if (isModifying) {
        let parsed;
        try {
          parsed = JSON.parse(jsonText);
        } catch {
          setJsonError('Invalid JSON format.');
          setLoading(false);
          return;
        }
        await onModify(approval.id, parsed, notes);
      } else {
        await onAction(approval.id, 'approve', notes);
      }
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await onAction(approval.id, 'reject', notes);
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-navy-900 rounded-2xl max-w-2xl w-full border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-navy-950/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center border border-amber-500/20">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Human-in-the-Loop Review</h3>
              <p className="text-xs text-slate-500">Autonomous execution checkpoint</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs">
          {/* Action & Risk */}
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-semibold">Requested Operation</span>
              <h4 className="text-sm font-bold text-slate-900 dark:text-white mt-0.5">{approval.title}</h4>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase border ${getRiskBadge(approval.risk_level)}`}>
                {approval.risk_level} Risk
              </span>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                Agent: {approval.agent_name}
              </span>
            </div>
          </div>

          {/* AI Reason & Explanation */}
          <div className="bg-brand-50/50 dark:bg-brand-950/20 p-4 rounded-xl border border-brand-100 dark:border-brand-900/40">
            <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400 font-semibold mb-1">
              <Bot className="w-4 h-4" />
              <span>AI Rationale & Context</span>
            </div>
            <p className="text-slate-700 dark:text-slate-300 mb-2 leading-relaxed">{approval.reason}</p>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 bg-white/60 dark:bg-navy-900/60 p-2.5 rounded-lg border border-brand-200/40 dark:border-brand-800/40">
              <strong>Impact Assessment:</strong> {approval.ai_explanation}
            </div>
          </div>

          {/* Action Payload */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-slate-700 dark:text-slate-300">Data Payload & Parameters:</span>
              <button
                onClick={() => setIsModifying(!isModifying)}
                className="inline-flex items-center gap-1 text-[11px] text-brand-600 hover:text-brand-700 font-medium"
              >
                <Edit3 className="w-3 h-3" />
                <span>{isModifying ? 'Revert to View' : 'Modify Parameters'}</span>
              </button>
            </div>

            {isModifying ? (
              <div>
                <textarea
                  value={jsonText}
                  onChange={(e) => {
                    setJsonText(e.target.value);
                    setJsonError(null);
                  }}
                  rows={6}
                  className="w-full p-3 font-mono text-[11px] rounded-lg bg-slate-900 text-slate-200 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
                {jsonError && (
                  <p className="text-[11px] text-rose-500 mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {jsonError}
                  </p>
                )}
              </div>
            ) : (
              <pre className="p-3 bg-slate-900 text-slate-200 rounded-xl font-mono text-[11px] overflow-x-auto max-h-40">
                {JSON.stringify(approval.data_payload || {}, null, 2)}
              </pre>
            )}
          </div>

          {/* Review Notes */}
          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Reviewer Authorization Notes (Recorded in Audit Trail):
            </label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Verified customer SLA and approved outreach protocol"
              className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-navy-950 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-brand-500 text-xs"
            />
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-navy-950/50 flex items-center justify-between">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition"
          >
            Cancel
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReject}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold shadow-sm transition"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Reject Action</span>
            </button>
            <button
              onClick={handleApprove}
              disabled={loading}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-sm transition"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              <span>{isModifying ? 'Authorize Modified Payload' : 'Authorize & Execute'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
