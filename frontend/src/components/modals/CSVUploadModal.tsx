import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertTriangle, AlertCircle, Download } from 'lucide-react';
import { api } from '../../api/client';
import { CSVImportResult } from '../../types';
import { useNotification } from '../../context/NotificationContext';

interface CSVUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const CSVUploadModal: React.FC<CSVUploadModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { notify } = useNotification();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [result, setResult] = useState<CSVImportResult | null>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setResult(null);

    try {
      const res = await api.importCSV(file);
      setResult(res);
      if (res.imported > 0) {
        notify('success', 'Import Successful', `Ingested ${res.imported} new transactions.`);
        onSuccess();
      } else if (res.skipped_duplicates > 0) {
        notify('info', 'No New Records', `Skipped ${res.skipped_duplicates} duplicate transactions.`);
      }
    } catch (err: any) {
      notify('error', 'CSV Import Failed', err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const downloadSampleTemplate = () => {
    const sample = 
      "date,raw_description,amount,transaction_type,category,budget_bucket\n" +
      "2026-09-01,Trader Joe's Manhattan,85.40,Expense,Groceries,Needs\n" +
      "2026-09-02,Starbucks Coffee #0281,6.75,Expense,Food & Dining,Wants\n" +
      "2026-09-03,Uber Trip NYC,28.50,Expense,Transportation,Wants\n" +
      "2026-09-05,TechNova Corp Dir Dep,4800.00,Income,Income,Income\n";
    const blob = new Blob([sample], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'finomaly_sample_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg rounded-2xl bg-[#111827] border border-slate-700/80 shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <UploadCloud className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-white">Import Banking CSV</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Upload Area */}
          <div className="border-2 border-dashed border-slate-700 hover:border-cyan-500/60 rounded-2xl p-6 text-center transition-colors bg-slate-900/40">
            <input
              type="file"
              accept=".csv"
              id="csv-input"
              className="hidden"
              onChange={handleFileChange}
            />
            <label htmlFor="csv-input" className="cursor-pointer flex flex-col items-center">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-3">
                <FileText className="w-6 h-6" />
              </div>
              <span className="text-sm font-semibold text-slate-200">
                {file ? file.name : 'Choose a CSV file or drag and drop'}
              </span>
              <span className="text-xs text-slate-400 mt-1">
                Supports Chase, Amex, Apple Card, or Finomaly standard exports (up to 10MB)
              </span>
            </label>
          </div>

          {/* Sample template button */}
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span>Required: date, description, amount</span>
            <button
              onClick={downloadSampleTemplate}
              className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 hover:underline"
            >
              <Download className="w-3.5 h-3.5" />
              Download Sample Template
            </button>
          </div>

          {/* Results Card */}
          {result && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
              <div className="font-semibold text-slate-200 mb-1">Import Audit Summary:</div>
              <div className="flex items-center gap-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>Successfully imported {result.imported} new records.</span>
              </div>
              {result.skipped_duplicates > 0 && (
                <div className="flex items-center gap-2 text-amber-400">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  <span>Skipped {result.skipped_duplicates} duplicate records (exact date, amount & merchant match).</span>
                </div>
              )}
              {result.errors.length > 0 && (
                <div className="space-y-1 text-rose-400 pt-1 border-t border-slate-800">
                  <div className="flex items-center gap-1.5 font-semibold">
                    <AlertCircle className="w-4 h-4" />
                    <span>Row Validation Warnings ({result.errors.length}):</span>
                  </div>
                  <ul className="list-disc pl-5 space-y-0.5 text-[11px] text-slate-400 max-h-24 overflow-y-auto">
                    {result.errors.map((e, idx) => (
                      <li key={idx}>{e}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/50 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
          <button
            type="button"
            disabled={!file || isUploading}
            onClick={handleUpload}
            className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-cyan-600/30 transition-all flex items-center gap-1.5"
          >
            {isUploading ? 'Parsing & Ingesting...' : 'Upload & Process'}
          </button>
        </div>
      </div>
    </div>
  );
};
