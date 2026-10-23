import React, { useState, useEffect } from 'react';
import { X, Sparkles, Check, DollarSign, Calendar, Tag, Layers, AlignLeft } from 'lucide-react';
import { Transaction, CategorizationSuggestion } from '../../types';
import { api } from '../../api/client';
import { useNotification } from '../../context/NotificationContext';

interface TransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  initialData?: Transaction | null;
}

const CATEGORIES = [
  'Housing',
  'Utilities',
  'Groceries',
  'Food & Dining',
  'Transportation',
  'Entertainment & Subscriptions',
  'Shopping',
  'Health & Medical',
  'Savings & Investments',
  'Income',
  'Other & Miscellaneous'
];

export const TransactionModal: React.FC<TransactionModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialData
}) => {
  const { notify } = useNotification();
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [description, setDescription] = useState<string>('');
  const [merchant, setMerchant] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [type, setType] = useState<'Expense' | 'Income' | 'Transfer'>('Expense');
  const [category, setCategory] = useState<string>('Food & Dining');
  const [subcategory, setSubcategory] = useState<string>('');
  const [budgetBucket, setBudgetBucket] = useState<'Needs' | 'Wants' | 'Savings' | 'Income'>('Wants');
  const [isRecurring, setIsRecurring] = useState<boolean>(false);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Suggestion state
  const [suggestion, setSuggestion] = useState<CategorizationSuggestion | null>(null);

  useEffect(() => {
    if (initialData) {
      setDate(initialData.date);
      setDescription(initialData.raw_description);
      setMerchant(initialData.clean_merchant);
      setAmount(String(initialData.amount));
      setType(initialData.transaction_type);
      setCategory(initialData.category);
      setSubcategory(initialData.subcategory || '');
      setBudgetBucket(initialData.budget_bucket as any);
      setIsRecurring(Boolean(initialData.is_recurring));
      setNotes(initialData.notes || '');
    } else {
      setDate(new Date().toISOString().split('T')[0]);
      setDescription('');
      setMerchant('');
      setAmount('');
      setType('Expense');
      setCategory('Food & Dining');
      setSubcategory('');
      setBudgetBucket('Wants');
      setIsRecurring(false);
      setNotes('');
    }
    setSuggestion(null);
  }, [initialData, isOpen]);

  // Real-time categorization suggestion on description change
  useEffect(() => {
    if (initialData || description.trim().length < 3) {
      setSuggestion(null);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const sug = await api.suggestCategory(description);
        if (sug && sug.suggested_category !== 'Other & Miscellaneous') {
          setSuggestion(sug);
        }
      } catch {
        // ignore suggestion error
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [description, initialData]);

  const applySuggestion = () => {
    if (suggestion) {
      setCategory(suggestion.suggested_category);
      setSubcategory(suggestion.suggested_subcategory);
      setBudgetBucket(suggestion.suggested_budget_bucket as any);
      notify('info', 'Smart Suggestion Applied', `${suggestion.suggested_category} (${Math.round(suggestion.confidence * 100)}% match)`);
      setSuggestion(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const numAmt = parseFloat(amount);
    if (isNaN(numAmt) || numAmt <= 0) {
      notify('error', 'Validation Error', 'Please enter a valid positive transaction amount.');
      return;
    }
    if (!description.trim()) {
      notify('error', 'Validation Error', 'Please provide a transaction description.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (initialData) {
        await api.updateTransaction(initialData.id, {
          date,
          raw_description: description.trim(),
          clean_merchant: merchant.trim() || undefined,
          amount: numAmt,
          transaction_type: type,
          category,
          subcategory,
          budget_bucket: budgetBucket,
          is_recurring: isRecurring,
          notes: notes.trim() || undefined
        });
        notify('success', 'Transaction Updated', `${description} was updated.`);
      } else {
        await api.createTransaction({
          date,
          raw_description: description.trim(),
          clean_merchant: merchant.trim() || undefined,
          amount: numAmt,
          transaction_type: type,
          category,
          subcategory,
          budget_bucket: budgetBucket,
          is_recurring: isRecurring,
          notes: notes.trim() || undefined
        });
        notify('success', 'Transaction Recorded', `${description} of $${numAmt.toFixed(2)} recorded.`);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      notify('error', 'Save Error', err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg rounded-2xl bg-[#111827] border border-slate-700/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
              $
            </div>
            <h2 className="text-lg font-bold text-white">
              {initialData ? 'Edit Transaction' : 'Record New Transaction'}
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4 text-sm">
          {/* Type Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
              Transaction Classification
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['Expense', 'Income', 'Transfer'] as const).map(t => (
                <button
                  type="button"
                  key={t}
                  onClick={() => {
                    setType(t);
                    if (t === 'Income') setBudgetBucket('Income');
                    else if (t === 'Transfer') setBudgetBucket('Savings');
                    else if (budgetBucket === 'Income') setBudgetBucket('Wants');
                  }}
                  className={`py-2 px-3 rounded-xl font-semibold text-xs border transition-all ${
                    type === t
                      ? t === 'Expense'
                        ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-sm'
                        : t === 'Income'
                        ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm'
                        : 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 shadow-sm'
                      : 'bg-slate-800/60 text-slate-400 border-slate-700/60 hover:text-slate-200'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Description & Smart Suggestion */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
              <AlignLeft className="w-3.5 h-3.5" />
              Description / Raw String
            </label>
            <input
              type="text"
              required
              placeholder="e.g. STARBUCKS COFFEE #0281 NYC"
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
            />

            {/* Smart Suggestion Pill */}
            {suggestion && (
              <div className="mt-2 p-2.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300 animate-slide-in">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>
                    Suggested: <strong className="text-white">{suggestion.suggested_category}</strong> ({suggestion.suggested_budget_bucket})
                  </span>
                </div>
                <button
                  type="button"
                  onClick={applySuggestion}
                  className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 font-semibold border border-emerald-500/40 transition-colors flex items-center gap-1"
                >
                  <Check className="w-3 h-3" />
                  Apply
                </button>
              </div>
            )}
          </div>

          {/* Amount & Date in 2 columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5" />
                Amount ($)
              </label>
              <input
                type="number"
                step="0.01"
                required
                placeholder="0.00"
                value={amount}
                onChange={e => setAmount(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono-num font-semibold placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                Transaction Date
              </label>
              <input
                type="date"
                required
                value={date}
                onChange={e => setDate(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Category & Budget Bucket */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Tag className="w-3.5 h-3.5" />
                Primary Category
              </label>
              <select
                value={category}
                onChange={e => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              >
                {CATEGORIES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                50/30/20 Bucket
              </label>
              <select
                value={budgetBucket}
                onChange={e => setBudgetBucket(e.target.value as any)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              >
                <option value="Needs">Needs (≤ 50% Essential)</option>
                <option value="Wants">Wants (≤ 30% Lifestyle)</option>
                <option value="Savings">Savings (≥ 20% Allocation)</option>
                <option value="Income">Income (Revenue Feed)</option>
              </select>
            </div>
          </div>

          {/* Clean Merchant & Subcategory */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Normalized Merchant (Optional)
              </label>
              <input
                type="text"
                placeholder="Auto-derived if left empty"
                value={merchant}
                onChange={e => setMerchant(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Subcategory (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Coffee Shops"
                value={subcategory}
                onChange={e => setSubcategory(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Recurring Checkbox */}
          <div className="flex items-center gap-2 pt-1">
            <input
              type="checkbox"
              id="is_recurring_cb"
              checked={isRecurring}
              onChange={e => setIsRecurring(e.target.checked)}
              className="w-4 h-4 rounded text-emerald-500 bg-slate-900 border-slate-700 focus:ring-emerald-500"
            />
            <label htmlFor="is_recurring_cb" className="text-xs text-slate-300 font-medium cursor-pointer">
              Mark as periodic recurring subscription / bill
            </label>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">
              Analytical Notes (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Team dinner celebration"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-md shadow-emerald-600/30 transition-all flex items-center gap-1.5"
            >
              {isSubmitting ? 'Saving...' : initialData ? 'Save Changes' : 'Confirm Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
