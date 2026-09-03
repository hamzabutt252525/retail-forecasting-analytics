"""
FEATURE ENHANCEMENT - Add holiday distance + campaign context features
Addresses DeepSeek critique: static binary flags → dynamic continuous features
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*60)
print("ENHANCING FORECASTING FEATURES")
print("="*60)

# Load the base features from the root folder
df = pd.read_csv('forecasting_features.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])
print(f"Loaded {len(df)} rows with {len(df.columns)} existing features")

# ============================================
# HOLIDAY REFERENCE DATES (all 3 years)
# ============================================
BLACK_FRIDAY_DATES = [
    datetime(2023, 11, 24), datetime(2024, 11, 29), datetime(2025, 11, 28),
    datetime(2026, 11, 27)
]

CHRISTMAS_DATES = [
    datetime(2023, 12, 25), datetime(2024, 12, 25), datetime(2025, 12, 25),
    datetime(2026, 12, 25)
]

RAMADAN_START_DATES = [
    datetime(2023, 3, 22), datetime(2024, 3, 11), datetime(2025, 2, 28),
    datetime(2026, 2, 17)
]

EID_DATES = [
    datetime(2023, 4, 21), datetime(2024, 4, 10), datetime(2025, 3, 30),
    datetime(2026, 3, 20)
]

CYBER_MONDAY_DATES = [
    datetime(2023, 11, 27), datetime(2024, 12, 2), datetime(2025, 12, 1),
    datetime(2026, 11, 30)
]

# ============================================
# DAYS UNTIL / DAYS SINCE FEATURES
# ============================================
def days_to_nearest_future(date, holiday_list):
    future_holidays = [h for h in holiday_list if h >= date]
    if not future_holidays:
        return 365
    days = (min(future_holidays) - date).days
    return min(days, 365)

def days_since_nearest_past(date, holiday_list):
    past_holidays = [h for h in holiday_list if h <= date]
    if not past_holidays:
        return 365
    days = (date - max(past_holidays)).days
    return min(days, 365)

print("\nCalculating days_until_holiday features...")

df['days_until_black_friday'] = df['sale_date'].apply(
    lambda d: days_to_nearest_future(d, BLACK_FRIDAY_DATES)
)
df['days_since_black_friday'] = df['sale_date'].apply(
    lambda d: days_since_nearest_past(d, BLACK_FRIDAY_DATES)
)
df['days_until_christmas'] = df['sale_date'].apply(
    lambda d: days_to_nearest_future(d, CHRISTMAS_DATES)
)
df['days_since_christmas'] = df['sale_date'].apply(
    lambda d: days_since_nearest_past(d, CHRISTMAS_DATES)
)
df['days_until_ramadan'] = df['sale_date'].apply(
    lambda d: days_to_nearest_future(d, RAMADAN_START_DATES)
)
df['days_until_eid'] = df['sale_date'].apply(
    lambda d: days_to_nearest_future(d, EID_DATES)
)
df['days_until_cyber_monday'] = df['sale_date'].apply(
    lambda d: days_to_nearest_future(d, CYBER_MONDAY_DATES)
)

# ============================================
# HOLIDAY PROXIMITY FLAGS (ramp-up periods)
# ============================================
df['is_bf_week'] = ((df['days_until_black_friday'] <= 7) | 
                    (df['days_since_black_friday'] <= 3)).astype(int)
df['is_xmas_2week'] = ((df['days_until_christmas'] <= 14) & 
                       (df['days_until_christmas'] >= 0)).astype(int)
df['is_ramadan_month'] = ((df['days_until_ramadan'] <= 3) | 
                          (df['days_until_eid'] <= 30)).astype(int)

# ============================================
# CYCLICAL ENCODING (proper seasonality representation)
# ============================================
print("Adding cyclical encoding for day of week and month...")

df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# ============================================
# ROLLING VOLATILITY FEATURES
# ============================================
print("Adding rolling volatility features...")

df = df.sort_values('sale_date').reset_index(drop=True)
df['rolling_std_7day'] = df['total_revenue'].rolling(window=7, min_periods=1).std()
df['rolling_std_30day'] = df['total_revenue'].rolling(window=30, min_periods=1).std()

# ============================================
# CAMPAIGN CONTEXT FEATURES
# ============================================
print("Adding campaign context features...")

# Days since last campaign
days_since_list = []
last_campaign_date = None
for idx, row in df.iterrows():
    if row['has_campaign'] == 1:
        last_campaign_date = row['sale_date']
        days_since_list.append(0)
    else:
        if last_campaign_date is None:
            days_since_list.append(365)
        else:
            days_since_list.append((row['sale_date'] - last_campaign_date).days)
df['days_since_last_campaign'] = days_since_list

# ============================================
# SAVE ENHANCED FEATURES (to root folder)
# ============================================
print(f"\nTotal features now: {len(df.columns)}")
print(f"New features added: 15")

# Save to the root folder (no path, just filename)
df.to_csv('forecasting_features_enhanced.csv', index=False)
print(f"\nSaved: forecasting_features_enhanced.csv (in project root)")

# Preview
print("\nSample of new features (last 10 rows):")
new_feature_cols = ['sale_date', 'days_until_black_friday', 'days_until_christmas', 
                     'is_bf_week', 'is_xmas_2week', 'dow_sin', 'month_sin', 
                     'rolling_std_7day', 'days_since_last_campaign']
print(df[new_feature_cols].tail(10).to_string(index=False))

print("\n" + "="*60)
print("FEATURE ENHANCEMENT COMPLETE")
print("="*60)