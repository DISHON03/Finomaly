import React, { useState, useEffect } from 'react';
import {
  Target,
  Plus,
  TrendingUp,
  Calendar,
  CheckCircle2,
  DollarSign,
  PiggyBank,
  Trash2,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { SavingsGoal } from '../types';
import { useNotification } from '../context/NotificationContext';

export const SavingsPage: React.FC = () => {
  const { notify } = useNotification();
  const [goals, setGoals] = useState<SavingsGoal[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // New Goal Modal state
  const [showGoalModal, setShowGoalModal] = useState<boolean>(false);
  const [goalName, setGoalName] = useState<string>('');
  const [targetAmount, setTargetAmount] = useState<string>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [goalCategory, setGoalCategory] = useState<string>('Emergency Fund');

  // Contribution Modal state
  const [selectedGoal, setSelectedGoal] = useState<SavingsGoal | null>(null);
  const [contribAmount, setContribAmount] = useState<string>('');
  const [contribNotes, setContribNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const fetchGoals = async () => {
    setIsLoading(true);
    try {
      const data = await api.getSavingsGoals();
      setGoals(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Goals', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    const target = parseFloat(targetAmount);
    if (!goalName.trim() || isNaN(target) || target <= 0) {
      notify('warning', 'Invalid Input', 'Please enter a goal name and valid target amount.');
      return;
    }
    setSubmitting(true);
    try {
      await api.createSavingsGoal({
        name: goalName.trim(),
        target_amount: target,
        target_date: targetDate || '2027-12-31',
        category: goalCategory
      });
      notify('success', 'Goal Created', `Created savings goal: "${goalName}"`);
      setShowGoalModal(false);
      setGoalName('');
      setTargetAmount('');
      fetchGoals();
    } catch (err: any) {
      notify('error', 'Failed to Create', err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddContribution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGoal) return;
    const amount = parseFloat(contribAmount);
    if (isNaN(amount) || amount <= 0) {
      notify('warning', 'Invalid Amount', 'Please enter a valid contribution amount.');
      return;
    }
    setSubmitting(true);
    try {
      await api.addGoalContribution(selectedGoal.id, {
        amount,
        date: new Date().toISOString().slice(0, 10),
        notes: contribNotes.trim() || undefined
      });
      notify('success', 'Contribution Added', `Added $${amount.toFixed(2)} to ${selectedGoal.name}`);
      setSelectedGoal(null);
      setContribAmount('');
      setContribNotes('');
      fetchGoals();
    } catch (err: any) {
      notify('error', 'Contribution Failed', err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteGoal = async (id: number, name: string) => {
    if (!window.confirm(`Are you sure you want to delete goal "${name}"?`)) return;
    try {
      await api.deleteSavingsGoal(id);
      notify('info', 'Goal Deleted', `Deleted goal "${name}".`);
      setGoals(prev => prev.filter(g => g.id !== id));
    } catch (err: any) {
      notify('error', 'Delete Failed', err.message);
    }
  };

  const totalSaved = goals.reduce((acc, g) => acc + g.current_amount, 0);
  const totalTarget = goals.reduce((acc, g) => acc + g.target_amount, 0);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-teal-400" />
            Capital Preservation & Savings Velocity Tracking
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Monitor target milestones, projected completion runway, and recurring monthly capital contributions.
          </p>
        </div>

        <button
          onClick={() => setShowGoalModal(true)}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-2 shadow-lg shadow-teal-500/20 transition-all self-stretch sm:self-auto justify-center"
        >
          <Plus className="w-4 h-4" />
          <span>New Savings Target</span>
        </button>
      </div>

      {/* Aggregate KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Total Capital Accumulated
          </span>
          <div className="text-2xl font-extrabold text-teal-400 font-mono-num">
            ${totalSaved.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Liquid Savings Balance</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Total Target Milestone
          </span>
          <div className="text-2xl font-extrabold text-white font-mono-num">
            ${totalTarget.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Combined Long-Term Targets</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Overall Goal Progress
          </span>
          <div className="text-2xl font-extrabold text-emerald-400 font-mono-num">
            {totalTarget > 0 ? ((totalSaved / totalTarget) * 100).toFixed(1) : '0.0'}%
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            {goals.filter(g => g.is_completed).length} of {goals.length} Goals Completed
          </span>
        </div>
      </div>

      {/* Goals Grid */}
      {isLoading ? (
        <div className="py-16 flex justify-center items-center text-slate-400 text-sm">
          <div className="w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin mr-3" />
          Loading savings milestones...
        </div>
      ) : goals.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-slate-800">
          <PiggyBank className="w-12 h-12 text-teal-400 mx-auto mb-3 opacity-80" />
          <h4 className="text-base font-bold text-white mb-1">No Active Savings Goals</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
            Establish financial milestones like an Emergency Fund, Home Downpayment, or Travel Fund.
          </p>
          <button
            onClick={() => setShowGoalModal(true)}
            className="px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs"
          >
            Create Your First Goal
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {goals.map(goal => {
            const isCompleted = goal.is_completed || goal.progress_pct >= 100;

            return (
              <div
                key={goal.id}
                className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">
                      {goal.category}
                    </span>
                    <button
                      onClick={() => handleDeleteGoal(goal.id, goal.name)}
                      className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                      title="Delete Goal"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <h3 className="text-base font-bold text-white mb-1">{goal.name}</h3>

                  <div className="flex items-baseline justify-between mt-3 mb-1">
                    <span className="text-xl font-extrabold text-teal-400 font-mono-num">
                      ${goal.current_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                    <span className="text-xs text-slate-400 font-mono-num">
                      target ${goal.target_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden my-2">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isCompleted ? 'bg-emerald-400' : 'bg-gradient-to-r from-teal-500 to-emerald-400'
                      }`}
                      style={{ width: `${Math.min(goal.progress_pct, 100)}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-400 mt-1 mb-4">
                    <span>{goal.progress_pct.toFixed(1)}% Completed</span>
                    <span>
                      {goal.remaining_amount > 0
                        ? `$${goal.remaining_amount.toFixed(0)} remaining`
                        : 'Goal Achieved!'}
                    </span>
                  </div>

                  <div className="space-y-1 text-[11px] text-slate-400 pt-2 border-t border-slate-800/80">
                    <div className="flex justify-between">
                      <span>Target Date:</span>
                      <span className="text-white font-mono-num">{goal.target_date}</span>
                    </div>
                    {goal.projected_completion_date && (
                      <div className="flex justify-between">
                        <span>Est. Completion:</span>
                        <span className="text-cyan-400 font-mono-num">{goal.projected_completion_date}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-800/80">
                  <button
                    onClick={() => {
                      setSelectedGoal(goal);
                      setContribAmount('');
                    }}
                    className="w-full py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Plus className="w-3.5 h-3.5 text-teal-400" />
                    <span>Deposit Contribution</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create Goal Modal */}
      {showGoalModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-[#0D1322] border border-slate-700 shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1">Create Savings Target</h3>
            <p className="text-xs text-slate-400 mb-4">Establish target reserve for emergency or wealth accumulation.</p>

            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Goal Name</label>
                <input
                  type="text"
                  value={goalName}
                  onChange={e => setGoalName(e.target.value)}
                  placeholder="e.g. 6-Month Emergency Fund"
                  required
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  value={targetAmount}
                  onChange={e => setTargetAmount(e.target.value)}
                  placeholder="10000.00"
                  required
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-mono-num text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Target Date</label>
                <input
                  type="date"
                  value={targetDate}
                  onChange={e => setTargetDate(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                <select
                  value={goalCategory}
                  onChange={e => setGoalCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-teal-500"
                >
                  <option value="Emergency Fund">Emergency Fund</option>
                  <option value="Investments">Investments</option>
                  <option value="Real Estate">Real Estate</option>
                  <option value="Travel & Leisure">Travel & Leisure</option>
                  <option value="Vehicle">Vehicle</option>
                  <option value="General Savings">General Savings</option>
                </select>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowGoalModal(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 text-xs font-bold disabled:opacity-50"
                >
                  {submitting ? 'Creating...' : 'Create Goal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Contribution Modal */}
      {selectedGoal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl bg-[#0D1322] border border-slate-700 shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1">Add Contribution</h3>
            <p className="text-xs text-slate-400 mb-4">
              Allocate capital to <span className="text-teal-400 font-bold">{selectedGoal.name}</span>.
            </p>

            <form onSubmit={handleAddContribution} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Deposit Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={contribAmount}
                  onChange={e => setContribAmount(e.target.value)}
                  placeholder="250.00"
                  required
                  autoFocus
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-sm font-mono-num text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Notes / Origin (Optional)</label>
                <input
                  type="text"
                  value={contribNotes}
                  onChange={e => setContribNotes(e.target.value)}
                  placeholder="e.g. Monthly automated transfer"
                  className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedGoal(null)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-950 text-xs font-bold disabled:opacity-50"
                >
                  {submitting ? 'Depositing...' : 'Confirm Deposit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
