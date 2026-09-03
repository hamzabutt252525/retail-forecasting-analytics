"""
TABLEAU DATA PREPARATION
Aggregates and reshapes model outputs into Tableau-friendly CSVs.
"""

import pandas as pd
import numpy as np
import os
import sqlite3

os.makedirs('../tableau', exist_ok=True)

print("="*60)
print("PREPARING TABLEAU DATA")
print("="*60)

# ============================================
# FILE 1: Daily revenue with model predictions (LONG format)
# ============================================
predictions = pd.read_csv('../analysis/forecast_predictions.csv')
predictions['sale_date'] = pd.to_datetime(predictions['sale_date'])

model_cols = ['actual', 'xgboost', 'random_forest', 'naive_baseline', 
              'prophet', 'moving_avg', 'seasonal_naive']
model_cols = [c for c in model_cols if c in predictions.columns]

predictions_long = predictions.melt(
    id_vars=['sale_date'],
    value_vars=model_cols,
    var_name='model',
    value_name='revenue'
)

name_map = {
    'actual': 'Actual',
    'xgboost': 'XGBoost',
    'random_forest': 'Random Forest',
    'naive_baseline': 'Naive Baseline (lag_365)',
    'prophet': 'Prophet',
    'moving_avg': 'Moving Avg (30-day)',
    'seasonal_naive': 'Seasonal Naive (lag_7)'
}
predictions_long['model'] = predictions_long['model'].map(name_map)

predictions_long.to_csv('../tableau/forecast_predictions_long.csv', index=False)
print(f"Saved: forecast_predictions_long.csv ({len(predictions_long)} rows)")

# ============================================
# FILE 2: Full historical revenue (for trend view)
# ============================================
full = pd.read_csv('../analysis/forecasting_features_enhanced.csv')
full['sale_date'] = pd.to_datetime(full['sale_date'])

historical = full[['sale_date', 'total_revenue', 'month', 'quarter', 'year',
                    'day_of_week', 'is_weekend', 'has_campaign', 
                    'is_holiday_season', 'is_december']].copy()
historical.columns = ['sale_date', 'revenue', 'month', 'quarter', 'year',
                       'day_of_week', 'is_weekend', 'has_campaign',
                       'is_holiday_season', 'is_december']

dow_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
historical['day_name'] = historical['day_of_week'].map(dow_map)

month_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
             7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
historical['month_name'] = historical['month'].map(month_map)

historical.to_csv('../tableau/historical_revenue.csv', index=False)
print(f"Saved: historical_revenue.csv ({len(historical)} rows)")

# ============================================
# FILE 3: Model comparison metrics
# ============================================
model_comp = pd.read_csv('../analysis/model_comparison.csv')
model_comp.to_csv('../tableau/model_comparison.csv', index=False)
print(f"Saved: model_comparison.csv ({len(model_comp)} rows)")

# ============================================
# FILE 4: Feature importance
# ============================================
rf_imp = pd.read_csv('../analysis/rf_feature_importance.csv')
rf_imp['importance_pct'] = (rf_imp['importance'] * 100).round(2)
rf_imp.to_csv('../tableau/feature_importance.csv', index=False)
print(f"Saved: feature_importance.csv ({len(rf_imp)} rows)")

# ============================================
# Database-derived files
# ============================================
conn = sqlite3.connect('../data/retail_analytics.db')

# FILE 5: Category performance
category_perf = pd.read_sql("""
SELECT 
    p.category,
    COUNT(DISTINCT ds.sku_id) as sku_count,
    ROUND(SUM(ds.revenue_gbp), 0) as total_revenue,
    ROUND(SUM(ds.gross_profit_gbp), 0) as total_profit,
    ROUND(AVG(ds.units_sold), 1) as avg_daily_units,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales), 2) as pct_of_total
FROM daily_sales ds
JOIN products p ON ds.sku_id = p.sku_id
GROUP BY p.category
ORDER BY total_revenue DESC
""", conn)

category_perf.to_csv('../tableau/category_performance.csv', index=False)
print(f"Saved: category_performance.csv ({len(category_perf)} rows)")

# FILE 6: Store performance
store_perf = pd.read_sql("""
SELECT 
    s.store_name,
    s.size as store_size,
    s.location,
    ROUND(SUM(ds.revenue_gbp), 0) as total_revenue,
    ROUND(SUM(ds.gross_profit_gbp), 0) as total_profit,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales), 2) as pct_of_total
FROM daily_sales ds
JOIN stores s ON ds.store_id = s.store_id
GROUP BY s.store_id
ORDER BY total_revenue DESC
""", conn)

store_perf.to_csv('../tableau/store_performance.csv', index=False)
print(f"Saved: store_performance.csv ({len(store_perf)} rows)")

# FILE 7: Campaign ROI (Incremental)
campaign_roi = pd.read_sql("""
WITH baseline AS (
    SELECT AVG(revenue_gbp) AS baseline_daily
    FROM daily_sales
    WHERE active_campaign IS NULL
),
campaign_perf AS (
    SELECT 
        c.campaign_name,
        c.marketing_spend_gbp,
        AVG(ds.revenue_gbp) AS campaign_avg_daily,
        SUM(ds.revenue_gbp) AS revenue_during,
        julianday(c.end_date) - julianday(c.start_date) + 1 AS campaign_days
    FROM campaigns c
    LEFT JOIN daily_sales ds ON ds.sale_date BETWEEN c.start_date AND c.end_date
    GROUP BY c.campaign_id
)
SELECT 
    cp.campaign_name,
    cp.marketing_spend_gbp AS marketing_spend,
    ROUND(cp.revenue_during, 0) AS revenue_during,
    ROUND((cp.campaign_avg_daily - b.baseline_daily) * cp.campaign_days, 0) AS incremental_revenue,
    ROUND(((cp.campaign_avg_daily - b.baseline_daily) * cp.campaign_days) / NULLIF(cp.marketing_spend_gbp, 0), 2) AS incremental_roi
FROM campaign_perf cp
CROSS JOIN baseline b
ORDER BY incremental_roi DESC
""", conn)

campaign_roi.to_csv('../tableau/campaign_roi.csv', index=False)
print(f"Saved: campaign_roi.csv ({len(campaign_roi)} rows)")