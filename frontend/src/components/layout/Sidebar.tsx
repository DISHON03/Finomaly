import React from 'react';
import {
  LayoutDashboard,
  Receipt,
  PieChart,
  ShieldAlert,
  TrendingUp,
  RefreshCw,
  Lightbulb,
  Target,
  Sparkles,
  BarChart3,
  RotateCcw,
  User as UserIcon,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { api } from '../../api/client';

export type PageId =
  | 'dashboard'
  | 'transactions'
  | 'budgets'
  | 'anomalies'
  | 'forecasting'
  | 'recurring'
  | 'insights'
  | 'savings'
  | 'categorization'
  | 'tableau';

interface SidebarProps {
  activePage: PageId;
  setActivePage: (page: PageId) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  activeAnomaliesCount: number;
  onRefreshData?: () => void;
}

const NAV_ITEMS: { id: PageId; label: string; icon: React.ReactNode; badge?: string }[] = [
  { id: 'dashboard', label: 'Executive Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
  { id: 'transactions', label: 'Transactions Ledger', icon: <Receipt className="w-5 h-5" /> },
  { id: 'budgets', label: '50/30/20 Budget Planner', icon: <PieChart className="w-5 h-5" /> },
  { id: 'anomalies', label: 'Anomaly Detector', icon: <ShieldAlert className="w-5 h-5" /> },
  { id: 'forecasting', label: 'Expense Forecasting', icon: <TrendingUp className="w-5 h-5" /> },
  { id: 'recurring', label: 'Recurring Subscriptions', icon: <RefreshCw className="w-5 h-5" /> },
  { id: 'insights', label: 'Financial Insights', icon: <Lightbulb className="w-5 h-5" /> },
  { id: 'savings', label: 'Savings Goals', icon: <Target className="w-5 h-5" /> },
  { id: 'categorization', label: 'Smart Rules & ML', icon: <Sparkles className="w-5 h-5" /> },
  { id: 'tableau', label: 'Tableau BI Layer', icon: <BarChart3 className="w-5 h-5" /> },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  setActivePage,
  isOpen,
  setIsOpen,
  activeAnomaliesCount,
  onRefreshData
}) => {
  const { user } = useAuth();
  const { notify } = useNotification();

  const handleResetDemo = async () => {
    try {
      await api.resetDemoProfile();
      notify('success', 'Demo Reset', 'Reset account to standard multi-year baseline.');
      if (onRefreshData) onRefreshData();
    } catch (err: any) {
      notify('error', 'Reset Failed', err.message);
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-72 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } bg-[#0D1322] border-r border-slate-800/80 shadow-2xl`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <img
              src="/finomaly-logo.svg"
              alt="Finomaly Logo"
              className="w-10 h-10 rounded-xl shadow-lg shadow-black/30"
            />
            <div>
              <div className="font-extrabold text-lg text-white tracking-tight flex items-center gap-1.5">
                Finomaly
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  AI
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-medium">Expense & Anomaly Analytics</div>
            </div>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
          <div className="px-3 pb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Analytics & Operations
          </div>
          {NAV_ITEMS.map(item => {
            const isActive = activePage === item.id;
            const isAnomaly = item.id === 'anomalies' && activeAnomaliesCount > 0;

            return (
              <button
                key={item.id}
                onClick={() => {
                  setActivePage(item.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`transition-colors ${
                      isActive ? 'text-emerald-400' : 'text-slate-400 group-hover:text-slate-200'
                    }`}
                  >
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </div>

                {/* Badges */}
                {isAnomaly && (
                  <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse">
                    {activeAnomaliesCount}
                  </span>
                )}
                {item.id === 'tableau' && (
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                    BI
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Demo Indicator & Reset Card */}
        {user?.is_demo && (
          <div className="px-4 py-3 mx-4 mb-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <div className="flex items-center justify-between text-xs font-semibold text-amber-400 mb-1">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                Sample Demo Data Active
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed mb-2.5">
              Populated with multi-year synthetic banking transactions for portfolio evaluation.
            </p>
            <button
              onClick={handleResetDemo}
              className="w-full flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-medium border border-amber-500/30 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Demo Profile
            </button>
          </div>
        )}

        {/* User Footer */}
        <div className="px-4 py-3.5 border-t border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-sm">
              <UserIcon className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="truncate text-left">
              <div className="text-sm font-semibold text-white truncate">
                {user?.full_name || 'Guest User'}
              </div>
              <div className="text-[11px] text-slate-400 truncate">
                {user?.email || 'demo@finomaly.io'}
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
