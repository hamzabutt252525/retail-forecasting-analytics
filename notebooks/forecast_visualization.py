"""
FORECAST VISUALIZATION
Plots actual vs predicted revenue for all 6 models on 90-day test period.
Generates comparison chart for LinkedIn article and dashboard.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
os.makedirs('../screenshots/forecasts', exist_ok=True)

print("="*60)
print("FORECAST VISUALIZATION")
print("="*60)

# Load predictions
df = pd.read_csv('../analysis/forecast_predictions.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])
df = df.sort_values('sale_date').reset_index(drop=True)

# Load model comparison for MAPE labels
results = pd.read_csv('../analysis/model_comparison.csv')
mape_lookup = dict(zip(results['model'], results['MAPE']))

print(f"Loaded {len(df)} test predictions")
print(f"Test period: {df['sale_date'].min().date()} to {df['sale_date'].max().date()}")

# ============================================
# PLOT 1: ALL MODELS OVERLAID
# ============================================
print("\n[1/3] Generating combined forecast plot...")

fig, ax = plt.subplots(figsize=(18, 8))

# Actual (thick black line)
ax.plot(df['sale_date'], df['actual'], color='black', linewidth=2.5, 
        label=f"Actual Revenue", zorder=10)

# Models with distinct colors
model_configs = [
    ('xgboost', 'XGBoost', 'darkgreen', 2.0, '-'),
    ('random_forest', 'Random Forest', 'forestgreen', 1.5, '-'),
    ('naive_baseline', 'Naive Baseline (lag_365)', 'orange', 1.3, '--'),
    ('prophet', 'Prophet', 'purple', 1.3, '--'),
    ('moving_avg', 'Moving Avg (30-day)', 'gray', 1.0, ':'),
    ('seasonal_naive', 'Seasonal Naive (lag_7)', 'lightcoral', 1.0, ':')
]

for col, name, color, lw, ls in model_configs:
    if col in df.columns and df[col].notna().any():
        mape_val = mape_lookup.get(name, 'N/A')
        label = f"{name} (MAPE: {mape_val}%)" if mape_val != 'N/A' else name
        ax.plot(df['sale_date'], df[col], color=color, linewidth=lw, 
                linestyle=ls, alpha=0.75, label=label)

# Highlight Black Friday and Christmas
ax.axvline(pd.Timestamp('2025-11-28'), color='red', linestyle=':', alpha=0.4)
ax.annotate('Black Friday', xy=(pd.Timestamp('2025-11-28'), df['actual'].max()*0.98), 
            ha='center', fontsize=9, color='red', fontweight='bold')

ax.axvline(pd.Timestamp('2025-12-25'), color='darkgreen', linestyle=':', alpha=0.4)
ax.annotate('Christmas', xy=(pd.Timestamp('2025-12-25'), df['actual'].max()*0.90), 
            ha='center', fontsize=9, color='darkgreen', fontweight='bold')

ax.set_title('90-Day Forecast Comparison: All 6 Models vs Actual Revenue', 
             fontsize=15, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue (GBP)', fontsize=12)
ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../screenshots/forecasts/01_all_models_comparison.png', bbox_inches='tight', dpi=120)
plt.close()
print("  Saved: 01_all_models_comparison.png")

# ============================================
# PLOT 2: BEST MODEL (XGBOOST) DETAIL
# ============================================
print("\n[2/3] Generating XGBoost detail plot...")

fig, ax = plt.subplots(figsize=(18, 7))

ax.plot(df['sale_date'], df['actual'], color='black', linewidth=2.5, 
        label='Actual Revenue', zorder=10)
ax.plot(df['sale_date'], df['xgboost'], color='darkgreen', linewidth=2, 
        label=f"XGBoost Forecast (MAPE: {mape_lookup.get('XGBoost', 'N/A')}%)")

# Fill the error area
ax.fill_between(df['sale_date'], df['actual'], df['xgboost'], 
                alpha=0.15, color='green', label='Forecast Error')

# Annotate holidays
ax.axvline(pd.Timestamp('2025-11-28'), color='red', linestyle=':', alpha=0.5)
ax.annotate('Black Friday', xy=(pd.Timestamp('2025-11-28'), df['actual'].max()*0.98), 
            ha='center', fontsize=10, color='red', fontweight='bold')

ax.axvline(pd.Timestamp('2025-12-25'), color='darkgreen', linestyle=':', alpha=0.5)
ax.annotate('Christmas', xy=(pd.Timestamp('2025-12-25'), df['actual'].max()*0.90), 
            ha='center', fontsize=10, color='darkgreen', fontweight='bold')

ax.axvline(pd.Timestamp('2025-12-01'), color='purple', linestyle=':', alpha=0.5)
ax.annotate('Cyber Monday', xy=(pd.Timestamp('2025-12-01'), df['actual'].max()*0.82), 
            ha='center', fontsize=10, color='purple', fontweight='bold')

ax.set_title('XGBoost Forecast Performance | 90-Day Holdout | 2.95% MAPE', 
             fontsize=15, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Daily Revenue (GBP)', fontsize=12)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../screenshots/forecasts/02_xgboost_detail.png', bbox_inches='tight', dpi=120)
plt.close()
print("  Saved: 02_xgboost_detail.png")

# ============================================
# PLOT 3: MODEL COMPARISON BAR CHART (MAPE)
# ============================================
print("\n[3/3] Generating MAPE comparison chart...")

fig, ax = plt.subplots(figsize=(12, 6))

results_sorted = results.sort_values('MAPE', ascending=True)
colors_bar = ['darkgreen' if m == 'XGBoost' else 
              'forestgreen' if m == 'Random Forest' else
              'orange' if 'Naive Baseline' in m else
              'gray' for m in results_sorted['model']]

bars = ax.barh(results_sorted['model'], results_sorted['MAPE'], color=colors_bar, edgecolor='black')

# Value labels
for bar, val in zip(bars, results_sorted['MAPE']):
    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.2f}%', 
            va='center', fontsize=11, fontweight='bold')

# Baseline reference line
baseline_mape = results[results['model'] == 'Naive Baseline (lag_365)']['MAPE'].values[0]
ax.axvline(baseline_mape, color='red', linestyle='--', alpha=0.5, 
           label=f'Naive Baseline: {baseline_mape:.2f}%')

ax.set_title('Model Comparison: MAPE on 90-Day Holdout (Lower is Better)', 
             fontsize=14, fontweight='bold')
ax.set_xlabel('MAPE (%)', fontsize=12)
ax.set_ylabel('')
ax.legend(loc='lower right', fontsize=11)
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('../screenshots/forecasts/03_mape_comparison.png', bbox_inches='tight', dpi=120)
plt.close()
print("  Saved: 03_mape_comparison.png")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*60)
print("VISUALIZATION COMPLETE")
print("="*60)
print(f"""
Files generated in screenshots/forecasts/:
  01_all_models_comparison.png  (all 6 models overlaid)
  02_xgboost_detail.png         (best model detailed view)
  03_mape_comparison.png        (MAPE ranking bar chart)

Best model: XGBoost @ 2.95% MAPE
Improvement over naive baseline: 83.4%
""")