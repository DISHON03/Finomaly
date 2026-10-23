import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Search,
  Plus,
  Trash2,
  Tag,
  CheckCircle2,
  Sliders,
  ArrowRight
} from 'lucide-react';
import { api } from '../api/client';
import { CategoryRule, CategorizationSuggestion } from '../types';
import { useNotification } from '../context/NotificationContext';

export const CategorizationPage: React.FC = () => {
  const { notify } = useNotification();
  const [rules, setRules] = useState<CategoryRule[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Suggestion tester
  const [testString, setTestString] = useState<string>('WHOLEFDS SFO 4093');
  const [suggestion, setSuggestion] = useState<CategorizationSuggestion | null>(null);
  const [isTesting, setIsTesting] = useState<boolean>(false);

  // New Rule Form
  const [keywordPattern, setKeywordPattern] = useState<string>('');
  const [ruleCategory, setRuleCategory] = useState<string>('Groceries');
  const [ruleBucket, setRuleBucket] = useState<'Needs' | 'Wants' | 'Savings'>('Needs');
  const [submitting, setSubmitting] = useState<boolean>(false);

  const fetchRules = async () => {
    setIsLoading(true);
    try {
      const data = await api.getCategoryRules();
      setRules(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Rules', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRules();
    handleTestSuggest('WHOLEFDS SFO 4093');
  }, []);

  const handleTestSuggest = async (desc: string) => {
    if (!desc.trim()) return;
    setIsTesting(true);
    try {
      const res = await api.suggestCategory(desc);
      setSuggestion(res);
    } catch (err: any) {
      notify('error', 'Test Failed', err.message);
    } finally {
      setIsTesting(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keywordPattern.trim()) {
      notify('warning', 'Pattern Required', 'Please enter a keyword or regex pattern.');
      return;
    }
    setSubmitting(true);
    try {
      const created = await api.createCategoryRule({
        keyword_pattern: keywordPattern.trim(),
        category: ruleCategory,
        budget_bucket: ruleBucket
      });
      notify('success', 'Rule Created', `Rule for "${keywordPattern}" saved successfully.`);
      setKeywordPattern('');
      fetchRules();
    } catch (err: any) {
      notify('error', 'Creation Failed', err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteRule = async (id: number) => {
    try {
      await api.deleteCategoryRule(id);
      notify('info', 'Rule Removed', 'Keyword categorization rule deleted.');
      setRules(prev => prev.filter(r => r.id !== id));
    } catch (err: any) {
      notify('error', 'Delete Failed', err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            Smart Merchant Normalization & Taxonomy Memory
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Heuristic pattern matching and deterministic correction memory that standardizes messy bank feed descriptions.
          </p>
        </div>
      </div>

      {/* Interactive Suggestion Tester Card */}
      <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
        <h3 className="text-base font-bold text-white mb-1">Live Merchant Categorization Sandbox</h3>
        <p className="text-xs text-slate-400 mb-4">
          Test raw merchant strings against the Finomaly normalization engine to observe matched taxonomy and confidence scores.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={testString}
              onChange={e => setTestString(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleTestSuggest(testString)}
              placeholder="e.g. UBER *TRIP 2026-10 SAN FRANCISCO, NETFLIX.COM"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>
          <button
            onClick={() => handleTestSuggest(testString)}
            disabled={isTesting}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs flex items-center justify-center gap-1.5 shadow-md shadow-emerald-500/20 disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Test Inference</span>
          </button>
        </div>

        {/* Suggestion Output */}
        {suggestion && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950/80 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Inferred Category</span>
              <span className="text-sm font-bold text-white">{suggestion.suggested_category}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">50/30/20 Bucket</span>
              <span className="text-xs font-semibold text-emerald-400">{suggestion.suggested_budget_bucket}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Confidence Score</span>
              <span className="text-xs font-mono-num font-bold text-cyan-400">
                {(suggestion.confidence * 100).toFixed(0)}%
              </span>
            </div>
            {suggestion.matched_rule && (
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Active Match Pattern</span>
                <span className="text-xs font-mono-num text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                  {suggestion.matched_rule}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Rules Manager */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Rule Form */}
        <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <h3 className="text-base font-bold text-white mb-1">Create Classification Rule</h3>
          <p className="text-xs text-slate-400 mb-4">Override automated ML with custom keyword matching.</p>

          <form onSubmit={handleCreateRule} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Keyword / Pattern</label>
              <input
                type="text"
                value={keywordPattern}
                onChange={e => setKeywordPattern(e.target.value)}
                placeholder="e.g. TRADER JOE, SPOTIFY"
                required
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Target Category</label>
              <select
                value={ruleCategory}
                onChange={e => setRuleCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
              >
                <option value="Groceries">Groceries</option>
                <option value="Food & Dining">Food & Dining</option>
                <option value="Housing">Housing</option>
                <option value="Utilities">Utilities</option>
                <option value="Transportation">Transportation</option>
                <option value="Entertainment & Subscriptions">Entertainment & Subscriptions</option>
                <option value="Shopping">Shopping</option>
                <option value="Health & Medical">Health & Medical</option>
                <option value="Savings & Investments">Savings & Investments</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">50/30/20 Bucket</label>
              <div className="grid grid-cols-3 gap-2">
                {(['Needs', 'Wants', 'Savings'] as const).map(b => (
                  <button
                    key={b}
                    type="button"
                    onClick={() => setRuleBucket(b)}
                    className={`py-1.5 text-xs font-bold rounded-lg border transition-all ${
                      ruleBucket === b
                        ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                        : 'bg-slate-900 border-slate-700 text-slate-400'
                    }`}
                  >
                    {b}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 disabled:opacity-50"
            >
              {submitting ? 'Saving...' : 'Add Rule'}
            </button>
          </form>
        </div>

        {/* Rules Table */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-white">Active Learned Rules</h3>
            <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-lg">
              {rules.length} Rules Active
            </span>
          </div>

          {isLoading ? (
            <div className="py-12 flex justify-center items-center text-slate-400 text-xs">
              Loading rules...
            </div>
          ) : rules.length === 0 ? (
            <div className="py-12 text-center text-slate-400 text-xs">
              No custom categorization rules added yet.
            </div>
          ) : (
            <div className="overflow-x-auto max-h-[360px]">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900 text-slate-400 border-b border-slate-800 sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3 font-semibold">Pattern</th>
                    <th className="py-2.5 px-3 font-semibold">Category</th>
                    <th className="py-2.5 px-3 font-semibold">Bucket</th>
                    <th className="py-2.5 px-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {rules.map(rule => (
                    <tr key={rule.id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 font-mono-num text-white font-semibold">
                        {rule.keyword_pattern}
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {rule.category}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300">
                          {rule.budget_bucket}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="text-slate-500 hover:text-rose-400 p-1"
                          title="Delete Rule"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
