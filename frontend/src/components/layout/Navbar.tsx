import React from 'react';
import {
  Menu,
  Plus,
  ShieldCheck,
  Sun,
  Moon,
  LogOut,
  Sparkles
} from 'lucide-react';
import { PageId } from './Sidebar';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useNotification } from '../../context/NotificationContext';
import { api } from '../../api/client';

interface NavbarProps {
  activePage: PageId;
  onOpenSidebar: () => void;
  onOpenAddModal: () => void;
  onScanComplete?: () => void;
}

const PAGE_METADATA: Record<PageId, { title: string; subtitle: string }> = {
  dashboard: {
    title: 'Executive Financial Dashboard',
    subtitle: 'Comprehensive cash flow, spending trend, and monthly KPI audit.'
  },
  transactions: {
    title: 'Transactions Ledger & Operations',
    subtitle: 'Manage, search, categorize, and import/export financial transaction records.'
  },
  budgets: {
    title: '50/30/20 Budget Planner',
    subtitle: 'Monitor category limits, savings velocity, and real-time variance thresholds.'
  },
  anomalies: {
    title: 'Spending Anomaly Detector',
    subtitle: 'Machine learning Isolation Forest & statistical IQR baseline outlier auditing.'
  },
  forecasting: {
    title: 'Expense Forecasting & Runway Model',
    subtitle: 'Double Exponential Smoothing forward burn projection with 95% confidence bounds.'
  },
  recurring: {
    title: 'Recurring Payment Cadence Detector',
    subtitle: 'Automated periodic cadence clustering and annualized subscription run-rate audit.'
  },
  insights: {
    title: 'Verified Financial Insights',
    subtitle: 'Data-driven mathematical observations calculated strictly from transaction history.'
  },
  savings: {
    title: 'Savings Goals & Velocity',
    subtitle: 'Track milestones, contribution patterns, and projected completion trajectories.'
  },
  categorization: {
    title: 'Smart Categorization & Learned Rules',
    subtitle: 'Interactive taxonomy matching and personalized merchant correction memory.'
  },
  tableau: {
    title: 'Tableau Business Intelligence Reporting Layer',
    subtitle: 'Documented CSV datasets, SQL views, and dashboard blueprints for Tableau Desktop & Public.'
  }
};

export const Navbar: React.FC<NavbarProps> = ({
  activePage,
  onOpenSidebar,
  onOpenAddModal,
  onScanComplete
}) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { notify } = useNotification();
  const [isScanning, setIsScanning] = React.useState(false);

  const meta = PAGE_METADATA[activePage];

  const handleScanAnomalies = async () => {
    setIsScanning(true);
    try {
      const result = await api.scanAnomalies();
      notify(
        'info',
        'Anomaly Scan Complete',
        `Analyzed ${result.scanned_transactions} transactions via ${result.method_used}. Detected ${result.new_anomalies_detected} new alerts.`
      );
      if (onScanComplete) onScanComplete();
    } catch (err: any) {
      notify('error', 'Scan Error', err.message);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <header className="sticky top-0 z-30 h-20 px-6 lg:px-8 flex items-center justify-between border-b border-slate-800/80 bg-[#0B0F19]/80 backdrop-blur-md">
      {/* Page Title & Mobile Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenSidebar}
          className="p-2 -ml-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
        >
          <Menu className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            {meta.title}
          </h1>
          <p className="hidden sm:block text-xs text-slate-400 mt-0.5">{meta.subtitle}</p>
        </div>
      </div>

      {/* Action Buttons & Utilities */}
      <div className="flex items-center gap-3">
        {/* ML Scan Button */}
        <button
          onClick={handleScanAnomalies}
          disabled={isScanning}
          className="hidden md:flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-cyan-300 bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-700/50 shadow-sm transition-all"
        >
          <Sparkles className={`w-4 h-4 text-cyan-400 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Analyzing Spend...' : 'Run ML Scan'}
        </button>

        {/* Add Transaction Button */}
        <button
          onClick={onOpenAddModal}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 shadow-lg shadow-emerald-600/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <Plus className="w-4 h-4" />
          <span>New Transaction</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/80 border border-slate-800 transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
        </button>

        {/* User Signout */}
        <button
          onClick={logout}
          title="Sign Out"
          className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 border border-slate-800 hover:border-rose-900/40 transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
