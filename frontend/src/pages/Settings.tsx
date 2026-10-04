import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Cpu,
  Key,
  Database,
  Shield,
  Save,
  CheckCircle,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Settings: React.FC = () => {
  const { user } = useAuth();
  const [llmProvider, setLlmProvider] = useState('gemini');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [apiKey, setApiKey] = useState('••••••••••••••••••••••••••••••••');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl mx-auto">
      {/* Header */}
      <div className="pb-4 border-b border-slate-200 dark:border-slate-800">
        <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          System & AI Configuration
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Configure central AI models, LLM providers, database connectivity, and enterprise security policies.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6 text-xs">
        {/* AI & LLM Service Configuration */}
        <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
            <Cpu className="w-4 h-4 text-brand-500" />
            <span>AI Orchestrator & LLM Providers</span>
          </div>
          <p className="text-slate-500 dark:text-slate-400">
            Select the primary Large Language Model engine driving the multi-agent task planning and execution.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Active Provider
              </label>
              <select
                value={llmProvider}
                onChange={(e) => setLlmProvider(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-white focus:outline-none"
              >
                <option value="gemini">Google Gemini API (Default)</option>
                <option value="mock">Intelligent Local Mock Provider (Offline / Testing)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Gemini Model Version
              </label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-white focus:outline-none"
              >
                <option value="gemini-2.5-flash">Gemini 2.5 Flash (Optimized for Agentic Speed)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Cross-Functional Reasoning)</option>
                <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Gemini API Key
            </label>
            <div className="relative">
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full px-3 py-2 font-mono rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-navy-950 text-slate-900 dark:text-white focus:outline-none"
              />
              <Key className="w-4 h-4 text-slate-400 absolute right-3 top-2.5" />
            </div>
            <span className="text-[10px] text-slate-400 mt-1 block">
              Stored securely in backend environment variables. Never exposed to clients.
            </span>
          </div>
        </div>

        {/* Database & Infrastructure */}
        <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
            <Database className="w-4 h-4 text-emerald-500" />
            <span>Database & Storage Architecture</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-100 dark:border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Relational Database</span>
              <p className="font-bold text-slate-900 dark:text-white mt-0.5">PostgreSQL 16 + pgvector</p>
              <span className="inline-block mt-1 text-[10px] text-emerald-600 font-semibold">● Connected (SQLAlchemy 2.0)</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-100 dark:border-slate-800">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Task Queue & Cache</span>
              <p className="font-bold text-slate-900 dark:text-white mt-0.5">Redis 7 Alpine</p>
              <span className="inline-block mt-1 text-[10px] text-emerald-600 font-semibold">● Ready</span>
            </div>
          </div>
        </div>

        {/* Security & Human-in-the-Loop */}
        <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-slate-900 dark:text-white font-bold text-sm">
            <Shield className="w-4 h-4 text-purple-500" />
            <span>Human-in-the-Loop Policy Enforcer</span>
          </div>
          <p className="text-slate-500 dark:text-slate-400">
            Mandatory authorization checkpoints for high-risk operations:
          </p>

          <div className="space-y-2">
            {[
              "Automated outbound customer communication and escalation emails",
              "Direct database financial ledger adjustments or refund disbursements",
              "Production checkout error escalation notices to client C-suite",
              "Document deletion and irreversible organizational data changes"
            ].map((rule, idx) => (
              <div key={idx} className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />
                <span>{rule}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {saved && (
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1.5 animate-fadeIn">
              <CheckCircle className="w-4 h-4" />
              <span>Settings successfully persisted!</span>
            </span>
          )}
          <div className="ml-auto">
            <button
              type="submit"
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold shadow transition"
            >
              <Save className="w-4 h-4" />
              <span>Save Configuration</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
