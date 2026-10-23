export interface User {
  id: number;
  email: string;
  full_name: string;
  is_demo: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Transaction {
  id: number;
  transaction_id?: string;
  date: string;
  raw_description: string;
  clean_merchant: string;
  amount: number;
  transaction_type: 'Expense' | 'Income' | 'Transfer';
  category: string;
  subcategory?: string;
  budget_bucket: 'Needs' | 'Wants' | 'Savings' | 'Income';
  is_recurring?: boolean;
  payment_channel?: string;
  city?: string;
  state?: string;
  notes?: string;
  account_id?: string;
  is_demo?: boolean;
}

export interface TransactionListResponse {
  total: number;
  page: number;
  page_size: number;
  transactions: Transaction[];
}

export interface CSVImportResult {
  total_rows: number;
  imported: number;
  skipped_duplicates: number;
  errors: string[];
}

export interface BudgetPerformanceItem {
  category: string;
  budget_bucket: 'Needs' | 'Wants' | 'Savings';
  monthly_target: number;
  actual_spent: number;
  remaining_amount: number;
  utilization_pct: number;
  alert_threshold: number;
  status: 'OK' | 'APPROACHING' | 'EXCEEDED';
}

export interface BudgetSummary {
  year_month: string;
  total_budget: number;
  total_spent: number;
  remaining_total: number;
  overall_utilization_pct: number;
  needs_spent: number;
  needs_budget: number;
  wants_spent: number;
  wants_budget: number;
  savings_allocated: number;
  savings_target: number;
  items: BudgetPerformanceItem[];
}

export interface GoalContribution {
  id: number;
  goal_id: number;
  amount: number;
  date: string;
  notes?: string;
}

export interface SavingsGoal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  category: string;
  notes?: string;
  is_completed: boolean;
  progress_pct: number;
  remaining_amount: number;
  projected_completion_date?: string;
  average_monthly_contribution: number;
  contributions: GoalContribution[];
}

export interface AnomalyAlert {
  id: number;
  user_id: number;
  transaction_id?: number;
  alert_type: string;
  title: string;
  explanation: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  comparison_metric?: string;
  difference_amount?: number;
  status: 'active' | 'reviewed' | 'dismissed';
  created_at: string;
  transaction_date?: string;
  transaction_merchant?: string;
  transaction_amount?: number;
  transaction_category?: string;
}

export interface AnomalyScanResult {
  scanned_transactions: number;
  new_anomalies_detected: number;
  method_used: string;
  alerts: AnomalyAlert[];
}

export interface DashboardKPIs {
  total_income: number;
  total_expenses: number;
  remaining_balance: number;
  savings_rate: number;
  needs_spend: number;
  wants_spend: number;
  savings_alloc: number;
  needs_pct: number;
  wants_pct: number;
  savings_pct: number;
  active_anomalies_count: number;
  predicted_eom_spend: number;
  budget_target: number;
  currency_symbol: string;
}

export interface MonthlyTrendPoint {
  year_month: string;
  income: number;
  expense: number;
  net_savings: number;
  savings_rate_pct: number;
}

export interface CategoryBreakdownItem {
  category: string;
  budget_bucket: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface RecentTransactionItem {
  id: number;
  date: string;
  clean_merchant: string;
  amount: number;
  transaction_type: string;
  category: string;
  budget_bucket: string;
}

export interface ForecastPoint {
  period: string;
  actual_spend?: number;
  forecast_spend: number;
  lower_bound: number;
  upper_bound: number;
  is_forecast: boolean;
}

export interface ForecastSummary {
  model_name: string;
  historical_months_used: number;
  current_month_to_date: number;
  projected_end_of_month: number;
  current_monthly_budget: number;
  budget_variance: number;
  status: 'ON_TRACK' | 'AT_RISK' | 'OVER_BUDGET';
  limitations_note: string;
  forward_projections: ForecastPoint[];
}

export interface RecurringPaymentItem {
  merchant: string;
  category: string;
  estimated_amount: number;
  observed_frequency: string;
  transaction_count: number;
  last_payment_date: string;
  estimated_next_date: string;
  is_confirmed: boolean;
  projected_annual_cost: number;
}

export interface FinancialInsightItem {
  id: string;
  type: 'positive' | 'warning' | 'neutral' | 'tip';
  title: string;
  observation: string;
  metric_highlight: string;
  category?: string;
}

export interface CategorizationSuggestion {
  suggested_category: string;
  suggested_subcategory: string;
  suggested_budget_bucket: string;
  confidence: number;
  matched_rule?: string;
}

export interface CategoryRule {
  id: number;
  keyword_pattern: string;
  category: string;
  subcategory?: string;
  budget_bucket: string;
}

export interface TableauDataset {
  id: string;
  name: string;
  filename: string;
  description: string;
  record_grain: string;
  recommended_visuals: string;
}
