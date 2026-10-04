import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { api } from '../../services/api';

export const Layout: React.FC = () => {
  const [pendingApprovals, setPendingApprovals] = useState<number>(0);

  const checkApprovals = async () => {
    try {
      const data = await api.approvals.list('pending');
      setPendingApprovals(data.length);
    } catch {
      // Ignore background check errors
    }
  };

  useEffect(() => {
    checkApprovals();
    const interval = setInterval(checkApprovals, 12000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-navy-950">
      <Sidebar pendingApprovalsCount={pendingApprovals} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
