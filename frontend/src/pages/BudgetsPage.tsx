import React, { useState, useEffect } from 'react';
import {
  PieChart as PieIcon,
  Plus,
  AlertTriangle,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  DollarSign,
  Edit2,
  Trash2,
  Sparkles,
  ArrowUpRight
} from 'lucide-react';
import { api } from '../api/client';
import { BudgetSummary, BudgetPerformanceItem } from '../types';
import { useNotification } from '../context/NotificationContext';

export const BudgetsPage: React.FC = () => {
  const { notify } = useNotification();
  const [summary, setSummary] = useState<BudgetSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [category, setCategory] = useState<string>('Food & Dining');
  const [budgetBucket, setBudgetBucket] = useState<'Needs' | 'Wants' | 'Savings'>('Wants');
  const [monthlyTarget, setMonthlyTarget] = useState<string>('500');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const fetchBudgetData = async () => {
    setIsLoading(true);
    try {
      const data = await api.getBudgetSummary();
      setSummary(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Budgets', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgetData();
  }, []);

  const handleSaveBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    const target = parseFloat(monthlyTarget);
    if (isNaN(target) || target <= 0) {
      notify('warning', 'Invalid Target', 'Please enter a valid monthly budget limit.');
      return;
    }
    setSubmitting(true);
    try {
      await api.createOrUpdateBudget({
        category,
        budget_bucket: budgetBucket,
        monthly_target: target
      });
      notify('success', 'Budget Updated', `Monthly target for ${category} set to $${target.toFixed(2)}`);
      setShowModal(false);
      fetchBudgetData();
    } catch (err: any) {
      notify('error', 'Save Failed', err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <PieIcon className="w-5 h-5 text-emerald-400" />
            50/30/20 Budget Optimization Architecture
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time monthly burn rate audit across Essential Needs (≤50%), Discretionary Wants (≤30%), and Capital Savings (≥20%).
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 transition-all self-stretch sm:self-auto justify-center"
        >
          <Plus className="w-4 h-4" />
          <span>Set Category Target</span>
        </button>
      </div>

      {/* 50/30/20 High-Level Macro Allocation Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Needs Card */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-cyan-400">Needs (Target ≤ 50%)</span>
              <h3 className="text-xl font-extrabold text-white font-mono-num mt-1">
                ${summary ? summary.needs_spent.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
              </h3>
            </div>
            <div className="px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
              Budget: ${summary ? summary.needs_budget.toLocaleString() : '0'}
            </div>
          </div>
          <div className="space-y-1.5 mt-4">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Current Allocation</span>
              <span className="font-semibold text-white">
                {summary && summary.total_spent > 0
                  ? ((summary.needs_spent / summary.total_spent) * 100).toFixed(1)
                  : '0.0'}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                style={{
                  width: `${
                    summary && summary.needs_budget > 0
                      ? Math.min((summary.needs_spent / summary.needs_budget) * 100, 100)
                      : 0
                  }%`
                }}
              />
            </div>
            <span className="text-[10px] text-slate-400 block pt-1">
              Housing, Utilities, Groceries, Commute & Health
            </span>
          </div>
        </div>

        {/* Wants Card */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400">Wants (Target ≤ 30%)</span>
              <h3 className="text-xl font-extrabold text-white font-mono-num mt-1">
                ${summary ? summary.wants_spent.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
              </h3>
            </div>
            <div className="px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
              Budget: ${summary ? summary.wants_budget.toLocaleString() : '0'}
            </div>
          </div>
          <div className="space-y-1.5 mt-4">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Current Allocation</span>
              <span className="font-semibold text-white">
                {summary && summary.total_spent > 0
                  ? ((summary.wants_spent / summary.total_spent) * 100).toFixed(1)
                  : '0.0'}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-purple-500 h-full rounded-full transition-all duration-500"
                style={{
                  width: `${
                    summary && summary.wants_budget > 0
                      ? Math.min((summary.wants_spent / summary.wants_budget) * 100, 100)
                      : 0
                  }%`
                }}
              />
            </div>
            <span className="text-[10px] text-slate-400 block pt-1">
              Dining, Entertainment, Shopping & Hobbies
            </span>
          </div>
        </div>

        {/* Savings Card */}
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl relative overflow-hidden">
          <div className="flex justify-between items-start mb-3">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400">Savings (Target ≥ 20%)</span>
              <h3 className="text-xl font-extrabold text-white font-mono-num mt-1">
                ${summary ? summary.savings_allocated.toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
              </h3>
            </div>
            <div className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              Target: ${summary ? summary.savings_target.toLocaleString() : '0'}
            </div>
          </div>
          <div className="space-y-1.5 mt-4">
            <div className="flex justify-between text-xs text-slate-400">
              <span>Current Allocation</span>
              <span className="font-semibold text-white">
                {summary && summary.total_spent > 0
                  ? ((summary.savings_allocated / (summary.total_spent + summary.savings_allocated)) * 100).toFixed(1)
                  : '0.0'}%
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{
                  width: `${
                    summary && summary.savings_target > 0
                      ? Math.min((summary.savings_allocated / summary.savings_target) * 100, 100)
                      : 0
                  }%`
                }}
              />
            </div>
            <span className="text-[10px] text-slate-400 block pt-1">
              HYSA, Emergency Fund, Roth IRA, 401(k)
            </span>
          </div>
        </div>
      </div>

      {/* Category Performance Breakdown Table */}
      <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-base font-bold text-white">Category Budget Performance Ledger</h3>
            <p className="text-xs text-slate-400">Monthly actual expenditures benchmarked against configured ceiling limits.</p>
          </div>
          <span className="text-xs font-semibold text-slate-400 bg-slate-800 px-3 py-1 rounded-lg">
            {summary ? summary.items.length : 0} Monitored Categories
          </span>
        </div>

        {isLoading ? (
          <div className="py-12 flex justify-center items-center text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mr-3" />
            Auditing budget performance...
          </div>
        ) : !summary || summary.items.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">
            No active budget limits configured yet. Click "Set Category Target" above to define rules.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Category</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Bucket</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Monthly Target</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Actual Spent</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Remaining</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Utilization</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {summary.items.map((item, idx) => {
                  const isOver = item.status === 'EXCEEDED';
                  const isWarn = item.status === 'APPROACHING';
                  return (
                    <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-white flex items-center gap-2">
                        <span>{item.category}</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            item.budget_bucket === 'Needs'
                              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                              : item.budget_bucket === 'Wants'
                              ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          }`}
                        >
                          {item.budget_bucket}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono-num text-white">
                        ${item.monthly_target.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4 font-mono-num font-semibold text-white">
                        ${item.actual_spent.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4 font-mono-num">
                        <span className={item.remaining_amount < 0 ? 'text-rose-400 font-semibold' : 'text-emerald-400'}>
                          ${item.remaining_amount.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 w-44">
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${
                                isOver ? 'bg-rose-500' : isWarn ? 'bg-amber-500' : 'bg-emerald-500'
                              }`}
                              style={{ width: `${Math.min(item.utilization_pct, 100)}%` }}
                            />
                          </div>
                          <span className="font-mono-num text-[11px] w-12 text-right">
                            {item.utilization_pct.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <span
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                            isOver
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                              : isWarn
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          }`}
                        >
                          {isOver ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Target Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-[#0D1322] border border-slate-700/80 shadow-2xl p-6 relative">
            <h3 className="text-base font-bold text-white mb-1">Set Category Budget Target</h3>
            <p className="text-xs text-slate-400 mb-4">
              Configure spending limit ceiling and 50/30/20 classification.
            </p>

            <form onSubmit={handleSaveBudget} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Category</label>
                <select
                  value={category}
                  onChange={e => setCategory(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Housing">Housing</option>
                  <option value="Utilities">Utilities</option>
                  <option value="Groceries">Groceries</option>
                  <option value="Food & Dining">Food & Dining</option>
                  <option value="Transportation">Transportation</option>
                  <option value="Entertainment & Subscriptions">Entertainment & Subscriptions</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Health & Medical">Health & Medical</option>
                  <option value="Savings & Investments">Savings & Investments</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">50/30/20 Bucket</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Needs', 'Wants', 'Savings'] as const).map(b => (
                    <button
                      key={b}
                      type="button"
                      onClick={() => setBudgetBucket(b)}
                      className={`py-2 text-xs font-bold rounded-xl border transition-all ${
                        budgetBucket === b
                          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                          : 'bg-slate-900 border-slate-700 text-slate-400 hover:text-white'
                      }`}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">Monthly Ceiling Target ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  value={monthlyTarget}
                  onChange={e => setMonthlyTarget(e.target.value)}
                  placeholder="e.g. 600.00"
                  required
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-sm font-mono-num text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 disabled:opacity-50"
                >
                  {submitting ? 'Saving...' : 'Save Target'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
