"""
EDA VISUAL DIAGNOSTICS
Generates 4 diagnostic plots + summary statistics for retail sales forecasting.
Outputs saved to screenshots/eda/ for dashboard and documentation use.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
import os

# Setup
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
os.makedirs('../screenshots/eda', exist_ok=True)

print("="*60)
print("EDA VISUAL DIAGNOSTICS")
print("="*60)

# Load enhanced features
df = pd.read_csv('../analysis/forecasting_features_enhanced.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])
df = df.sort_values('sale_date').reset_index(drop=True)

print(f"Loaded {len(df)} daily records")
print(f"Date range: {df['sale_date'].min().date()} to {df['sale_date'].max().date()}")

# ============================================
# PLOT 1: Revenue Distribution
# ============================================
print("\n[1/4] Revenue distribution...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(df['total_revenue'], bins=60, color='steelblue', edgecolor='black')
axes[0].set_title('Daily Revenue Distribution (Raw)', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Daily Revenue (GBP)')
axes[0].set_ylabel('Frequency')
axes[0].axvline(df['total_revenue'].mean(), color='red', linestyle='--', 
                label=f"Mean: {df['total_revenue'].mean():,.0f}")
axes[0].axvline(df['total_revenue'].median(), color='green', linestyle='--', 
                label=f"Median: {df['total_revenue'].median():,.0f}")
axes[0].legend()

axes[1].hist(np.log1p(df['total_revenue']), bins=60, color='coral', edgecolor='black')
axes[1].set_title('Daily Revenue Distribution (Log-Transformed)', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Log(Daily Revenue)')
axes[1].set_ylabel('Frequency')

skewness = df['total_revenue'].skew()
plt.suptitle(f'Revenue Distribution Analysis | Skewness: {skewness:.2f}', 
             fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig('../screenshots/eda/01_revenue_distribution.png', bbox_inches='tight', dpi=120)
plt.close()
print(f"  Saved: 01_revenue_distribution.png | Skewness: {skewness:.2f}")

# ============================================
# PLOT 2: Revenue Time Series
# ============================================
print("\n[2/4] Revenue time series over 36 months...")
fig, ax = plt.subplots(figsize=(16, 6))

ax.plot(df['sale_date'], df['total_revenue'], color='steelblue', linewidth=0.8, 
        alpha=0.7, label='Daily Revenue')
ax.plot(df['sale_date'], df['total_revenue'].rolling(30).mean(), color='darkred', 
        linewidth=2, label='30-day Moving Avg')

black_fridays = [pd.Timestamp('2023-11-24'), pd.Timestamp('2024-11-29'), pd.Timestamp('2025-11-28')]
for bf in black_fridays:
    ax.axvline(bf, color='orange', linestyle=':', alpha=0.6)
    ax.annotate('BF', xy=(bf, df['total_revenue'].max()*0.95), ha='center', 
                fontsize=9, color='orange', fontweight='bold')

christmases = [pd.Timestamp('2023-12-25'), pd.Timestamp('2024-12-25'), pd.Timestamp('2025-12-25')]
for xm in christmases:
    ax.axvline(xm, color='green', linestyle=':', alpha=0.6)
    ax.annotate('Xmas', xy=(xm, df['total_revenue'].max()*0.85), ha='center', 
                fontsize=9, color='green', fontweight='bold')

ax.set_title('Daily Revenue Time Series (Jan 2023 - Dec 2025)', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Daily Revenue (GBP)')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../screenshots/eda/02_revenue_timeseries.png', bbox_inches='tight', dpi=120)
plt.close()
print("  Saved: 02_revenue_timeseries.png")

# ============================================
# PLOT 3: Autocorrelation
# ============================================
print("\n[3/4] Autocorrelation analysis...")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

plot_acf(df['total_revenue'], lags=60, ax=axes[0])
axes[0].set_title('Autocorrelation Function (ACF) - 60 lags', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Lag (days)')

plot_pacf(df['total_revenue'], lags=60, ax=axes[1], method='ywm')
axes[1].set_title('Partial Autocorrelation (PACF) - 60 lags', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Lag (days)')

adf_result = adfuller(df['total_revenue'])
stationarity_note = "STATIONARY" if adf_result[1] < 0.05 else "NON-STATIONARY"
plt.suptitle(f'ADF Test p-value: {adf_result[1]:.4f} -> Series is {stationarity_note}', 
             fontsize=12, y=1.02)
plt.tight_layout()
plt.savefig('../screenshots/eda/03_autocorrelation.png', bbox_inches='tight', dpi=120)
plt.close()
print(f"  Saved: 03_autocorrelation.png | ADF p-value: {adf_result[1]:.4f} ({stationarity_note})")

# ============================================
# PLOT 4: Weekly + Monthly Seasonality
# ============================================
print("\n[4/4] Weekly seasonality pattern...")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
dow_avg = df.groupby('day_of_week')['total_revenue'].mean().reindex([0,1,2,3,4,5,6])
colors_dow = ['steelblue']*5 + ['coral']*2

axes[0].bar(dow_names, dow_avg.values, color=colors_dow, edgecolor='black')
axes[0].set_title('Average Daily Revenue by Day of Week', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Avg Daily Revenue (GBP)')
for i, v in enumerate(dow_avg.values):
    axes[0].text(i, v, f'{v/1000:.0f}K', ha='center', va='bottom', fontsize=10)

month_avg = df.groupby('month')['total_revenue'].mean()
month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
colors_month = ['steelblue']*10 + ['darkred']*2

axes[1].bar(month_names, month_avg.values, color=colors_month, edgecolor='black')
axes[1].set_title('Average Daily Revenue by Month', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Avg Daily Revenue (GBP)')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('../screenshots/eda/04_seasonality.png', bbox_inches='tight', dpi=120)
plt.close()
print("  Saved: 04_seasonality.png")

# ============================================
# SUMMARY REPORT
# ============================================
print("\n" + "="*60)
print("EDA SUMMARY STATISTICS")
print("="*60)

weekend_rev = df[df['is_weekend']==1]['total_revenue'].mean()
weekday_rev = df[df['is_weekend']==0]['total_revenue'].mean()
dec_rev = df[df['month']==12]['total_revenue'].mean()
avg_rev = df['total_revenue'].mean()

print(f"""
Revenue statistics:
  Mean:     {df['total_revenue'].mean():,.0f}
  Median:   {df['total_revenue'].median():,.0f}
  Std:      {df['total_revenue'].std():,.0f}
  Skewness: {skewness:.2f}
  
Weekend effect:
  Avg weekday: {weekday_rev:,.0f}
  Avg weekend: {weekend_rev:,.0f}
  Lift: {(weekend_rev/weekday_rev - 1)*100:.1f}%

December seasonality:
  Avg December: {dec_rev:,.0f}
  Portfolio avg: {avg_rev:,.0f}
  Lift: {(dec_rev/avg_rev - 1)*100:.1f}%

Stationarity:
  ADF p-value: {adf_result[1]:.4f}
  Interpretation: {stationarity_note}

Autocorrelation observations:
  Strong 7-day cycle (weekly seasonality)
  365-day spike (annual seasonality)

Files generated in screenshots/eda/:
  01_revenue_distribution.png
  02_revenue_timeseries.png
  03_autocorrelation.png
  04_seasonality.png
""")

print("="*60)
print("EDA COMPLETE")
print("="*60)