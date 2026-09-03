# December 21 Is the Real Christmas Retail Peak — Not December 25

I spent the last week building a retail sales forecasting model on 1,096 days of daily revenue — 5 stores, 100 SKUs, 24 marketing campaigns. Somewhere between the SQL queries and the seventh feature engineering pass, I stopped and stared at the December revenue curve.

One pattern stood out immediately.

**The peak day is December 21. December 25 itself is a trough.**

Revenue climbs steadily from mid-November, spikes on Cyber Monday, drops briefly, then ramps hard from December 13 through December 21. Then it declines for four consecutive days into Christmas Day.

Retailers planning a Christmas Day inventory spike are staffing and stocking for the wrong date. The peak already happened.

Here is what I found and how I built the model that surfaced it.

---

## The Data

- 100 SKUs across 5 categories (Electronics, Apparel, Home Goods, Groceries, Seasonal)
- 5 stores of varying sizes
- 24 marketing campaigns
- 1,096 days (Jan 2023 to Dec 2025)
- £1.21B total revenue
- 548,000 daily sales records aggregated to 1,096 daily portfolio observations

Data is benchmark-grounded synthetic modeling UK-style multi-store retail operations. Volumes, seasonality patterns, and campaign lift ratios are calibrated to published industry benchmarks.

---

## Six Forecasting Models, One Winner

I benchmarked six models on a 90-day holdout (October 3 to December 31, 2025):

| Model | MAPE | Improvement vs Baseline |
|---|---|---|
| **XGBoost** | **2.95%** | **+83.4%** |
| Random Forest | 3.65% | +79.5% |
| Naive Baseline (same day last year) | 17.81% | — |
| Facebook Prophet | 20.53% | -15.3% |
| Moving Average (30-day) | 27.02% | -51.7% |
| Seasonal Naive (same day last week) | 31.87% | -78.9% |

The most surprising result: Facebook Prophet, the industry-default retail forecasting tool, placed 4th. It underperformed a simple same-day-last-year baseline.

I ran the numbers three times to make sure I hadn't misconfigured Prophet. Same result. It handles annual seasonality well but struggles with the sharp, campaign-driven spikes that dominate Q4 retail. XGBoost handles them because I engineered 21 features specifically for retail patterns.

---

## The Feature Engineering That Mattered

Standard time-series models use lag features (revenue 7 days ago, 30 days ago, 365 days ago) and calendar flags (is_december, is_holiday_season).

This compresses too much information. A binary `is_december = 1` treats December 21 the same as December 5. It cannot learn ramp-up patterns.

I replaced binary flags with continuous distance features:

- days_until_black_friday
- days_until_christmas
- days_until_cyber_monday
- days_until_ramadan
- days_until_eid
- days_since_last_campaign

Three of these ranked in the top 5 most important features in the final model. Days-until-Cyber-Monday alone accounted for 12.8% of XGBoost's predictive power.

Full feature importance ranking:

| Rank | Feature | Importance |
|---|---|---|
| 1 | 7-day moving average | 21.8% |
| 2 | Has active campaign | 18.3% |
| 3 | Days until Cyber Monday | 12.8% |
| 4 | Days until Christmas | 8.2% |
| 5 | Days since last campaign | 7.5% |

---

## Six Findings That Change Retail Planning

**1. Weekend lift is uniform across categories.**
All 5 product categories show a 1.46 to 1.50x weekend multiplier. There is no category-specific weekend behavior. A single is_weekend flag suffices.

**2. December delivers 107% revenue lift over baseline.**
Half of the year's profit concentrates in 6 weeks. Q4 planning is not a tactical decision. It is the entire year.

**3. Six of eight campaign categories underperform baseline.**
Only Christmas, Black Friday, and Cyber Monday deliver above-baseline revenue lift. Ramadan, Summer Sale, and New Year campaigns generate negative incremental revenue in this Western retail context. Retailers running all 8 campaign windows are burning budget on the wrong calendar events.

**4. Cyber Monday is the ROI champion.**
£5,329 in revenue per £1 of marketing spend. Black Friday and Christmas follow. Everything else clusters around break-even or worse.

**5. Peak revenue is December 21, not December 25.**
Christmas Day itself is a trough. The peak is the last Sunday before Christmas — the final full shopping weekend before family obligations begin. Retailers forecasting a Christmas Day inventory spike misallocate stock.

**6. Super Saturday matters more than most retailers realize.**
December 13, 2025 (a Saturday, 12 days before Christmas) was a top-3 revenue day. It combines weekend shopping, mid-month payday, and gift-buying urgency.

---

## Business Implications

If you are forecasting retail Q4 revenue or allocating marketing budget:

- **Do not** use binary holiday flags. **Do** use continuous distance-to-holiday features.
- **Do not** default to Prophet as a black box. **Do** engineer domain-specific features that match your business calendar.
- **Do not** plan a Christmas Day inventory spike. **Do** plan for December 21.
- **Do not** spread marketing budget across 8 campaign windows. **Do** concentrate spend in Cyber Monday, Black Friday, and Christmas.

The forecast achieves 2.95% MAPE on a 90-day holdout because the features capture the retail calendar as it actually behaves — not as retailers assume it behaves.

---

## Full Project

**Live Dashboard:** https://public.tableau.com/app/profile/hamza.bashir.butt/viz/RetailForecastingAnalytics/RetailForecastingDashboardRetailForecastingDashboard

**GitHub Repository:** https://github.com/hamzabutt252525/retail-forecasting-analytics

Includes: 15 documented SQL queries, 8-sheet Tableau dashboard, 6-model comparison notebook, EDA diagnostics (autocorrelation, stationarity, distribution), 36-feature engineering pipeline, and a serialized XGBoost model.

---

## About This Portfolio

This is the third of three portfolio projects covering complementary analytics domains:

1. **Sales Team Performance Analytics** — RevOps focus, identified a $5.93M coaching opportunity across a 40-rep B2B sales team using activity-to-outcome funnel analysis
2. **Payment Merchant Analytics** — Fintech + ML focus, quantified £93.5M in retention risk across a UK payment processor's portfolio using a Random Forest churn model (97.9% CV ROC-AUC)
3. **Retail Sales Forecasting & Campaign ROI** — this project

I'm currently exploring Data Analyst, Revenue Operations, and Fintech Operations roles in Dubai, Saudi Arabia, and the UK — happy to talk to hiring managers, recruiters, or anyone building analytics teams in those markets.

If your team is working through demand forecasting or campaign attribution and any of this looks useful, drop me a message. I'd genuinely enjoy walking through the methodology or hearing how you're approaching the same problems.

---

**Hamza Butt**
Data Analyst | RevOps | Fintech Operations