# Retail Sales Forecasting & Campaign ROI Analytics

End-to-end analytics pipeline forecasting daily retail revenue across 5 stores and 100 SKUs, with campaign attribution analysis. Achieves 2.95% MAPE on 90-day holdout — 83.4% improvement over naive baseline.

**Live Dashboard:** [Tableau Public](https://public.tableau.com/app/profile/hamza.bashir.butt/viz/RetailForecastingAnalytics/RetailForecastingDashboardRetailForecastingDashboard)

---

## Business Context

Multi-store retail operations require accurate daily revenue forecasts for:
- Inventory allocation (Q4 concentration = 40% of annual revenue in 3 months)
- Staffing decisions (weekend lift = 47.8%)
- Marketing budget allocation (6 of 8 campaign types generate negative incremental revenue)

This project builds a production-grade forecasting pipeline with model interpretability and campaign ROI attribution.

---

## Data

- **Scope:** 100 SKUs, 5 stores, 24 marketing campaigns, 1,096 days (Jan 2023 – Dec 2025)
- **Volume:** 548,000 daily sales records aggregated to 1,096 daily portfolio observations
- **Revenue:** £1.21B total, £11.4M profit
- **Categories:** Electronics (38%), Apparel (30%), Home Goods (18%), Groceries (8%), Seasonal (5%)
- **Stores:** Downtown Flagship, Marina Mall, Suburban Plaza, City Center Express, Airport Outlet

Data is benchmark-grounded synthetic data modeling UK-style multi-store retail operations. Volumes, seasonality patterns, and campaign lift ratios align with published retail industry benchmarks.

---

## Methodology

### 1. Data Generation & Storage
- Python-generated synthetic data with realistic seasonality, weekend effects, campaign lifts, and Q4 concentration
- SQLite database (`retail_analytics.db`) with 4 indexed tables

### 2. SQL Analytics (15 queries)
- Portfolio overview, category performance, store rankings
- Seasonality decomposition, campaign lift analysis, cohort trends
- Feature engineering (lags 1/7/30/365, moving averages, campaign flags)

### 3. Feature Engineering (36 features)
- **Temporal:** day-of-week, month, quarter, cyclical sin/cos encodings
- **Lag features:** revenue_lag_1, lag_7, lag_30, lag_365
- **Rolling statistics:** 7-day and 30-day moving averages and standard deviations
- **Holiday distance:** days_until_black_friday, days_until_christmas, days_until_cyber_monday, days_until_ramadan, days_until_eid
- **Campaign context:** has_campaign, days_since_last_campaign

### 4. Model Comparison (6 models)
Chronological split: 1,006 training days, 90 holdout test days.

| Model | MAPE | RMSE (£) | Improvement vs Baseline |
|-------|------|----------|-------------------------|
| **XGBoost** | **2.95%** | **110,128** | **+83.4%** |
| Random Forest | 3.65% | 191,966 | +79.5% |
| Naive Baseline (lag_365) | 17.81% | 612,218 | — |
| Prophet | 20.53% | 733,109 | -15.3% |
| Moving Average (30-day) | 27.02% | 913,852 | -51.7% |
| Seasonal Naive (lag_7) | 31.87% | 1,250,516 | -78.9% |

### 5. Visualization
- 8-sheet Tableau dashboard with interactive filtering
- EDA diagnostic plots (revenue distribution, ACF/PACF, seasonality)
- Forecast overlay plots (actual vs predicted for all models)

---

## Key Findings

1. **XGBoost achieves 2.95% MAPE** — 83.4% improvement over industry-standard naive baseline
2. **Facebook Prophet placed 4th** at 20.53% MAPE — the industry default underperformed properly-engineered XGBoost on this dataset
3. **7-day moving average dominates predictions** — 36% of XGBoost feature importance
4. **Engineered holiday-distance features rank 2nd and 4th** in importance — validating the choice to replace binary holiday flags with continuous distance features
5. **Peak retail revenue is Dec 21, not Christmas Day** — Christmas Day itself is a revenue trough; retailers who forecast a Dec 25 spike over-order inventory
6. **December delivers 107% revenue lift** over annual baseline — half the year's profit concentrates in 6 weeks
7. **Electronics = 38% of revenue from 20% of SKUs** — inventory should follow revenue concentration, not SKU count
8. **No campaign meaningfully beats baseline** — top-performing campaigns generate under £0.30 of incremental revenue per £1 spent. Standard ROI metrics inflate this by including baseline traffic
---

## Technical Stack

- **Data generation & modeling:** Python 3.14 (pandas, numpy, scikit-learn, xgboost, prophet, statsmodels)
- **Storage:** SQLite via DB Browser
- **Analytics:** SQL (window functions, CTEs, cohort analysis)
- **Visualization:** Tableau Public, matplotlib, seaborn
- **Version control:** GitHub

---

## Repository Structure
retail-forecasting-analytics/
├── data/ # Generated raw data + SQLite DB
├── notebooks/ # Python scripts (generation, features, models, viz)
├── sql/ # 15 analytical SQL queries
├── analysis/ # Model outputs, predictions, feature importance
├── tableau/ # Dashboard file + Tableau-ready CSVs
├── screenshots/ # EDA + forecast visualizations
├── models/ # Serialized model files
├── deliverables/ # Methodology doc, LinkedIn article
└── README.md
---

## Reproducibility

```bash
# 1. Generate data
cd notebooks
python data_generation.py

# 2. Build database
python database_setup.py

# 3. Run SQL analysis (via DB Browser or CLI)
# See sql/analytical_queries.sql

# 4. Enhance features
python enhance_features.py

# 5. EDA
python eda_checks.py

# 6. Train models
python forecasting_models.py

# 7. Prep Tableau data
python prep_tableau_data.py
```

---

## Author

**Hamza Butt** — Data Analyst | RevOps | Fintech Ops  
LinkedIn: [linkedin.com/in/hamzabutt](https://linkedin.com/in/hamzabutt)  
GitHub: [github.com/hamzabutt252525](https://github.com/hamzabutt252525)

**Related portfolio projects:**
- [Sales Team Performance Analytics](https://github.com/hamzabutt252525/sales-team-performance-analytics)
- [Payment Merchant Analytics](https://github.com/hamzabutt252525/payment-merchant-analytics)