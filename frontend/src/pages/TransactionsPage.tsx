import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Plus,
  UploadCloud,
  Download,
  Trash2,
  Edit2,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  RefreshCw,
  Tag
} from 'lucide-react';
import { Transaction } from '../types';
import { api } from '../api/client';
import { useNotification } from '../context/NotificationContext';

interface TransactionsPageProps {
  onOpenAddModal: () => void;
  onOpenImportModal: () => void;
  onEditTransaction: (tx: Transaction) => void;
}

export const TransactionsPage: React.FC<TransactionsPageProps> = ({
  onOpenAddModal,
  onOpenImportModal,
  onEditTransaction
}) => {
  const { notify } = useNotification();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);
  const [search, setSearch] = useState<string>('');
  const [category, setCategory] = useState<string>('All');
  const [txType, setTxType] = useState<string>('All');
  const [budgetBucket, setBudgetBucket] = useState<string>('All');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      const res = await api.listTransactions({
        page,
        page_size: pageSize,
        search: search.trim() || undefined,
        category: category !== 'All' ? category : undefined,
        transaction_type: txType !== 'All' ? txType : undefined,
        budget_bucket: budgetBucket !== 'All' ? budgetBucket : undefined
      });
      setTransactions(res.transactions);
      setTotal(res.total);
    } catch (err: any) {
      notify('error', 'Failed to Load Transactions', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, pageSize, category, txType, budgetBucket]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1);
      fetchTransactions();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleDelete = async (id: number, merchant: string) => {
    if (!window.confirm(`Are you sure you want to delete transaction "${merchant}"?`)) return;
    try {
      await api.deleteTransaction(id);
      notify('success', 'Transaction Deleted', `Deleted transaction #${id}`);
      fetchTransactions();
    } catch (err: any) {
      notify('error', 'Delete Failed', err.message);
    }
  };

  const handleExportCSV = () => {
    const exportUrl = api.getExportCSVUrl({
      category: category !== 'All' ? category : undefined,
      transaction_type: txType !== 'All' ? txType : undefined
    });
    window.open(exportUrl, '_blank');
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      {/* Header Controls Bar */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 p-5 rounded-2xl bg-[#111827] border border-slate-800 shadow-xl">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search merchant, description, category..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
          <button
            onClick={onOpenImportModal}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
          >
            <UploadCloud className="w-4 h-4 text-cyan-400" />
            Import CSV
          </button>

          <button
            onClick={handleExportCSV}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-colors"
          >
            <Download className="w-4 h-4 text-emerald-400" />
            Export CSV
          </button>

          <button
            onClick={onOpenAddModal}
            className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 shadow-lg shadow-emerald-600/20 transition-all"
          >
            <Plus className="w-4 h-4" />
            Add Entry
          </button>
        </div>
      </div>

      {/* Filter Chips Bar */}
      <div className="flex flex-wrap items-center gap-3 p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
        <span className="font-semibold text-slate-400 flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5 text-cyan-400" /> Filters:
        </span>

        {/* Type Filter */}
        <select
          value={txType}
          onChange={e => { setTxType(e.target.value); setPage(1); }}
          className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
        >
          <option value="All">All Types</option>
          <option value="Expense">Expense Only</option>
          <option value="Income">Income Only</option>
          <option value="Transfer">Transfer Only</option>
        </select>

        {/* Category Filter */}
        <select
          value={category}
          onChange={e => { setCategory(e.target.value); setPage(1); }}
          className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
        >
          <option value="All">All Categories</option>
          <option value="Housing">Housing</option>
          <option value="Utilities">Utilities</option>
          <option value="Groceries">Groceries</option>
          <option value="Food & Dining">Food & Dining</option>
          <option value="Transportation">Transportation</option>
          <option value="Entertainment & Subscriptions">Entertainment</option>
          <option value="Shopping">Shopping</option>
          <option value="Health & Medical">Health & Medical</option>
          <option value="Income">Income</option>
        </select>

        {/* 50/30/20 Bucket Filter */}
        <select
          value={budgetBucket}
          onChange={e => { setBudgetBucket(e.target.value); setPage(1); }}
          className="px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-emerald-500"
        >
          <option value="All">All Buckets</option>
          <option value="Needs">Needs (≤ 50%)</option>
          <option value="Wants">Wants (≤ 30%)</option>
          <option value="Savings">Savings (≥ 20%)</option>
        </select>

        <span className="ml-auto text-slate-500 text-xs">
          Showing {transactions.length} of {total.toLocaleString()} transactions
        </span>
      </div>

      {/* Transactions Table Card */}
      <div className="rounded-2xl bg-[#111827] border border-slate-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[11px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Merchant & Description</th>
                <th className="py-3 px-4">Category & Bucket</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4 text-right">Amount</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-200">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-emerald-400" />
                    Loading transactions...
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No transactions match the selected filters.
                  </td>
                </tr>
              ) : (
                transactions.map(tx => (
                  <tr key={tx.id} className="hover:bg-slate-850/50 transition-colors">
                    {/* Date */}
                    <td className="py-3 px-4 whitespace-nowrap text-slate-400 font-mono-num">
                      {tx.date}
                    </td>

                    {/* Merchant & Raw Description */}
                    <td className="py-3 px-4">
                      <div className="font-semibold text-white">{tx.clean_merchant}</div>
                      <div className="text-[11px] text-slate-400 truncate max-w-xs">
                        {tx.raw_description}
                      </div>
                    </td>

                    {/* Category & Bucket */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <Tag className="w-3 h-3 text-emerald-400" />
                        <span className="font-medium text-slate-200">{tx.category}</span>
                      </div>
                      <span className="text-[10px] text-slate-400 block mt-0.5">
                        Bucket: {tx.budget_bucket}
                      </span>
                    </td>

                    {/* Type Badge */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          tx.transaction_type === 'Income'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : tx.transaction_type === 'Transfer'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {tx.transaction_type}
                      </span>
                    </td>

                    {/* Amount */}
                    <td
                      className={`py-3 px-4 text-right font-bold font-mono-num whitespace-nowrap ${
                        tx.transaction_type === 'Income' ? 'text-emerald-400' : 'text-slate-100'
                      }`}
                    >
                      {tx.transaction_type === 'Income' ? '+' : '-'}${tx.amount.toFixed(2)}
                    </td>

                    {/* Actions */}
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => onEditTransaction(tx)}
                          title="Edit transaction"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(tx.id, tx.clean_merchant)}
                          title="Delete transaction"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-900/60 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span>Rows per page:</span>
            <select
              value={pageSize}
              onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 text-white focus:outline-none"
            >
              <option value={15}>15</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span>
              Page {page} of {totalPages}
            </span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 text-slate-200 font-semibold font-mono-num">{page}</span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
