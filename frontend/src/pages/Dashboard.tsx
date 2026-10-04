import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitFork,
  CheckSquare,
  ShieldAlert,
  DollarSign,
  Headphones,
  TrendingUp,
  Activity,
  ArrowRight,
  Sparkles,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { api } from '../services/api';
import { DashboardStats } from '../types';

const COLORS = ['#0c87eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await api.analytics.getDashboard();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center gap-3 text-slate-500">
          <RefreshCw className="w-5 h-5 animate-spin text-brand-500" />
          <span className="text-xs font-semibold">Loading platform telemetry...</span>
        </div>
      </div>
    );
  }

  const kpis = [
    {
      title: 'Total Revenue',
      value: `$${(stats?.total_revenue || 0).toLocaleString()}`,
      sub: '+14.2% YoY growth',
      icon: DollarSign,
      color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-950/60 dark:text-emerald-400',
    },
    {
      title: 'Active Workflows',
      value: stats?.active_workflows || 0,
      sub: `${stats?.completed_workflows || 0} completed`,
      icon: GitFork,
      color: 'text-brand-600 bg-brand-100 dark:bg-brand-950/60 dark:text-brand-400',
    },
    {
      title: 'Pending Approvals',
      value: stats?.pending_approvals || 0,
      sub: 'Human-in-the-Loop',
      icon: ShieldAlert,
      color: 'text-amber-600 bg-amber-100 dark:bg-amber-950/60 dark:text-amber-400',
      action: () => navigate('/approvals'),
    },
    {
      title: 'Open Support Tickets',
      value: stats?.open_tickets || 0,
      sub: `${stats?.total_tickets || 0} total tickets`,
      icon: Headphones,
      color: 'text-purple-600 bg-purple-100 dark:bg-purple-950/60 dark:text-purple-400',
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Executive Operations Dashboard
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time multi-agent activity, sales analytics, and autonomous workflow telemetry.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 text-xs font-semibold border border-emerald-200 dark:border-emerald-800">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>AI Orchestrator: {stats?.system_health || 'Operational'}</span>
          </div>
          <button
            onClick={() => navigate('/command')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-500/20 transition"
          >
            <Sparkles className="w-4 h-4" />
            <span>Submit Directive</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            onClick={kpi.action}
            className={`p-5 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm transition hover:shadow-md ${
              kpi.action ? 'cursor-pointer hover:border-amber-400' : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">{kpi.title}</span>
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${kpi.color}`}>
                <kpi.icon className="w-4 h-4" />
              </div>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                {kpi.value}
              </span>
              <p className="text-[11px] text-slate-400 mt-1">{kpi.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sales Revenue Trend Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">Revenue Performance vs Target</h2>
              <p className="text-xs text-slate-400">Monthly sales volume across global regions</p>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-600">
              <TrendingUp className="w-4 h-4" />
              <span>+18.4% Q3 Pace</span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.monthly_sales_chart || []}>
                <defs>
                  <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0c87eb" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#0c87eb" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" opacity={0.4} />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(val) => `$${val / 1000}k`} />
                <Tooltip
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Amount']}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Area type="monotone" dataKey="sales" stroke="#0c87eb" strokeWidth={2.5} fillOpacity={1} fill="url(#salesGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Customer Ticket Category Distribution */}
        <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white mb-1">Support Inquiries by Category</h2>
          <p className="text-xs text-slate-400 mb-4">Customer sentiment cluster segmentation</p>
          <div className="flex-1 h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.ticket_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {(stats?.ticket_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '11px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Grid: Agent Activity & Recent Workflows */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Monitored AI Agents Status */}
        <div className="p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-brand-500" />
              <span>Specialized AI Agents</span>
            </h2>
            <button onClick={() => navigate('/agents')} className="text-xs text-brand-600 hover:underline">
              View telemetry
            </button>
          </div>
          <div className="space-y-3">
            {(stats?.agent_activity || []).map((agent) => (
              <div
                key={agent.agent_type}
                className="p-3 rounded-xl bg-slate-50 dark:bg-navy-950/40 border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs"
              >
                <div>
                  <p className="font-semibold text-slate-800 dark:text-slate-200">{agent.name}</p>
                  <span className="text-[10px] text-slate-400">{agent.total_tasks} completed tasks</span>
                </div>
                <div className="text-right">
                  <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-600">
                    {agent.success_rate}% success
                  </span>
                  <p className="text-[10px] text-slate-400 mt-0.5">{agent.avg_execution_time_ms} ms avg</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Workflows */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-white dark:bg-navy-900 border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-slate-900 dark:text-white">Recent Workflows</h2>
            <button onClick={() => navigate('/workflows')} className="text-xs text-brand-600 hover:underline flex items-center gap-1">
              <span>All Workflows</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 dark:border-slate-800 text-slate-400">
                <tr>
                  <th className="pb-3 font-semibold">Workflow Directive</th>
                  <th className="pb-3 font-semibold">Stages</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Triggered</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
                {(stats?.recent_workflows || []).map((wf) => (
                  <tr
                    key={wf.id}
                    onClick={() => navigate(`/workflows/${wf.id}`)}
                    className="hover:bg-slate-50 dark:hover:bg-slate-800/30 cursor-pointer transition"
                  >
                    <td className="py-3 font-medium text-slate-900 dark:text-white max-w-xs truncate pr-3">
                      {wf.title}
                    </td>
                    <td className="py-3 text-slate-500 font-mono">{wf.steps_count} steps</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                        wf.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                          : wf.status === 'waiting_for_human'
                          ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                          : wf.status === 'running'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                          : 'bg-slate-100 text-slate-700'
                      }`}>
                        {wf.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 text-slate-400 font-mono">
                      {new Date(wf.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
