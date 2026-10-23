import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Sliders,
  AlertCircle,
  CheckCircle2,
  Calendar,
  DollarSign,
  ShieldAlert,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine
} from 'recharts';
import { api } from '../api/client';
import { ForecastSummary } from '../types';
import { useNotification } from '../context/NotificationContext';

export const ForecastingPage: React.FC = () => {
  const { notify } = useNotification();
  const [horizon, setHorizon] = useState<number>(6);
  const [forecast, setForecast] = useState<ForecastSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchForecast = async () => {
    setIsLoading(true);
    try {
      const data = await api.getForecast(horizon);
      setForecast(data);
    } catch (err: any) {
      notify('error', 'Forecasting Error', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, [horizon]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            Holt's Linear Trend Expense Forecasting Model
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Double Exponential Smoothing (level + trend) with 95% empirical confidence intervals for cash runway risk detection.
          </p>
        </div>

        {/* Horizon Selector */}
        <div className="flex items-center gap-2 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          <span className="text-xs text-slate-400 px-2 font-medium flex items-center gap-1">
            <Sliders className="w-3.5 h-3.5" /> Horizon:
          </span>
          {[3, 6, 9, 12].map(h => (
            <button
              key={h}
              onClick={() => setHorizon(h)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                horizon === h
                  ? 'bg-cyan-500 text-slate-950 shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {h}M
            </button>
          ))}
        </div>
      </div>

      {/* KPI Highlight Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Current Month-to-Date
          </span>
          <div className="text-2xl font-extrabold text-white font-mono-num">
            ${forecast ? forecast.current_month_to_date.toFixed(2) : '0.00'}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Active Incurred Expenses</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Projected End-of-Month
          </span>
          <div className="text-2xl font-extrabold text-cyan-400 font-mono-num">
            ${forecast ? forecast.projected_end_of_month.toFixed(2) : '0.00'}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Holt's Estimated EOM Closure</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Monthly Target Limit
          </span>
          <div className="text-2xl font-extrabold text-white font-mono-num">
            ${forecast ? forecast.current_monthly_budget.toFixed(2) : '0.00'}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Configured Budget Baseline</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Trajectory Status
          </span>
          <div className="flex items-center gap-2 mt-1">
            {forecast && forecast.status === 'ON_TRACK' ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                <CheckCircle2 className="w-3.5 h-3.5" />
                ON TRACK
              </span>
            ) : forecast && forecast.status === 'AT_RISK' ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30">
                <AlertCircle className="w-3.5 h-3.5" />
                AT RISK
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-300 border border-rose-500/30">
                <ShieldAlert className="w-3.5 h-3.5" />
                OVER BUDGET
              </span>
            )}
          </div>
          <span className="text-[11px] text-slate-500 mt-2 block">
            Variance: ${forecast ? Math.abs(forecast.budget_variance).toFixed(2) : '0.00'}
          </span>
        </div>
      </div>

      {/* Projection Chart Container */}
      <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
          <div>
            <h3 className="text-base font-bold text-white">Historical Actuals vs Forward Spending Runway</h3>
            <p className="text-xs text-slate-400">
              Shaded cyan corridor depicts upper and lower 95% confidence variance bounds.
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-emerald-400" /> Historical Actuals
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-cyan-400 border-dashed" /> Forecast
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-2 bg-cyan-500/20 rounded" /> 95% Confidence
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className="h-80 flex justify-center items-center text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mr-3" />
            Computing double exponential smoothing projection...
          </div>
        ) : !forecast || !forecast.forward_projections.length ? (
          <div className="h-80 flex justify-center items-center text-slate-400 text-sm">
            Insufficient historical transactions to establish statistical trend slope.
          </div>
        ) : (
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={forecast.forward_projections} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="forecastArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="actualArea" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="period" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#64748B"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={val => `$${val}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0F172A',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    color: '#F8FAFC'
                  }}
                  formatter={(value: any) => [`$${Number(value).toFixed(2)}`, '']}
                />
                <Area
                  type="monotone"
                  dataKey="actual_spend"
                  stroke="#10B981"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#actualArea)"
                  name="Historical Actual ($)"
                />
                <Area
                  type="monotone"
                  dataKey="forecast_spend"
                  stroke="#06B6D4"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  fillOpacity={1}
                  fill="url(#forecastArea)"
                  name="Projected Spend ($)"
                />
                <Area
                  type="monotone"
                  dataKey="upper_bound"
                  stroke="#38BDF8"
                  strokeWidth={1}
                  strokeOpacity={0.4}
                  fill="none"
                  name="95% Upper Bound"
                />
                <Area
                  type="monotone"
                  dataKey="lower_bound"
                  stroke="#38BDF8"
                  strokeWidth={1}
                  strokeOpacity={0.4}
                  fill="none"
                  name="95% Lower Bound"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}

        {forecast && forecast.limitations_note && (
          <div className="mt-4 p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex items-start gap-2.5 text-xs text-slate-400">
            <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <span>{forecast.limitations_note}</span>
          </div>
        )}
      </div>
    </div>
  );
};
