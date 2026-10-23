import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  PiggyBank,
  AlertTriangle,
  Calendar,
  Layers,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  PieChart as PieIcon,
  ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { api } from '../api/client';
import { DashboardKPIs, MonthlyTrendPoint, CategoryBreakdownItem, RecentTransactionItem, AnomalyAlert } from '../types';
import { PageId } from '../components/layout/Sidebar';
import { useNotification } from '../context/NotificationContext';

interface DashboardPageProps {
  onNavigate: (page: PageId) => void;
  onOpenAddModal: () => void;
}

const CATEGORY_COLORS = [
  '#10B981', // Emerald
  '#06B6D4', // Cyan
  '#F59E0B', // Amber
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#3B82F6', // Blue
  '#F97316', // Orange
  '#14B8A6', // Teal
  '#64748B', // Slate
];

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate, onOpenAddModal }) => {
  const { notify } = useNotification();
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [trends, setTrends] = useState<MonthlyTrendPoint[]>([]);
  const [categories, setCategories] = useState<CategoryBreakdownItem[]>([]);
  const [recentTx, setRecentTx] = useState<RecentTransactionItem[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<AnomalyAlert[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState<string>('All');

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [kpisRes, trendsRes, catsRes, txRes, alertsRes] = await Promise.all([
        api.getKPIs({ category: categoryFilter }),
        api.getTrends(),
        api.getCategoryBreakdown(),
        api.getRecentTransactions(6),
        api.getAnomalies('active')
      ]);
      setKpis(kpisRes);
      setTrends(trendsRes);
      setCategories(catsRes);
      setRecentTx(txRes);
      setActiveAlerts(alertsRes.slice(0, 3));
    } catch (err: any) {
      notify('error', 'Dashboard Load Failed', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [categoryFilter]);

  const handleDismissAlert = async (id: number) => {
    try {
      await api.updateAnomalyStatus(id, 'dismissed');
      setActiveAlerts(prev => prev.filter(a => a.id !== id));
      notify('info', 'Alert Dismissed', 'Anomaly alert marked as dismissed.');
    } catch (err: any) {
      notify('error', 'Action Failed', err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Filter Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-300">Slice by Category:</span>
          <select
            value={categoryFilter}
            onChange={e => setCategoryFilter(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="All">All Categories</option>
            <option value="Housing">Housing</option>
            <option value="Groceries">Groceries</option>
            <option value="Food & Dining">Food & Dining</option>
            <option value="Transportation">Transportation</option>
            <option value="Entertainment & Subscriptions">Entertainment</option>
            <option value="Shopping">Shopping</option>
            <option value="Utilities">Utilities</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Calendar className="w-3.5 h-3.5 text-cyan-400" />
          <span>Active Period: Trailing 12-Month Analytical Slice</span>
        </div>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Income */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Income</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-extrabold text-white font-mono-num">
            ${kpis ? kpis.total_income.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
          </div>
          <div className="mt-2 text-xs text-emerald-400 flex items-center gap-1">
            <span>Primary Revenue Inflow</span>
          </div>
        </div>

        {/* Total Expenses */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Expenses</span>
            <div className="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-400 flex items-center justify-center">
              <TrendingDown className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-extrabold text-white font-mono-num">
            ${kpis ? kpis.total_expenses.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Recorded Outflows
          </div>
        </div>

        {/* Net Savings */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Net Cash Flow</span>
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
              <Wallet className="w-4 h-4" />
            </div>
          </div>
          <div
            className={`text-2xl lg:text-3xl font-extrabold font-mono-num ${
              kpis && kpis.remaining_balance >= 0 ? 'text-cyan-400' : 'text-rose-400'
            }`}
          >
            ${kpis ? kpis.remaining_balance.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
          </div>
          <div className="mt-2 text-xs text-cyan-300/80">
            Retained Liquid Surplus
          </div>
        </div>

        {/* Savings Rate */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Savings Velocity</span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
              <PiggyBank className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl lg:text-3xl font-extrabold text-purple-400 font-mono-num">
            {kpis ? kpis.savings_rate.toFixed(1) : '0.0'}%
          </div>
          <div className="mt-2 text-xs text-slate-400">
            50/30/20 Target: ≥ 20.0%
          </div>
        </div>
      </div>

      {/* 50/30/20 Compliance Strip */}
      {kpis && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 to-[#111827] border border-slate-800 shadow-lg">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                50/30/20 Cash Flow Allocation Status
              </h3>
              <p className="text-xs text-slate-400">
                Audits essential needs vs discretionary lifestyle vs capital preservation.
              </p>
            </div>
            <button
              onClick={() => onNavigate('budgets')}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 self-start md:self-auto"
            >
              Open Budget Planner <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Essential Needs</span>
                <span className="font-semibold text-white">{kpis.needs_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-cyan-500 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(kpis.needs_pct, 100)}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500 mt-1 block">Target: ≤ 50%</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Discretionary Wants</span>
                <span className={`font-semibold ${kpis.wants_pct > 30 ? 'text-amber-400' : 'text-white'}`}>
                  {kpis.wants_pct}%
                </span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${kpis.wants_pct > 30 ? 'bg-amber-500' : 'bg-purple-500'}`}
                  style={{ width: `${Math.min(kpis.wants_pct, 100)}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500 mt-1 block">Target: ≤ 30%</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">Net Savings Allocated</span>
                <span className="font-semibold text-emerald-400">{kpis.savings_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(kpis.savings_pct, 100)}%` }}
                />
              </div>
              <span className="text-[10px] text-slate-500 mt-1 block">Target: ≥ 20%</span>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Charts Section (2 Columns) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cash Flow Timeline Chart (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Monthly Spending & Cash Flow Trajectory</h2>
              <p className="text-xs text-slate-400">Income vs expenses across the trailing 12 months</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                <span className="text-slate-300">Income</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="text-slate-300">Expense</span>
              </div>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="year_month" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} tickFormatter={v => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', borderRadius: '12px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="income" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#incomeGrad)" />
                <Area type="monotone" dataKey="expense" stroke="#F43F5E" strokeWidth={2} fillOpacity={1} fill="url(#expenseGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Donut (1 col) */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Category Breakdown</h2>
              <p className="text-xs text-slate-400">Share of recorded spend</p>
            </div>
            <PieIcon className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categories.slice(0, 6)}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {categories.slice(0, 6).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', borderRadius: '12px' }}
                  formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Spent']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 mt-2 flex-1 overflow-y-auto max-h-36 pr-1">
            {categories.slice(0, 5).map((c, i) => (
              <div key={c.category} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 truncate">
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }}
                  />
                  <span className="text-slate-300 truncate">{c.category}</span>
                </div>
                <div className="font-mono-num font-semibold text-slate-200">
                  ${c.amount.toFixed(0)} <span className="text-slate-500 font-normal">({c.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Lower Row: Active Anomalies + Recent Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Anomaly Alerts Widget */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <div>
                <h2 className="text-base font-bold text-white tracking-tight">Active Spending Anomalies</h2>
                <p className="text-xs text-slate-400">Flagged outliers with mathematical rationale</p>
              </div>
            </div>
            <button
              onClick={() => onNavigate('anomalies')}
              className="text-xs font-semibold text-rose-400 hover:text-rose-300 flex items-center gap-1"
            >
              View All ({kpis?.active_anomalies_count || 0}) <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {activeAlerts.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-slate-400">
              <Sparkles className="w-8 h-8 text-emerald-400 mb-2 opacity-60" />
              <div className="text-sm font-semibold text-slate-200">No Active Anomalies</div>
              <p className="text-xs text-slate-500 mt-1">All current transactions align with your baseline.</p>
            </div>
          ) : (
            <div className="space-y-3 flex-1">
              {activeAlerts.map(alert => (
                <div
                  key={alert.id}
                  className="p-3.5 rounded-xl bg-slate-900/80 border border-rose-900/30 hover:border-rose-700/50 transition-colors flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-slate-200 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                      {alert.title}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{alert.explanation}</p>
                  <div className="flex items-center justify-between pt-1 text-[11px]">
                    <span className="text-cyan-400 font-mono-num">{alert.comparison_metric}</span>
                    <button
                      onClick={() => handleDismissAlert(alert.id)}
                      className="text-slate-400 hover:text-white font-medium hover:underline"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Transactions Widget */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Recent Transactions</h2>
              <p className="text-xs text-slate-400">Latest recorded ledger entries</p>
            </div>
            <button
              onClick={() => onNavigate('transactions')}
              className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
            >
              Full Ledger <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2 flex-1">
            {recentTx.map(tx => (
              <div
                key={tx.id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/50 hover:bg-slate-900 border border-slate-800/80 transition-colors"
              >
                <div className="flex items-center gap-3 truncate">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                      tx.transaction_type === 'Income'
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : tx.transaction_type === 'Transfer'
                        ? 'bg-indigo-500/10 text-indigo-400'
                        : 'bg-rose-500/10 text-rose-400'
                    }`}
                  >
                    {tx.transaction_type === 'Income' ? '+' : '-'}
                  </div>
                  <div className="truncate">
                    <div className="text-xs font-semibold text-slate-200 truncate">{tx.clean_merchant}</div>
                    <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                      <span>{tx.date}</span>
                      <span>•</span>
                      <span className="text-slate-400">{tx.category}</span>
                    </div>
                  </div>
                </div>

                <div
                  className={`text-sm font-bold font-mono-num ${
                    tx.transaction_type === 'Income' ? 'text-emerald-400' : 'text-slate-100'
                  }`}
                >
                  {tx.transaction_type === 'Income' ? '+' : '-'}${tx.amount.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
