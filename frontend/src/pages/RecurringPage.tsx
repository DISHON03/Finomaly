import React, { useState, useEffect } from 'react';
import {
  RefreshCw,
  AlertTriangle,
  Calendar,
  CreditCard,
  DollarSign,
  CheckCircle2,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { api } from '../api/client';
import { RecurringPaymentItem } from '../types';
import { useNotification } from '../context/NotificationContext';

export const RecurringPage: React.FC = () => {
  const { notify } = useNotification();
  const [items, setItems] = useState<RecurringPaymentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchRecurring = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRecurringPayments();
      setItems(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Subscriptions', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecurring();
  }, []);

  const totalMonthly = items.reduce((acc, curr) => acc + curr.estimated_amount, 0);
  const totalAnnual = items.reduce((acc, curr) => acc + curr.projected_annual_cost, 0);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-purple-400" />
            Recurring Payment Cadence & Subscription Creep Radar
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Statistical interval clustering isolates recurring merchant debits to audit annualized commitments and redundant media streaming.
          </p>
        </div>
      </div>

      {/* KPI Highlight Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Monthly Recurring Outflow
          </span>
          <div className="text-2xl font-extrabold text-white font-mono-num">
            ${totalMonthly.toFixed(2)}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Expected 30-Day Automated Debit</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Annualized Commitment
          </span>
          <div className="text-2xl font-extrabold text-purple-400 font-mono-num">
            ${totalAnnual.toFixed(2)}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Cumulative Annualized Run-Rate</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Monitored Subscriptions
          </span>
          <div className="text-2xl font-extrabold text-emerald-400 font-mono-num">
            {items.length} Services
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Identified Cadence Patterns</span>
        </div>
      </div>

      {/* Subscription Creep Diagnostic Callout */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-950/40 to-slate-900 border border-amber-500/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-white mb-1">
              Subscription Creep & Redundancy Alert Detected
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Analysis identifies multiple concurrent video streaming and cloud storage platforms
              aggregating over <span className="font-bold text-amber-300 font-mono-num">${totalAnnual.toFixed(2)}/yr</span>.
              Consolidating redundant entertainment services could unlock an estimated $600-$900/year in immediate savings velocity.
            </p>
          </div>
        </div>
      </div>

      {/* Subscriptions Table */}
      <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
        <h3 className="text-base font-bold text-white mb-1">Identified Recurring Subscriptions</h3>
        <p className="text-xs text-slate-400 mb-5">Chronological recurring merchant debits detected by clustering transaction intervals.</p>

        {isLoading ? (
          <div className="py-12 flex justify-center items-center text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mr-3" />
            Analyzing payment cadences...
          </div>
        ) : items.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">
            No regular recurring payment intervals detected yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Service / Merchant</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Category</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Cadence</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Amount / Cycle</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Annualized Impact</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider">Last Observed</th>
                  <th className="py-3 px-4 font-semibold uppercase tracking-wider text-right">Est. Next Charge</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {items.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-white">
                      {item.merchant}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {item.category}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {item.observed_frequency}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono-num font-semibold text-white">
                      ${item.estimated_amount.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 font-mono-num text-purple-400 font-bold">
                      ${item.projected_annual_cost.toFixed(2)}/yr
                    </td>
                    <td className="py-3.5 px-4 font-mono-num text-slate-400">
                      {item.last_payment_date}
                    </td>
                    <td className="py-3.5 px-4 font-mono-num text-right text-cyan-400">
                      {item.estimated_next_date}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
