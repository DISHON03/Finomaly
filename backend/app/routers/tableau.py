from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.services.auth_service import get_current_user
from backend.app.services.tableau_service import (
    generate_tableau_transactions_csv,
    generate_tableau_monthly_summary_csv,
    generate_tableau_category_expenses_csv,
    generate_tableau_budget_vs_actual_csv,
    generate_tableau_anomalies_csv,
    generate_tableau_forecast_csv,
    export_all_tableau_files
)

router = APIRouter(prefix="/tableau", tags=["Tableau BI Integration"])

DATASET_METADATA = [
    {
        "id": "transactions",
        "name": "Transactions Feed",
        "filename": "transactions_tableau.csv",
        "description": "Granular transaction records enriched with calendar dimensions, day of week, weekend flags, and merchant normalization.",
        "record_grain": "1 row per transaction",
        "recommended_visuals": "Time series scatter plots, transaction histograms, Pareto merchant rank."
    },
    {
        "id": "monthly-summary",
        "name": "Monthly Financial Summaries",
        "filename": "monthly_financial_summaries_tableau.csv",
        "description": "Monthly aggregates of income, expenses, net cash flow, savings rate %, and 50/30/20 budget allocations.",
        "record_grain": "1 row per year-month",
        "recommended_visuals": "Cash flow trend lines, dual-axis savings rate, 50/30/20 stacked bar chart."
    },
    {
        "id": "category-expenses",
        "name": "Category-Wise Expenses",
        "filename": "category_expenses_tableau.csv",
        "description": "Category aggregates with total spend, transaction volume, average ticket size, and % share of total spending.",
        "record_grain": "1 row per category and budget bucket",
        "recommended_visuals": "Category treemap, donut breakdown, ticket size vs volume scatter."
    },
    {
        "id": "budget-vs-actual",
        "name": "Budget vs Actual Performance",
        "filename": "budget_vs_actual_tableau.csv",
        "description": "Category target vs actual spending, remaining budget amounts, utilization %, and warning status.",
        "record_grain": "1 row per category for the current period",
        "recommended_visuals": "Bullet graphs, budget variance bar chart, threshold traffic light cards."
    },
    {
        "id": "spending-anomalies",
        "name": "Spending Anomalies & Outliers",
        "filename": "spending_anomalies_tableau.csv",
        "description": "Flagged outliers with severity, statistical comparison metrics (multipliers vs median), difference amounts, and status.",
        "record_grain": "1 row per flagged anomaly alert",
        "recommended_visuals": "Outlier scatter plot with threshold boundaries, severity breakdown."
    },
    {
        "id": "forecast-vs-actual",
        "name": "Forecast vs Actual Expenses",
        "filename": "forecast_vs_actual_tableau.csv",
        "description": "Historical spend alongside forward Double Exponential Smoothing projections with 95% upper and lower confidence intervals.",
        "record_grain": "1 row per month (historical + forecast)",
        "recommended_visuals": "Fan chart / confidence cone, forward trajectory line with shaded error band."
    }
]

@router.get("/datasets")
def list_tableau_datasets():
    """Lists available Tableau analytical datasets with metadata and schema descriptions."""
    return DATASET_METADATA

@router.get("/export/{dataset_id}")
def export_dataset_csv(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates and downloads a clean, documented CSV dataset for Tableau Desktop / Tableau Public."""
    if dataset_id == "transactions":
        content = generate_tableau_transactions_csv(db, current_user.id)
        filename = "transactions_tableau.csv"
    elif dataset_id == "monthly-summary":
        content = generate_tableau_monthly_summary_csv(db, current_user.id)
        filename = "monthly_financial_summaries_tableau.csv"
    elif dataset_id == "category-expenses":
        content = generate_tableau_category_expenses_csv(db, current_user.id)
        filename = "category_expenses_tableau.csv"
    elif dataset_id == "budget-vs-actual":
        content = generate_tableau_budget_vs_actual_csv(db, current_user.id)
        filename = "budget_vs_actual_tableau.csv"
    elif dataset_id == "spending-anomalies":
        content = generate_tableau_anomalies_csv(db, current_user.id)
        filename = "spending_anomalies_tableau.csv"
    elif dataset_id == "forecast-vs-actual":
        content = generate_tableau_forecast_csv(db, current_user.id)
        filename = "forecast_vs_actual_tableau.csv"
    else:
        content = generate_tableau_transactions_csv(db, current_user.id)
        filename = "tableau_export.csv"

    # Also persist to tableau/exports folder
    try:
        export_all_tableau_files(db, current_user.id)
    except Exception:
        pass

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
