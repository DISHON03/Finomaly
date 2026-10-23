"""
Finomaly - Predictive Forecasting & Runway Modeling
Generates 3-to-6-month forward projections for cash flow and category burn rates
using Exponential Smoothing and trend-adjusted moving averages.
"""

import pandas as pd
import numpy as np

def forecast_monthly_expenses(df, horizon_months=6, alpha=0.35, beta=0.15):
    """
    Double Exponential Smoothing (Holt's Linear Trend) for monthly expense forecasting.
    Includes 95% confidence intervals and historical backtest fit.
    """
    exp_df = df[df["transaction_type"] == "Expense"]
    monthly_series = exp_df.groupby("year_month")["amount"].sum().reset_index()
    monthly_series["date_parsed"] = pd.to_datetime(monthly_series["year_month"] + "-01")
    monthly_series = monthly_series.sort_values(by="date_parsed").reset_index(drop=True)

    y = monthly_series["amount"].values
    n = len(y)

    if n < 4:
        raise ValueError("Need at least 4 months of data to construct a valid forecast.")

    # Initialization
    level = y[0]
    trend = y[1] - y[0]
    
    fitted = [level + trend]
    levels = [level]
    trends = [trend]

    for t in range(1, n):
        val = y[t]
        last_level = level
        last_trend = trend
        level = alpha * val + (1 - alpha) * (last_level + last_trend)
        trend = beta * (level - last_level) + (1 - beta) * last_trend
        fitted.append(level + trend)
        levels.append(level)
        trends.append(trend)

    monthly_series["fitted_amount"] = np.round(fitted, 2)
    residuals = y - fitted
    sigma = np.std(residuals)

    # Project forward
    last_date = monthly_series["date_parsed"].iloc[-1]
    forecast_rows = []

    for h in range(1, horizon_months + 1):
        future_date = last_date + pd.DateOffset(months=h)
        future_ym = future_date.strftime("%Y-%m")
        # Holt's linear projection: level + h * trend
        pred_val = round(level + (h * trend), 2)
        
        # Uncertainty widens with horizon
        margin = round(1.96 * sigma * np.sqrt(h), 2)
        lower_bound = max(0, round(pred_val - margin, 2))
        upper_bound = round(pred_val + margin, 2)

        forecast_rows.append({
            "year_month": future_ym,
            "forecast_spend": pred_val,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "is_forecast": True
        })

    forecast_df = pd.DataFrame(forecast_rows)
    return monthly_series, forecast_df, sigma

def calculate_savings_runway(current_savings, avg_monthly_burn, avg_monthly_income):
    """
    Calculates runway in months if income ceased or decreased.
    """
    net_burn = avg_monthly_burn - avg_monthly_income
    emergency_runway_no_income = round(current_savings / avg_monthly_burn, 1) if avg_monthly_burn > 0 else 999.0
    
    return {
        "current_savings": current_savings,
        "monthly_burn": avg_monthly_burn,
        "runway_months_zero_income": emergency_runway_no_income,
        "healthy_emergency_fund_target_3mo": round(avg_monthly_burn * 3, 2),
        "healthy_emergency_fund_target_6mo": round(avg_monthly_burn * 6, 2),
    }
