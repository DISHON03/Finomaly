import React, { useState, useEffect } from 'react';
import {
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Sparkles,
  Info,
  ArrowRight,
  ShieldCheck,
  Flame
} from 'lucide-react';
import { api } from '../api/client';
import { FinancialInsightItem } from '../types';
import { useNotification } from '../context/NotificationContext';

export const InsightsPage: React.FC = () => {
  const { notify } = useNotification();
  const [insights, setInsights] = useState<FinancialInsightItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchInsights = async () => {
    setIsLoading(true);
    try {
      const data = await api.getFinancialInsights();
      setInsights(data);
    } catch (err: any) {
      notify('error', 'Insights Failed', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-amber-400" />
            Empirically Verified Financial Insights & Behavior Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Strictly computed from historical ledger transactions using statistical distribution checks, weekend surges, and budget compliance ratios.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Zero Hallucination Guarantee</span>
        </div>
      </div>

      {/* Insights Cards List */}
      {isLoading ? (
        <div className="py-16 flex justify-center items-center text-slate-400 text-sm">
          <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mr-3" />
          Computing financial observations from transaction history...
        </div>
      ) : insights.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-slate-800">
          <Info className="w-12 h-12 text-slate-500 mx-auto mb-3" />
          <h4 className="text-base font-bold text-white mb-1">No Insights Generated Yet</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Record more transactions or load demo transactions to unlock deep behavioral insights.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((item, idx) => {
            const isWarning = item.type === 'warning';
            const isPositive = item.type === 'positive';
            const isTip = item.type === 'tip';

            return (
              <div
                key={item.id || idx}
                className={`p-6 rounded-2xl bg-[#111827] border shadow-xl flex flex-col justify-between transition-all ${
                  isWarning
                    ? 'border-amber-500/40 hover:border-amber-500'
                    : isPositive
                    ? 'border-emerald-500/40 hover:border-emerald-500'
                    : isTip
                    ? 'border-cyan-500/40 hover:border-cyan-500'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        isWarning
                          ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                          : isPositive
                          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                          : isTip
                          ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                          : 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {item.type} observation
                    </span>

                    {item.category && (
                      <span className="text-[11px] font-semibold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                        {item.category}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
                    {isWarning && <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />}
                    {isPositive && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                    {isTip && <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />}
                    {item.title}
                  </h3>

                  <p className="text-xs text-slate-300 leading-relaxed mb-4">
                    {item.observation}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">Key Observation Metric</span>
                  <span className="px-3 py-1 rounded-xl bg-slate-950 font-mono-num text-xs font-bold text-white border border-slate-800">
                    {item.metric_highlight}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
