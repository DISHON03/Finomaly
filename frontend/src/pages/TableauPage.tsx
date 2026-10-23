import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  Download,
  ExternalLink,
  Layers,
  FileSpreadsheet,
  CheckCircle2,
  Code,
  BookOpen
} from 'lucide-react';
import { api } from '../api/client';
import { TableauDataset } from '../types';
import { useNotification } from '../context/NotificationContext';

export const TableauPage: React.FC = () => {
  const { notify } = useNotification();
  const [datasets, setDatasets] = useState<TableauDataset[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchDatasets = async () => {
    setIsLoading(true);
    try {
      const data = await api.getTableauDatasets();
      setDatasets(data);
    } catch (err: any) {
      notify('error', 'Failed to Load Datasets', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleDownload = (datasetId: string, filename: string) => {
    const url = api.getTableauExportUrl(datasetId);
    window.open(url, '_blank');
    notify('success', 'Export Initiated', `Downloading ${filename} for Tableau.`);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
            Tableau Business Intelligence & Semantic Analytics Layer
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Curated dimensional tables, pre-aggregated analytical views, and optimized extracts ready for Tableau Desktop and Tableau Public.
          </p>
        </div>
      </div>

      {/* Datasets Grid */}
      <div>
        <h3 className="text-base font-bold text-white mb-3">Pre-Aggregated BI Exports & Star-Schema Datasets</h3>
        {isLoading ? (
          <div className="py-12 flex justify-center items-center text-slate-400 text-sm">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
            Querying warehouse extracts...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {datasets.map(ds => (
              <div
                key={ds.id}
                className="p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl flex flex-col justify-between hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
                      <FileSpreadsheet className="w-3 h-3" />
                      {ds.filename}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono-num">{ds.record_grain}</span>
                  </div>

                  <h4 className="text-base font-bold text-white mb-1.5">{ds.name}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed mb-4">{ds.description}</p>

                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-400 mb-4">
                    <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                      Recommended Tableau Visualizations
                    </span>
                    <span>{ds.recommended_visuals}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleDownload(ds.id, ds.filename)}
                  className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-md shadow-indigo-500/20 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download {ds.filename}</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tableau Blueprint & Calculated Fields Guide */}
      <div className="p-6 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl space-y-4">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          Tableau Calculated Field Formulas & Recipe Guide
        </h3>
        <p className="text-xs text-slate-400">
          Paste these verified Tableau calculation formulas directly into your Tableau Desktop data source:
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[11px] font-sans font-bold text-emerald-400 block mb-1">
              50/30/20 Compliance Status
            </span>
            <code className="text-slate-300 text-[11px] block whitespace-pre-wrap leading-relaxed">
{`IF [Budget Bucket] = 'Needs' AND [Spend Pct] <= 0.50 THEN 'Compliant'
ELSEIF [Budget Bucket] = 'Wants' AND [Spend Pct] <= 0.30 THEN 'Compliant'
ELSEIF [Budget Bucket] = 'Savings' AND [Spend Pct] >= 0.20 THEN 'Optimal'
ELSE 'Over Budget'
END`}
            </code>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
            <span className="text-[11px] font-sans font-bold text-cyan-400 block mb-1">
              Weekend Spending Multiplier
            </span>
            <code className="text-slate-300 text-[11px] block whitespace-pre-wrap leading-relaxed">
{`IF [Is Weekend] = 1 
THEN [Amount] / WINDOW_AVG(SUM(IF [Is Weekend] = 0 THEN [Amount] END))
ELSE 1.0
END`}
            </code>
          </div>
        </div>
      </div>
    </div>
  );
};
