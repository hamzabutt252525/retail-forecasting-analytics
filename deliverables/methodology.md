# Methodology — Retail Sales Forecasting Analytics

## Objective

Build a production-grade daily revenue forecasting pipeline for multi-store retail operations, benchmarked against industry-standard models, with feature interpretability and campaign attribution analysis.

---

## 1. Data Generation

**Approach:** Benchmark-grounded synthetic data modeling UK-style multi-store retail operations.

**Parameters:**
- 100 SKUs across 5 categories (Electronics, Apparel, Home Goods, Groceries, Seasonal)
- 5 stores of varying sizes (Large, Medium, Small)
- 24 marketing campaigns across 3 years
- 1,096 daily observations (Jan 2023 – Dec 2025)

**Realism controls:**
- Category-specific base demand curves
- Store size multipliers (Large 1.5x, Medium 1.0x, Small 0.7x)
- Weekend lift (~1.5x uniform across categories)
- Q4 concentration (December ~2x annual baseline)
- Campaign lifts calibrated per campaign type (Christmas +250%, Black Friday +500%, Ramadan +60% on Groceries)
- Gross margin ~51% (aligned with published retail benchmarks)

---

## 2. Data Storage

- SQLite database via DB Browser
- 4 tables: `products`, `stores`, `campaigns`, `daily_sales`
- 5 indexes on join keys for query performance
- Total DB size: 73 MB (548K sales records + supporting dimensions)

---

## 3. SQL Analysis (15 Queries)

Analytical framework:

| # | Query | Purpose |
|---|-------|---------|
| 1 | Portfolio overview | Baseline KPIs |
| 2 | Category performance | Revenue concentration |
| 3 | Store performance | Location analysis |
| 4 | Monthly trend | Seasonality detection |
| 5 | Day-of-week pattern | Weekly cycle |
| 6 | Seasonality decomposition by category | Q4 sensitivity |
| 7 | Campaign impact vs baseline | Marketing effectiveness |
| 8 | ABC SKU classification | Product concentration |
| 9 | Campaign ROI | Marketing efficiency |
| 10 | Weekend uplift by category | Weekend effect uniformity |
| 11 | Moving averages (7-day, 30-day) | Trend smoothing |
| 12 | Year-over-year comparison | Growth trajectory |
| 13 | Campaign halo effect | Cross-category lift |
| 14 | Store × Category matrix | Consistency check |
| 15 | Forecasting features export | ML input preparation |

---

## 4. Feature Engineering

**36 engineered features grouped by category:**

### Temporal
- `day_of_week`, `is_weekend`, `month`, `quarter`, `year`, `day_of_year`
- Cyclical encoding: `dow_sin`, `dow_cos`, `month_sin`, `month_cos`

### Lag features (autoregressive)
- `revenue_lag_1day`, `revenue_lag_7day`, `revenue_lag_30day`, `revenue_lag_365day`

### Rolling statistics
- `ma_7day`, `ma_30day` (moving averages)
- `rolling_std_7day`, `rolling_std_30day` (volatility)

### Holiday distance (dynamic)
- `days_until_black_friday`
- `days_until_christmas`
- `days_until_cyber_monday`
- `days_until_ramadan`
- `days_until_eid`
- `days_since_black_friday`
- `days_since_christmas`

### Campaign context
- `has_campaign`, `days_since_last_campaign`
- `is_holiday_season`, `is_december`

**Design rationale:** Static binary holiday flags (`is_christmas=1`) compress continuous distance signal into a single day. Continuous distance features (`days_until_christmas`) capture ramp-up patterns 30+ days before the event. This design decision improved XGBoost MAPE from 4.8% (binary flags only) to 2.95% (with distance features).

---

## 5. Exploratory Data Analysis

**Diagnostic tests performed:**

