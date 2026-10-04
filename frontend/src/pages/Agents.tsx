import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Activity,
  CheckCircle2,
  Clock,
  Pause,
  Play,
  RefreshCw,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { AgentMetric } from '../types';

export const Agents: React.FC = () => {
  const [agents, setAgents] = useState<AgentMetric[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const data = await api.agents.list();
      setAgents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleToggle = async (agentType: string) => {
    try {
      await api.agents.toggleStatus(agentType);
      fetchAgents();
    } catch (err) {
      console.error(err);
    }
  };

  const getAgentRoleDescription = (type: string) => {
    switch (type) {
      case 'planner':
        return 'Decomposes unstructured natural language into structured multi-agent execution plans with dependency management.';
      case 'finance':
        return 'Audits sales metrics, calculates revenue trends, and identifies statistical financial anomalies and outlier refunds.';
      case 'support':
        return 'Clusters customer tickets, determines sentiment & priority, and prepares escalation drafts for SLA breaches.';
      case 'document':
        return 'Executes hybrid vector RAG retrieval, extracts contractual clauses, and verifies compliance guidelines.';
      case 'reporting':
        return 'Aggregates multi-agent intelligence into executive briefing reports with downloadable formats.';
      default:
        return 'Autonomous specialized agent.';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            AI Agent Monitoring & Telemetry
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time operational status, execution latency, and success metrics for all specialized AI agents.
          </p>
        </div>
        <button
          onClick={fetchAgents}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-navy-900 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div
            key={agent.agent_type}
            className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">{agent.name}</h3>
                    <span className="text-[10px] font-mono text-slate-400 uppercase">
                      type: {agent.agent_type}
                    </span>
                  </div>
                </div>

                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                  agent.status === 'paused'
                    ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400'
                    : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400'
                }`}>
                  {agent.status}
                </span>
              </div>

              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed min-h-[48px]">
                {getAgentRoleDescription(agent.agent_type)}
              </p>

              {/* Stats Box */}
              <div className="grid grid-cols-2 gap-2 p-3 rounded-xl bg-slate-50 dark:bg-navy-950 border border-slate-100 dark:border-slate-800 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block">Total Executions</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{agent.total_tasks} runs</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Success Rate</span>
                  <span className="font-bold text-emerald-600 dark:text-emerald-400">{agent.success_rate}%</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Avg Latency</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200 font-mono">{agent.avg_execution_time_ms} ms</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 block">Failures</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{agent.failed_tasks}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between mt-4">
              <span className="text-[10px] text-slate-400 font-mono">
                Active: {new Date(agent.last_active_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <button
                onClick={() => handleToggle(agent.agent_type)}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  agent.status === 'paused'
                    ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                }`}
              >
                {agent.status === 'paused' ? (
                  <>
                    <Play className="w-3 h-3 fill-current" />
                    <span>Resume</span>
                  </>
                ) : (
                  <>
                    <Pause className="w-3 h-3" />
                    <span>Pause Agent</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
