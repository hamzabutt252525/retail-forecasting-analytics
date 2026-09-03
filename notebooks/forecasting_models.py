"""
RETAIL SALES FORECASTING - MODEL COMPARISON
Builds and compares 6 forecasting models on 90-day holdout.
Metrics: MAPE, RMSE, MAE
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import joblib
import os

os.makedirs('../models', exist_ok=True)

print("="*60)
print("RETAIL SALES FORECASTING - MODEL COMPARISON")
print("="*60)

# Load enhanced features
df = pd.read_csv('../analysis/forecasting_features_enhanced.csv')
df['sale_date'] = pd.to_datetime(df['sale_date'])
df = df.sort_values('sale_date').reset_index(drop=True)

print(f"Loaded {len(df)} daily records with {len(df.columns)} features")
print(f"Date range: {df['sale_date'].min().date()} to {df['sale_date'].max().date()}")

# Chronological split - last 90 days for test
TEST_DAYS = 90
train = df.iloc[:-TEST_DAYS].copy()
test = df.iloc[-TEST_DAYS:].copy()

print(f"\nTrain: {len(train)} days ({train['sale_date'].min().date()} to {train['sale_date'].max().date()})")
print(f"Test:  {len(test)} days ({test['sale_date'].min().date()} to {test['sale_date'].max().date()})")

# Evaluation function
def evaluate(actual, predicted, model_name):
    actual = np.array(actual)
    predicted = np.array(predicted)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mae = np.mean(np.abs(actual - predicted))
    print(f"\n{model_name}:")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  RMSE: {rmse:,.0f}")
    print(f"  MAE:  {mae:,.0f}")
    return {'model': model_name, 'MAPE': round(mape, 2), 'RMSE': round(rmse, 0), 'MAE': round(mae, 0)}

results = []
predictions_df = test[['sale_date', 'total_revenue']].copy()
predictions_df.columns = ['sale_date', 'actual']

# ============================================
# MODEL 1: NAIVE BASELINE (Same Day Last Year)
# ============================================
print("\n" + "="*60)
print("MODEL 1: NAIVE BASELINE (lag_365 - same day last year)")
print("="*60)

lag365_predictions = test['revenue_lag_365day'].values
# Handle any NaN by falling back to lag_30
lag365_predictions = np.where(np.isnan(lag365_predictions), 
                               test['revenue_lag_30day'].values, 
                               lag365_predictions)

results.append(evaluate(test['total_revenue'].values, lag365_predictions, 'Naive Baseline (lag_365)'))
predictions_df['naive_baseline'] = lag365_predictions

# ============================================
# MODEL 2: SEASONAL NAIVE (Same Day Last Week)
# ============================================
print("\n" + "="*60)
print("MODEL 2: SEASONAL NAIVE (lag_7 - same day last week)")
print("="*60)

lag7_predictions = test['revenue_lag_7day'].values
lag7_predictions = np.where(np.isnan(lag7_predictions), 
                             test['revenue_lag_1day'].values, 
                             lag7_predictions)

results.append(evaluate(test['total_revenue'].values, lag7_predictions, 'Seasonal Naive (lag_7)'))
predictions_df['seasonal_naive'] = lag7_predictions

# ============================================
# MODEL 3: MOVING AVERAGE (30-day)
# ============================================
print("\n" + "="*60)
print("MODEL 3: MOVING AVERAGE (30-day rolling)")
print("="*60)

ma_predictions = test['ma_30day'].values
results.append(evaluate(test['total_revenue'].values, ma_predictions, 'Moving Average (30-day)'))
predictions_df['moving_avg'] = ma_predictions

# ============================================
# MODEL 4: RANDOM FOREST
# ============================================
print("\n" + "="*60)
print("MODEL 4: RANDOM FOREST with engineered features")
print("="*60)

from sklearn.ensemble import RandomForestRegressor

feature_cols = [
    'month', 'day_of_week', 'is_weekend', 'quarter', 
    'has_campaign', 'is_holiday_season', 'is_december',
    'days_until_black_friday', 'days_until_christmas', 
    'days_until_ramadan', 'days_until_eid', 'days_until_cyber_monday',
    'dow_sin', 'dow_cos', 'month_sin', 'month_cos',
    'ma_7day', 'ma_30day', 'rolling_std_7day', 'rolling_std_30day',
    'days_since_last_campaign'
]

# Only use features that exist
feature_cols = [c for c in feature_cols if c in df.columns]
print(f"Using {len(feature_cols)} features")

train_rf = train.dropna(subset=feature_cols + ['total_revenue']).copy()
X_train = train_rf[feature_cols]
y_train = train_rf['total_revenue']
X_test = test[feature_cols].copy()

# Fill any test NaN with train medians
for col in feature_cols:
    if X_test[col].isna().any():
        X_test[col] = X_test[col].fillna(X_train[col].median())

rf_model = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)
rf_predictions = rf_model.predict(X_test)

results.append(evaluate(test['total_revenue'].values, rf_predictions, 'Random Forest'))
predictions_df['random_forest'] = rf_predictions

# Feature importance
print("\nRandom Forest Feature Importance (Top 10):")
importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)
print(importance_df.head(10).to_string(index=False))

# ============================================
# MODEL 5: XGBOOST
# ============================================
print("\n" + "="*60)
print("MODEL 5: XGBOOST")
print("="*60)

try:
    from xgboost import XGBRegressor
    
    xgb_model = XGBRegressor(
        n_estimators=500,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    
    xgb_model.fit(X_train, y_train)
    xgb_predictions = xgb_model.predict(X_test)
    
    results.append(evaluate(test['total_revenue'].values, xgb_predictions, 'XGBoost'))
    predictions_df['xgboost'] = xgb_predictions
    
    xgb_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': xgb_model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nXGBoost Feature Importance (Top 10):")
    print(xgb_importance.head(10).to_string(index=False))
    
except ImportError:
    print("XGBoost not installed. Skipping. Install with: pip install xgboost --break-system-packages")
    predictions_df['xgboost'] = None
    xgb_model = None

# ============================================
# MODEL 6: PROPHET
# ============================================
print("\n" + "="*60)
print("MODEL 6: FACEBOOK PROPHET")
print("="*60)

try:
    from prophet import Prophet
    
    prophet_train = train[['sale_date', 'total_revenue']].copy()
    prophet_train.columns = ['ds', 'y']
    
    prophet_model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05
    )
    
    # Add UK holidays
    prophet_model.add_country_holidays(country_name='UK')
    prophet_model.fit(prophet_train)
    
    future = pd.DataFrame({'ds': test['sale_date'].values})
    prophet_forecast = prophet_model.predict(future)
    prophet_predictions = prophet_forecast['yhat'].values
    
    results.append(evaluate(test['total_revenue'].values, prophet_predictions, 'Prophet'))
    predictions_df['prophet'] = prophet_predictions
    
except Exception as e:
    print(f"Prophet failed: {e}")
    predictions_df['prophet'] = None

# ============================================
# FINAL COMPARISON
# ============================================
print("\n" + "="*60)
print("FINAL MODEL COMPARISON (Lower is Better)")
print("="*60)

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('MAPE')

# Add improvement over baseline
baseline_mape = results_df[results_df['model'] == 'Naive Baseline (lag_365)']['MAPE'].values[0]
results_df['improvement_vs_baseline'] = ((baseline_mape - results_df['MAPE']) / baseline_mape * 100).round(1)
results_df['improvement_vs_baseline'] = results_df['improvement_vs_baseline'].astype(str) + '%'

print("\n" + results_df.to_string(index=False))

best_model = results_df.iloc[0]
print(f"\nBEST MODEL: {best_model['model']}")
print(f"  MAPE: {best_model['MAPE']}%")
print(f"  RMSE: {best_model['RMSE']:,.0f}")
print(f"  Improvement over naive baseline: {best_model['improvement_vs_baseline']}")

# ============================================
# SAVE OUTPUTS
# ============================================
os.makedirs('../analysis', exist_ok=True)

results_df.to_csv('../analysis/model_comparison.csv', index=False)
predictions_df.to_csv('../analysis/forecast_predictions.csv', index=False)
importance_df.to_csv('../analysis/rf_feature_importance.csv', index=False)

# Save best model
if best_model['model'] == 'Random Forest':
    joblib.dump(rf_model, '../models/forecast_model_random_forest.pkl')
    print("\nSaved: models/forecast_model_random_forest.pkl")
elif best_model['model'] == 'XGBoost' and xgb_model is not None:
    joblib.dump(xgb_model, '../models/forecast_model_xgboost.pkl')
    print("\nSaved: models/forecast_model_xgboost.pkl")

print("\n" + "="*60)
print("PHASE 3 COMPLETE")
print("="*60)
print("Files saved to analysis/:")
print("  model_comparison.csv")
print("  forecast_predictions.csv")
print("  rf_feature_importance.csv")