- **Revenue distribution:** Skewness 3.42 (heavily right-skewed due to holiday spikes)
- **Stationarity test:** ADF p-value 0.0048 → series is stationary (no differencing required for ARIMA)
- **Autocorrelation (ACF):** Strong 7-day cycle and 365-day annual cycle detected → validated lag_7 and lag_365 feature choices
- **Weekend effect:** 47.8% lift over weekday average (uniform across categories, not category-specific)
- **December effect:** 107.7% lift over annual baseline

---

## 6. Model Selection

**Chronological split** (no shuffling): 1,006 training days → 90 test days (Oct 3 – Dec 31, 2025)

**Six models compared:**

1. **Naive Baseline (lag_365)** — Same day last year (essential baseline)
2. **Seasonal Naive (lag_7)** — Same day last week
3. **Moving Average (30-day)** — Rolling window baseline
4. **Random Forest** — Tree-based ensemble with 21 features
5. **XGBoost** — Gradient boosting with same 21 features
6. **Facebook Prophet** — Industry-standard time series with UK holidays

**Evaluation metrics:** MAPE, RMSE, MAE

**Model hyperparameters:**
- Random Forest: 300 trees, max_depth=15, min_samples_split=5
- XGBoost: 500 trees, max_depth=8, learning_rate=0.05, subsample=0.8

---

## 7. Results

| Model | MAPE | RMSE (£) | MAE (£) | Improvement vs Baseline |
|-------|------|----------|---------|-------------------------|
| **XGBoost** | **2.95%** | **110,128** | **59,067** | **+83.4%** |
| Random Forest | 3.65% | 191,966 | 81,621 | +79.5% |
| Naive Baseline (lag_365) | 17.81% | 612,218 | 300,729 | — |
| Prophet | 20.53% | 733,109 | 395,636 | -15.3% |
| Moving Average (30-day) | 27.02% | 913,852 | 524,059 | -51.7% |
| Seasonal Naive (lag_7) | 31.87% | 1,250,516 | 621,313 | -78.9% |

**Best model:** XGBoost at 2.95% MAPE — production-grade accuracy for retail forecasting.

---

## 8. Feature Importance (XGBoost)

Top 10 features by importance:

1. `ma_7day` (21.8%)
2. `has_campaign` (18.3%)
3. `days_until_cyber_monday` (12.8%)
4. `days_until_christmas` (8.2%)
5. `days_since_last_campaign` (7.5%)
6. `dow_sin` (5.1%)
7. `day_of_week` (5.0%)
8. `is_weekend` (4.5%)
9. `quarter` (4.1%)
10. `rolling_std_7day` (2.6%)

**Insight:** 3 of the top 5 features are engineered holiday-distance and campaign-context features — validating the feature engineering approach over relying purely on lags and calendar flags.

---

## 9. Business Findings

1. **Peak revenue is Dec 21, not Christmas Day** — Christmas Day itself is a revenue trough
2. **Super Saturday (Dec 13, 2025)** — Saturday 12 days before Christmas — is a top-3 shopping day
3. **No campaign meaningfully beats baseline** — even top campaigns generate under £0.30 of incremental revenue per £1 spent. Standard ROI metrics (gross revenue ÷ spend) hide this by including baseline traffic
4. **Electronics = 38% of revenue from 20% of SKUs** — inventory investment should follow revenue concentration
5. **Downtown Flagship = 30.5% of portfolio** — single-store concentration risk

---

## 10. Limitations & Future Work

**Limitations:**
- Synthetic data — patterns are calibrated to industry benchmarks but not sourced from real operations
- 3-year window limits long-cycle trend detection
- Weekly cross-validation not performed on final models (chronological single-split only)
- Halo effect attribution (campaign spillover across non-targeted categories) uses simplified lift calculation

**Future work:**
- Deploy XGBoost model as REST API for real-time forecasting
- Implement SHAP values for per-day forecast explainability
- Add quantile regression to capture forecast uncertainty bands
- Extend to SKU-level forecasting (currently portfolio-level only)
- Integrate external signals (weather, macroeconomic indicators)

---

## Author

**Hamza Butt** — Data Analyst | RevOps | Fintech Ops