import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Filter,
  RefreshCw,
  Info,
  Calendar,
  DollarSign
} from 'lucide-react';
import { api } from '../api/client';
import { AnomalyAlert } from '../types';
import { useNotification } from '../context/NotificationContext';

export const AnomaliesPage: React.FC = () => {
  const { notify } = useNotification();
  const [alerts, setAlerts] = useState<AnomalyAlert[]>([]);
  const [statusFilter, setStatusFilter] = useState<'active' | 'reviewed' | 'dismissed'>('active');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isScanning, setIsScanning] = useState<boolean>(false);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAnomalies(statusFilter);
      setAlerts(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Alerts', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [statusFilter]);

  const handleScanNow = async () => {
    setIsScanning(true);
    try {
      const res = await api.scanAnomalies();
      notify(
        'success',
        'Anomaly Scan Complete',
        `Evaluated ${res.scanned_transactions} transactions with ${res.method_used}. Found ${res.new_anomalies_detected} anomalies.`
      );
      fetchAlerts();
    } catch (err: any) {
      notify('error', 'Scan Failed', err.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleUpdateStatus = async (id: number, newStatus: 'reviewed' | 'dismissed') => {
    try {
      await api.updateAnomalyStatus(id, newStatus);
      notify('info', 'Status Updated', `Alert #${id} marked as ${newStatus}.`);
      setAlerts(prev => prev.filter(a => a.id !== id));
    } catch (err: any) {
      notify('error', 'Update Failed', err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            Machine Learning Spending Anomaly Detector
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Statistical IQR baseline filtering and Isolation Forest clustering to detect anomalous charges, merchant price spikes, and subscription creep.
          </p>
        </div>

        <button
          onClick={handleScanNow}
          disabled={isScanning}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-rose-500 to-amber-500 hover:from-rose-400 hover:to-amber-400 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-rose-500/20 transition-all self-stretch sm:self-auto justify-center disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
          <span>{isScanning ? 'Running ML Scan...' : 'Trigger Full Audit Scan'}</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between">
        <div className="flex rounded-xl bg-slate-900 p-1 border border-slate-800">
          {(['active', 'reviewed', 'dismissed'] as const).map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg capitalize transition-all ${
                statusFilter === s
                  ? 'bg-slate-800 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {s} ({alerts.filter(a => a.status === s).length || (statusFilter === s ? alerts.length : 0)})
            </button>
          ))}
        </div>

        <div className="text-xs text-slate-400 hidden sm:flex items-center gap-2">
          <Info className="w-3.5 h-3.5 text-cyan-400" />
          <span>IQR Multiplier: 1.5x Q3 + 3.0x Outlier Isolation</span>
        </div>
      </div>

      {/* Anomaly Alerts Grid */}
      {isLoading ? (
        <div className="py-16 flex justify-center items-center text-slate-400 text-sm">
          <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin mr-3" />
          Loading audit alerts...
        </div>
      ) : alerts.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#111827] border border-slate-800">
          <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3 opacity-80" />
          <h4 className="text-base font-bold text-white mb-1">No {statusFilter} Anomalies Found</h4>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            All transaction charges within this filter window fall within expected standard deviation baselines.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {alerts.map(alert => {
            const isHigh = alert.severity === 'HIGH';
            const isMed = alert.severity === 'MEDIUM';

            return (
              <div
                key={alert.id}
                className={`p-5 rounded-2xl bg-[#111827] border shadow-xl flex flex-col justify-between transition-all ${
                  isHigh
                    ? 'border-rose-500/40 hover:border-rose-500'
                    : isMed
                    ? 'border-amber-500/40 hover:border-amber-500'
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        isHigh
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          : isMed
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'bg-slate-700 text-slate-300'
                      }`}
                    >
                      {alert.severity} SEVERITY
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono-num">
                      {alert.created_at ? alert.created_at.slice(0, 10) : ''}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-white mb-1.5 flex items-center gap-2">
                    <AlertTriangle
                      className={`w-4 h-4 shrink-0 ${
                        isHigh ? 'text-rose-400' : isMed ? 'text-amber-400' : 'text-slate-400'
                      }`}
                    />
                    {alert.title}
                  </h4>

                  <p className="text-xs text-slate-300 leading-relaxed mb-4">
                    {alert.explanation}
                  </p>

                  {/* Transaction metadata pill if available */}
                  {alert.transaction_merchant && (
                    <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs space-y-1 mb-4">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Merchant:</span>
                        <span className="font-semibold text-white">{alert.transaction_merchant}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Recorded Charge:</span>
                        <span className="font-mono-num font-bold text-rose-400">
                          ${alert.transaction_amount?.toFixed(2)}
                        </span>
                      </div>
                      {alert.comparison_metric && (
                        <div className="flex justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-900">
                          <span>Comparison:</span>
                          <span className="text-slate-300">{alert.comparison_metric}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                {statusFilter === 'active' && (
                  <div className="flex gap-2 pt-2 border-t border-slate-800/80">
                    <button
                      onClick={() => handleUpdateStatus(alert.id, 'reviewed')}
                      className="flex-1 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-semibold border border-emerald-500/20 transition-colors flex items-center justify-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Mark Reviewed
                    </button>
                    <button
                      onClick={() => handleUpdateStatus(alert.id, 'dismissed')}
                      className="flex-1 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Dismiss
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
