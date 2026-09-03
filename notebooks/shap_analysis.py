"""
SHAP analysis for XGBoost forecasting model.
Generates 2 interpretability plots for the GitHub repo.
"""

import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt
import os

os.makedirs('../screenshots/shap', exist_ok=True)

print("Loading model and data...")
model = joblib.load('../models/forecast_model_xgboost.pkl')
df = pd.read_csv('../analysis/forecasting_features_enhanced.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])

feature_cols = [
    'month', 'day_of_week', 'is_weekend', 'quarter', 
    'has_campaign', 'is_holiday_season', 'is_december',
    'days_until_black_friday', 'days_until_christmas', 
    'days_until_ramadan', 'days_until_eid', 'days_until_cyber_monday',
    'dow_sin', 'dow_cos', 'month_sin', 'month_cos',
    'ma_7day', 'ma_30day', 'rolling_std_7day', 'rolling_std_30day',
    'days_since_last_campaign'
]
feature_cols = [c for c in feature_cols if c in df.columns]

X = df[feature_cols].dropna()

print("Computing SHAP values...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# PLOT 1: Summary plot (top features by SHAP magnitude)
print("Generating summary plot...")
plt.figure(figsize=(12, 8))
shap.summary_plot(shap_values, X, plot_type='bar', show=False, max_display=15)
plt.title('SHAP Feature Importance - XGBoost Retail Forecasting Model', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../screenshots/shap/01_shap_summary_bar.png', bbox_inches='tight', dpi=120)
plt.close()

# PLOT 2: Beeswarm plot (feature value vs SHAP impact)
print("Generating beeswarm plot...")
plt.figure(figsize=(12, 8))
shap.summary_plot(shap_values, X, show=False, max_display=15)
plt.title('SHAP Feature Impact Distribution - Retail Revenue Forecasting', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('../screenshots/shap/02_shap_beeswarm.png', bbox_inches='tight', dpi=120)
plt.close()

print("\nDone. Files saved:")
print("  screenshots/shap/01_shap_summary_bar.png")
print("  screenshots/shap/02_shap_beeswarm.png")