import {
  AuthResponse,
  User,
  Transaction,
  TransactionListResponse,
  CSVImportResult,
  BudgetSummary,
  BudgetPerformanceItem,
  SavingsGoal,
  AnomalyAlert,
  AnomalyScanResult,
  DashboardKPIs,
  MonthlyTrendPoint,
  CategoryBreakdownItem,
  RecentTransactionItem,
  ForecastSummary,
  RecurringPaymentItem,
  FinancialInsightItem,
  CategorizationSuggestion,
  CategoryRule,
  TableauDataset
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private getAuthHeaders(isJson: boolean = true): HeadersInit {
    const headers: Record<string, string> = {};
    if (isJson) {
      headers['Content-Type'] = 'application/json';
    }
    const token = localStorage.getItem('finomaly_token') || localStorage.getItem('spendsense_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const res = await fetch(url, options);

    if (!res.ok) {
      let errorMsg = `API Error ${res.status}: ${res.statusText}`;
      try {
        const errorJson = await res.json();
        if (errorJson.detail) {
          errorMsg = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return await res.json() as T;
  }

  // --- Auth ---
  async demoLogin(): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>('/auth/demo-login', {
      method: 'POST',
      headers: this.getAuthHeaders()
    });
    localStorage.setItem('finomaly_token', res.access_token);
    localStorage.setItem('finomaly_user', JSON.stringify(res.user));
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
    return res;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ email, password })
    });
    localStorage.setItem('finomaly_token', res.access_token);
    localStorage.setItem('finomaly_user', JSON.stringify(res.user));
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
    return res;
  }

  async register(email: string, password: string, full_name: string): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ email, password, full_name })
    });
    localStorage.setItem('finomaly_token', res.access_token);
    localStorage.setItem('finomaly_user', JSON.stringify(res.user));
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me', {
      headers: this.getAuthHeaders()
    });
  }

  logout() {
    localStorage.removeItem('finomaly_token');
    localStorage.removeItem('finomaly_user');
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
  }

  // --- Dashboard ---
  async getKPIs(params?: { date_from?: string; date_to?: string; category?: string }): Promise<DashboardKPIs> {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    if (params?.category) query.append('category', params.category);
    return this.request<DashboardKPIs>(`/dashboard/kpis?${query.toString()}`, {
      headers: this.getAuthHeaders()
    });
  }

  async getTrends(): Promise<MonthlyTrendPoint[]> {
    return this.request<MonthlyTrendPoint[]>('/dashboard/trends', {
      headers: this.getAuthHeaders()
    });
  }

  async getCategoryBreakdown(params?: { date_from?: string; date_to?: string }): Promise<CategoryBreakdownItem[]> {
    const query = new URLSearchParams();
    if (params?.date_from) query.append('date_from', params.date_from);
    if (params?.date_to) query.append('date_to', params.date_to);
    return this.request<CategoryBreakdownItem[]>(`/dashboard/category-breakdown?${query.toString()}`, {
      headers: this.getAuthHeaders()
    });
  }

  async getRecentTransactions(limit: number = 8): Promise<RecentTransactionItem[]> {
    return this.request<RecentTransactionItem[]>(`/dashboard/recent-transactions?limit=${limit}`, {
      headers: this.getAuthHeaders()
    });
  }

  async resetDemoProfile(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/dashboard/reset-demo', {
      method: 'POST',
      headers: this.getAuthHeaders()
    });
  }

  // --- Transactions ---
  async listTransactions(params: {
    page?: number;
    page_size?: number;
    search?: string;
    category?: string;
    transaction_type?: string;
    budget_bucket?: string;
    date_from?: string;
    date_to?: string;
  }): Promise<TransactionListResponse> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', String(params.page));
    if (params.page_size) query.append('page_size', String(params.page_size));
    if (params.search) query.append('search', params.search);
    if (params.category) query.append('category', params.category);
    if (params.transaction_type) query.append('transaction_type', params.transaction_type);
    if (params.budget_bucket) query.append('budget_bucket', params.budget_bucket);
    if (params.date_from) query.append('date_from', params.date_from);
    if (params.date_to) query.append('date_to', params.date_to);

    return this.request<TransactionListResponse>(`/transactions?${query.toString()}`, {
      headers: this.getAuthHeaders()
    });
  }

  async createTransaction(tx: Partial<Transaction>): Promise<Transaction> {
    return this.request<Transaction>('/transactions', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(tx)
    });
  }

  async updateTransaction(id: number, tx: Partial<Transaction>): Promise<Transaction> {
    return this.request<Transaction>(`/transactions/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(tx)
    });
  }

  async deleteTransaction(id: number): Promise<void> {
    await this.request<void>(`/transactions/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
  }

  async importCSV(file: File): Promise<CSVImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('finomaly_token') || localStorage.getItem('spendsense_token');
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/transactions/import-csv`, {
      method: 'POST',
      headers,
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to import CSV' }));
      throw new Error(err.detail || 'CSV upload error');
    }
    return res.json();
  }

  getExportCSVUrl(filters?: { category?: string; transaction_type?: string; date_from?: string; date_to?: string }): string {
    const query = new URLSearchParams();
    if (filters?.category) query.append('category', filters.category);
    if (filters?.transaction_type) query.append('transaction_type', filters.transaction_type);
    if (filters?.date_from) query.append('date_from', filters.date_from);
    if (filters?.date_to) query.append('date_to', filters.date_to);
    return `${API_BASE_URL}/transactions/export-csv?${query.toString()}`;
  }

  // --- Budgets ---
  async getBudgets(): Promise<BudgetPerformanceItem[]> {
    return this.request<BudgetPerformanceItem[]>('/budgets', {
      headers: this.getAuthHeaders()
    });
  }

  async getBudgetSummary(): Promise<BudgetSummary> {
    return this.request<BudgetSummary>('/budgets/summary', {
      headers: this.getAuthHeaders()
    });
  }

  async createOrUpdateBudget(data: { category: string; budget_bucket: string; monthly_target: number; alert_threshold?: number }): Promise<any> {
    return this.request('/budgets', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
  }

  async deleteBudget(id: number): Promise<void> {
    await this.request<void>(`/budgets/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
  }

  // --- Savings Goals ---
  async getSavingsGoals(): Promise<SavingsGoal[]> {
    return this.request<SavingsGoal[]>('/savings/goals', {
      headers: this.getAuthHeaders()
    });
  }

  async createSavingsGoal(goal: { name: string; target_amount: number; target_date: string; category?: string; initial_deposit?: number; notes?: string }): Promise<SavingsGoal> {
    return this.request<SavingsGoal>('/savings/goals', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(goal)
    });
  }

  async updateSavingsGoal(id: number, data: Partial<SavingsGoal>): Promise<SavingsGoal> {
    return this.request<SavingsGoal>(`/savings/goals/${id}`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
  }

  async deleteSavingsGoal(id: number): Promise<void> {
    await this.request<void>(`/savings/goals/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
  }

  async addGoalContribution(goalId: number, data: { amount: number; date: string; notes?: string }): Promise<SavingsGoal> {
    return this.request<SavingsGoal>(`/savings/goals/${goalId}/contributions`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data)
    });
  }

  // --- Anomalies ---
  async getAnomalies(status?: string): Promise<AnomalyAlert[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<AnomalyAlert[]>(`/anomalies${query}`, {
      headers: this.getAuthHeaders()
    });
  }

  async scanAnomalies(): Promise<AnomalyScanResult> {
    return this.request<AnomalyScanResult>('/anomalies/scan', {
      method: 'POST',
      headers: this.getAuthHeaders()
    });
  }

  async updateAnomalyStatus(id: number, status: 'active' | 'reviewed' | 'dismissed'): Promise<boolean> {
    return this.request<boolean>(`/anomalies/${id}/status`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ status })
    });
  }

  // --- Forecasting ---
  async getForecast(horizon: number = 4): Promise<ForecastSummary> {
    return this.request<ForecastSummary>(`/forecasting?horizon=${horizon}`, {
      headers: this.getAuthHeaders()
    });
  }

  // --- Recurring Payments ---
  async getRecurringPayments(): Promise<RecurringPaymentItem[]> {
    return this.request<RecurringPaymentItem[]>('/recurring', {
      headers: this.getAuthHeaders()
    });
  }

  // --- Financial Insights ---
  async getFinancialInsights(): Promise<FinancialInsightItem[]> {
    return this.request<FinancialInsightItem[]>('/insights', {
      headers: this.getAuthHeaders()
    });
  }

  // --- Smart Categorization ---
  async suggestCategory(description: string): Promise<CategorizationSuggestion> {
    return this.request<CategorizationSuggestion>('/categorization/suggest', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ description })
    });
  }

  async getCategoryRules(): Promise<CategoryRule[]> {
    return this.request<CategoryRule[]>('/categorization/rules', {
      headers: this.getAuthHeaders()
    });
  }

  async createCategoryRule(rule: { keyword_pattern: string; category: string; subcategory?: string; budget_bucket?: string }): Promise<CategoryRule> {
    return this.request<CategoryRule>('/categorization/rules', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(rule)
    });
  }

  async deleteCategoryRule(id: number): Promise<void> {
    await this.request<void>(`/categorization/rules/${id}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders()
    });
  }

  // --- Tableau Integration ---
  async getTableauDatasets(): Promise<TableauDataset[]> {
    return this.request<TableauDataset[]>('/tableau/datasets', {
      headers: this.getAuthHeaders()
    });
  }

  getTableauExportUrl(datasetId: string): string {
    return `${API_BASE_URL}/tableau/export/${datasetId}`;
  }
}

export const api = new ApiClient();
