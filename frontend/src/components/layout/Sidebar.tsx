import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  CheckSquare,
  GitFork,
  Cpu,
  ShieldAlert,
  FileText,
  BarChart3,
  ScrollText,
  Users,
  Settings,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  pendingApprovalsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ pendingApprovalsCount = 0 }) => {
  const { user, isAdmin, isManager } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'AI Command Center', path: '/command', icon: Sparkles, highlight: true },
    { name: 'Workflows', path: '/workflows', icon: GitFork },
    { name: 'Tasks', path: '/tasks', icon: CheckSquare },
    { name: 'Approvals', path: '/approvals', icon: ShieldAlert, badge: pendingApprovalsCount },
    { name: 'AI Agents', path: '/agents', icon: Cpu },
    { name: 'Documents & RAG', path: '/documents', icon: FileText },
    { name: 'Reports', path: '/reports', icon: BarChart3 },
    ...(isManager ? [{ name: 'Audit Logs', path: '/audit', icon: ScrollText }] : []),
    ...(isAdmin ? [{ name: 'User Management', path: '/users', icon: Users }] : []),
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white dark:bg-navy-900 border-r border-slate-200 dark:border-slate-800 flex flex-col shrink-0 h-screen sticky top-0 transition-colors duration-200">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-900 dark:text-white leading-tight">AI BizOps</h1>
            <p className="text-[10px] text-brand-600 dark:text-brand-400 font-semibold tracking-wider uppercase">Enterprise Orchestrator</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
              } ${item.highlight ? 'border border-brand-200/60 dark:border-brand-800/60' : ''}`
            }
          >
            <div className="flex items-center gap-3">
              <item.icon className={`w-4 h-4 ${item.highlight ? 'text-brand-500 animate-pulse' : ''}`} />
              <span>{item.name}</span>
            </div>
            {item.badge !== undefined && item.badge > 0 && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white animate-bounce">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User Info Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-navy-950/40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-900 dark:text-white truncate">{user?.full_name}</p>
            <span className="inline-block px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 uppercase">
              {user?.role}
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
};
