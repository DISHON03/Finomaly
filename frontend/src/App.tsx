import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { NotificationProvider } from './context/NotificationContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar, PageId } from './components/layout/Sidebar';
import { Navbar } from './components/layout/Navbar';

// Pages
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { TransactionsPage } from './pages/TransactionsPage';
import { BudgetsPage } from './pages/BudgetsPage';
import { AnomaliesPage } from './pages/AnomaliesPage';
import { ForecastingPage } from './pages/ForecastingPage';
import { RecurringPage } from './pages/RecurringPage';
import { InsightsPage } from './pages/InsightsPage';
import { SavingsPage } from './pages/SavingsPage';
import { CategorizationPage } from './pages/CategorizationPage';
import { TableauPage } from './pages/TableauPage';

// Modals
import { TransactionModal } from './components/modals/TransactionModal';
import { CSVUploadModal } from './components/modals/CSVUploadModal';
import { Transaction } from './types';
import { api } from './api/client';
import { Sparkles, Terminal } from 'lucide-react';

const MainLayout: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  // Modals state
  const [txModalOpen, setTxModalOpen] = useState<boolean>(false);
  const [editingTx, setEditingTx] = useState<Transaction | null>(null);
  const [csvModalOpen, setCsvModalOpen] = useState<boolean>(false);

  // Active anomaly alerts count for sidebar badge
  const [activeAnomaliesCount, setActiveAnomaliesCount] = useState<number>(0);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const refreshAll = () => {
    setRefreshKey(prev => prev + 1);
  };

  useEffect(() => {
    if (isAuthenticated) {
      api.getAnomalies('active')
        .then(res => setActiveAnomaliesCount(res.length))
        .catch(() => {});
    }
  }, [isAuthenticated, refreshKey]);

  if (isLoading) {
    return (
      <div className="min-h-screen w-full bg-[#070B14] flex flex-col items-center justify-center text-white">
        <div className="relative mb-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-3xl font-black shadow-xl shadow-emerald-500/25">
            F
          </div>
          <div className="absolute inset-0 rounded-2xl border-2 border-emerald-400/50 animate-ping pointer-events-none" />
        </div>
        <p className="text-sm font-semibold tracking-wide text-slate-300">
          Initializing Finomaly Intelligence...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <DashboardPage
            key={refreshKey}
            onNavigate={setActivePage}
            onOpenAddModal={() => {
              setEditingTx(null);
              setTxModalOpen(true);
            }}
          />
        );
      case 'transactions':
        return (
          <TransactionsPage
            key={refreshKey}
            onOpenAddModal={() => {
              setEditingTx(null);
              setTxModalOpen(true);
            }}
            onOpenImportModal={() => setCsvModalOpen(true)}
            onEditTransaction={tx => {
              setEditingTx(tx);
              setTxModalOpen(true);
            }}
          />
        );
      case 'budgets':
        return <BudgetsPage key={refreshKey} />;
      case 'anomalies':
        return <AnomaliesPage key={refreshKey} />;
      case 'forecasting':
        return <ForecastingPage key={refreshKey} />;
      case 'recurring':
        return <RecurringPage key={refreshKey} />;
      case 'insights':
        return <InsightsPage key={refreshKey} />;
      case 'savings':
        return <SavingsPage key={refreshKey} />;
      case 'categorization':
        return <CategorizationPage key={refreshKey} />;
      case 'tableau':
        return <TableauPage key={refreshKey} />;
      default:
        return (
          <DashboardPage
            key={refreshKey}
            onNavigate={setActivePage}
            onOpenAddModal={() => {
              setEditingTx(null);
              setTxModalOpen(true);
            }}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
      {/* Navigation Sidebar */}
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        isOpen={sidebarOpen}
        setIsOpen={setSidebarOpen}
        activeAnomaliesCount={activeAnomaliesCount}
        onRefreshData={refreshAll}
      />

      {/* Main Content Stage */}
      <div className="lg:pl-72 flex flex-col min-h-screen transition-all duration-300">
        <Navbar
          activePage={activePage}
          onOpenSidebar={() => setSidebarOpen(true)}
          onOpenAddModal={() => {
            setEditingTx(null);
            setTxModalOpen(true);
          }}
          onScanComplete={refreshAll}
        />

        <main className="flex-1 px-4 sm:px-6 lg:px-8 py-6 max-w-7xl w-full mx-auto">
          {renderActivePage()}
        </main>

        {/* Global Footer */}
        <footer className="mt-auto px-6 py-4 border-t border-slate-800/80 bg-[#0B0F19]/60 text-slate-500 text-xs flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-slate-400 font-medium">FastAPI Engine Operational</span>
            <span className="text-slate-600">·</span>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-emerald-400 underline transition-colors"
            >
              Interactive Swagger API Docs
            </a>
          </div>
          <div className="font-mono-num text-[11px] text-slate-500">
            Finomaly v1.0.0 · Production Portfolio Edition
          </div>
        </footer>
      </div>

      {/* Modals */}
      <TransactionModal
        isOpen={txModalOpen}
        onClose={() => setTxModalOpen(false)}
        onSuccess={() => {
          setTxModalOpen(false);
          refreshAll();
        }}
        initialData={editingTx}
      />

      <CSVUploadModal
        isOpen={csvModalOpen}
        onClose={() => setCsvModalOpen(false)}
        onSuccess={() => {
          setCsvModalOpen(false);
          refreshAll();
        }}
      />
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <NotificationProvider>
        <AuthProvider>
          <MainLayout />
        </AuthProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}
