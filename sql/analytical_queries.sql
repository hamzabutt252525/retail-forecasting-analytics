-- ============================================================
-- RETAIL SALES FORECASTING - ANALYTICAL SQL QUERIES
-- Author: Hamza Butt
-- Database: SQLite (retail_analytics.db)
-- Scope: 100 SKUs, 5 stores, 24 campaigns, 1,096 days (Jan 2023 - Dec 2025)
-- 15 queries: portfolio analysis, seasonality, campaigns, ML feature engineering
-- ============================================================


-- ============================================================
-- Q1: PORTFOLIO OVERVIEW
-- Purpose: Establish baseline KPIs across the full 3-year window
-- Key Findings:
--   - Total revenue: £1.21B across 1,096 days
--   - Total units sold: 16.3M
--   - Gross margin: 51% (aligned with retail industry benchmarks)
--   - Total marketing spend: £769K across 24 campaigns
-- ============================================================
SELECT 
    COUNT(DISTINCT sale_date) AS total_days,
    COUNT(DISTINCT sku_id) AS total_skus,
    COUNT(DISTINCT store_id) AS total_stores,
    SUM(units_sold) AS total_units,
    ROUND(SUM(revenue_gbp), 0) AS total_revenue_gbp,
    ROUND(SUM(gross_profit_gbp), 0) AS total_profit_gbp,
    ROUND(SUM(gross_profit_gbp) * 100.0 / SUM(revenue_gbp), 2) AS gross_margin_pct,
    ROUND(SUM(campaign_spend_allocated), 0) AS total_marketing_spend
FROM daily_sales;


-- ============================================================
-- Q2: CATEGORY PERFORMANCE
-- Purpose: Identify revenue concentration across product categories
-- Key Findings:
--   - Electronics = 38% of revenue from 20 SKUs (20% of catalog)
--   - Apparel = 30% from 30 SKUs
--   - Home Goods = 18% from 20 SKUs
--   - Groceries = 8%, Seasonal = 5% (combined 13% from 30 SKUs)
--   - Inventory investment should follow revenue concentration, not SKU count
-- ============================================================
SELECT 
    p.category,
    COUNT(DISTINCT ds.sku_id) AS sku_count,
    ROUND(SUM(ds.revenue_gbp), 0) AS total_revenue,
    ROUND(SUM(ds.gross_profit_gbp), 0) AS total_profit,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales), 2) AS pct_of_total
FROM daily_sales ds
JOIN products p ON ds.sku_id = p.sku_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- ============================================================
-- Q3: STORE PERFORMANCE
-- Purpose: Analyze revenue distribution across 5 stores by size and location
-- Key Findings:
--   - Downtown Flagship (Large): £369M = 30.5% of portfolio
--   - Marina Mall (Large): £302M = 25%
--   - Suburban Plaza (Medium): £205M = 17%
--   - Airport Outlet (Small): £184M = 15%
--   - City Center Express (Small): £143M = 12%
--   - Store size correlates linearly with revenue; category mix ratios identical across stores
-- ============================================================
SELECT 
    s.store_name,
    s.size AS store_size,
    s.location,
    ROUND(SUM(ds.revenue_gbp), 0) AS total_revenue,
    ROUND(SUM(ds.gross_profit_gbp), 0) AS total_profit,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales), 2) AS pct_of_total
FROM daily_sales ds
JOIN stores s ON ds.store_id = s.store_id
GROUP BY s.store_id
ORDER BY total_revenue DESC;


-- ============================================================
-- Q4: MONTHLY REVENUE TREND
-- Purpose: Detect seasonality patterns across 36 months
-- Key Findings:
--   - Clear Q4 seasonality every year with November-December peaks
--   - December delivers 107.7% revenue lift over annual average
--   - Year-over-year growth plateau visible after 2024
--   - Half the year's profit concentrates in 6 weeks (mid-Nov to end-Dec)
-- ============================================================
SELECT 
    year,
    month,
    ROUND(SUM(revenue_gbp), 0) AS monthly_revenue,
    ROUND(AVG(revenue_gbp), 0) AS avg_daily_revenue,
    SUM(units_sold) AS units_sold
FROM daily_sales
GROUP BY year, month
ORDER BY year, month;


-- ============================================================
-- Q5: DAY-OF-WEEK PATTERN
-- Purpose: Quantify weekly revenue cycle for staffing decisions
-- Key Findings:
--   - Saturday and Sunday each = ~18% of weekly revenue
--   - Friday = 15.8%
--   - Weekdays (Mon-Thu) = 11-12% each
--   - Weekend lift over weekday average: 47.8%
--   - Weekend effect is uniform across all product categories (not category-specific)
-- ============================================================
SELECT 
    day_of_week,
    CASE day_of_week
        WHEN 0 THEN 'Monday' WHEN 1 THEN 'Tuesday' WHEN 2 THEN 'Wednesday'
        WHEN 3 THEN 'Thursday' WHEN 4 THEN 'Friday' WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END AS day_name,
    ROUND(AVG(revenue_gbp), 0) AS avg_daily_revenue,
    ROUND(SUM(revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales), 2) AS pct_of_total_revenue
FROM daily_sales
GROUP BY day_of_week
ORDER BY day_of_week;


-- ============================================================
-- Q6: SEASONALITY DECOMPOSITION BY CATEGORY
-- Purpose: Measure per-category seasonal index (monthly deviation from annual avg)
-- Key Findings:
--   - Seasonal category: December +358% over annual average
--   - Electronics: December +131%, November +63%
--   - Home Goods: December +91%
--   - Apparel: December +81%
--   - Groceries: flat across months (no strong seasonality)
--   - Implication: different forecasting models needed per category
-- ============================================================
WITH category_monthly AS (
    SELECT 
        p.category,
        ds.month,
        AVG(ds.revenue_gbp) AS avg_monthly_revenue
    FROM daily_sales ds
    JOIN products p ON ds.sku_id = p.sku_id
    GROUP BY p.category, ds.month
),
category_annual AS (
    SELECT 
        p.category,
        AVG(ds.revenue_gbp) AS avg_annual_revenue
    FROM daily_sales ds
    JOIN products p ON ds.sku_id = p.sku_id
    GROUP BY p.category
)
SELECT 
    cm.category,
    cm.month,
    ROUND(cm.avg_monthly_revenue, 0) AS monthly_avg,
    ROUND(ca.avg_annual_revenue, 0) AS annual_avg,
    ROUND((cm.avg_monthly_revenue - ca.avg_annual_revenue) * 100.0 / ca.avg_annual_revenue, 1) AS seasonal_index_pct
FROM category_monthly cm
JOIN category_annual ca ON cm.category = ca.category
ORDER BY cm.category, cm.month;


-- ============================================================
-- Q7: CAMPAIGN IMPACT VS BASELINE
-- Purpose: Quantify each campaign's revenue lift vs no-campaign baseline
-- Key Findings:
--   - Cyber Monday: +1076-1294% lift across product categories
--   - Black Friday: +485-555% lift
--   - Christmas: +289-310% lift (targeted at Seasonal +697%, Electronics +242%)
--   - Eid: +125-157% lift
--   - Back to School: +90-104% lift
--   - Ramadan, Summer Sale, New Year: all <40% lift (underperformers in Western retail context)
--   - Note: Query uses IS NULL (not = 'None') for baseline - schema quirk fix
-- ============================================================
WITH baseline AS (
    SELECT AVG(revenue_gbp) AS baseline_revenue
    FROM daily_sales
    WHERE active_campaign IS NULL
)
SELECT 
    ds.active_campaign,
    p.category,
    ROUND(AVG(ds.revenue_gbp), 2) AS avg_during_campaign,
    ROUND(b.baseline_revenue, 2) AS baseline,
    ROUND((AVG(ds.revenue_gbp) - b.baseline_revenue) * 100.0 / b.baseline_revenue, 2) AS lift_pct
FROM daily_sales ds
JOIN products p ON ds.sku_id = p.sku_id
CROSS JOIN baseline b
WHERE ds.active_campaign IS NOT NULL
GROUP BY ds.active_campaign, p.category
ORDER BY ds.active_campaign, lift_pct DESC;


-- ============================================================
-- Q8: SKU ABC CLASSIFICATION
-- Purpose: Rank SKUs by lifetime revenue (classic ABC inventory analysis)
-- Key Findings:
--   - Top 20 SKUs (A-class): Electronics-dominated (12 of top 20)
--   - Top SKU: Smart Phone SKU0045 at £66M lifetime revenue (5.5% of portfolio)
--   - Bottom 20 SKUs (C-class): Groceries-dominated (9 of bottom 20)
--   - Top 20% of SKUs generate 38% of revenue (Pareto pattern confirmed)
-- ============================================================
WITH sku_revenue AS (
    SELECT 
        ds.sku_id,
        p.product_name,
        p.category,
        SUM(ds.revenue_gbp) AS lifetime_revenue,
        SUM(ds.revenue_gbp) * 100.0 / (SELECT SUM(revenue_gbp) FROM daily_sales) AS pct_of_total,
        RANK() OVER (ORDER BY SUM(ds.revenue_gbp) DESC) AS revenue_rank
    FROM daily_sales ds
    JOIN products p ON ds.sku_id = p.sku_id
    GROUP BY ds.sku_id
)
SELECT 
    sku_id, product_name, category,
    ROUND(lifetime_revenue, 0) AS lifetime_revenue,
    ROUND(pct_of_total, 2) AS pct_of_total,
    revenue_rank,
    CASE 
        WHEN revenue_rank <= 20 THEN 'A - Top 20'
        WHEN revenue_rank >= 81 THEN 'C - Bottom 20'
        ELSE 'B - Middle 60'
    END AS abc_class
FROM sku_revenue
WHERE revenue_rank <= 20 OR revenue_rank >= 81
ORDER BY revenue_rank;


-- ============================================================
-- Q9: CAMPAIGN ROI - INCREMENTAL LIFT (REVENUE ABOVE BASELINE)
-- Purpose: Measure true incremental campaign contribution vs baseline
-- Key Findings:
--   - Christmas 2023: highest at £0.30 incremental revenue per £1 spent
--   - New Year Sale 2025: negative ROI (destroys value)
--   - ALL 24 campaigns generate under £0.35 per £1 of incremental revenue
--   - Standard "gross revenue during campaign / spend" metrics inflate ROI 5,000%+
--     because they include baseline traffic that would have occurred anyway
--   - True incremental measurement reveals campaigns barely beat baseline
-- ============================================================
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
    cp.marketing_spend_gbp,
    ROUND(cp.revenue_during, 0) AS revenue_during,
    ROUND((cp.campaign_avg_daily - b.baseline_daily) * cp.campaign_days, 0) AS incremental_revenue,
    ROUND(((cp.campaign_avg_daily - b.baseline_daily) * cp.campaign_days) / NULLIF(cp.marketing_spend_gbp, 0), 2) AS incremental_roi
FROM campaign_perf cp
CROSS JOIN baseline b
ORDER BY incremental_roi DESC;


-- ============================================================
-- Q10: WEEKEND UPLIFT BY CATEGORY
-- Purpose: Test whether weekend effect varies by product category
-- Key Findings:
--   - Uniform 1.46-1.50x weekend multiplier across ALL 5 categories
--   - ~37% of weekly revenue comes from weekends (Sat+Sun combined)
--   - Weekend effect is NOT category-specific (contrary to hypothesis)
--   - Implication: single weekend flag sufficient in ML features; no need for per-category interactions
-- ============================================================
SELECT 
    p.category,
    ROUND(AVG(CASE WHEN ds.is_weekend = 0 THEN ds.revenue_gbp END), 0) AS avg_weekday,
    ROUND(AVG(CASE WHEN ds.is_weekend = 1 THEN ds.revenue_gbp END), 0) AS avg_weekend,
    ROUND(AVG(CASE WHEN ds.is_weekend = 1 THEN ds.revenue_gbp END) 
        / AVG(CASE WHEN ds.is_weekend = 0 THEN ds.revenue_gbp END), 2) AS weekend_multiplier
FROM daily_sales ds
JOIN products p ON ds.sku_id = p.sku_id
GROUP BY p.category
ORDER BY weekend_multiplier DESC;


-- ============================================================
-- Q11: MOVING AVERAGES (7-DAY, 30-DAY) WITH DEVIATION
-- Purpose: Smooth revenue signal and detect anomalous days
-- Key Findings:
--   - 7-day moving average captures weekly cycle
--   - 30-day moving average captures underlying trend
--   - Christmas peak days show +1.4M to +3.4M deviation from 30-day average
--   - Weekend deviations: +200-500K above 30-day average
--   - ma_7day becomes the strongest single feature in XGBoost (36% importance)
-- ============================================================
SELECT 
    sale_date,
    ROUND(SUM(revenue_gbp), 2) AS total_revenue,
    ROUND(AVG(SUM(revenue_gbp)) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 0) AS ma_7day,
    ROUND(AVG(SUM(revenue_gbp)) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 0) AS ma_30day,
    ROUND(SUM(revenue_gbp) - AVG(SUM(revenue_gbp)) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 0) AS deviation_from_30day_avg
FROM daily_sales
GROUP BY sale_date
ORDER BY sale_date;


-- ============================================================
-- Q12: YEAR-OVER-YEAR MONTHLY GROWTH
-- Purpose: Measure YoY revenue growth per month
-- Key Findings:
--   - 2024 vs 2023: revenue growth visible across most months
--   - 2025 vs 2024: growth plateaus, indicating market maturity
--   - Q4 months (Nov, Dec) show strongest YoY consistency
--   - LAG window function used for YoY comparison
-- ============================================================
WITH monthly AS (
    SELECT 
        year, month,
        SUM(revenue_gbp) AS monthly_revenue
    FROM daily_sales
    GROUP BY year, month
)
SELECT 
    year, month, monthly_revenue,
    LAG(monthly_revenue, 12) OVER (ORDER BY year, month) AS prev_year_revenue,
    ROUND((monthly_revenue - LAG(monthly_revenue, 12) OVER (ORDER BY year, month)) 
        * 100.0 / LAG(monthly_revenue, 12) OVER (ORDER BY year, month), 1) AS yoy_growth_pct
FROM monthly
ORDER BY year, month;


-- ============================================================
-- Q13: CAMPAIGN HALO EFFECT (CROSS-CATEGORY LIFT)
-- Purpose: Detect whether campaigns lift non-targeted categories (halo)
-- Key Findings:
--   - Christmas lifts Seasonal +697% (targeted), Electronics +242% (halo)
--   - Christmas has NEAR-ZERO lift on Groceries (-2% to +1%) - no cross-category spillover
--   - Black Friday lifts Electronics +661% (targeted), Home Goods +407% (halo)
--   - Ramadan targets Groceries (+64-82%), has NEGATIVE lift on Electronics
--   - Campaign category-fit determines lift magnitude; misaligned campaigns waste budget
-- ============================================================
WITH baseline AS (
    SELECT p.category, AVG(ds.revenue_gbp) AS baseline_rev
    FROM daily_sales ds
    JOIN products p ON ds.sku_id = p.sku_id
    WHERE ds.active_campaign IS NULL
    GROUP BY p.category
),
campaign_perf AS (
    SELECT 
        ds.active_campaign,
        p.category,
        AVG(ds.revenue_gbp) AS campaign_rev
    FROM daily_sales ds
    JOIN products p ON ds.sku_id = p.sku_id
    WHERE ds.active_campaign IS NOT NULL
    GROUP BY ds.active_campaign, p.category
)
SELECT 
    cp.active_campaign,
    cp.category,
    ROUND(cp.campaign_rev, 2) AS avg_during_campaign,
    ROUND(b.baseline_rev, 2) AS baseline,
    ROUND((cp.campaign_rev - b.baseline_rev) * 100.0 / b.baseline_rev, 2) AS lift_pct
FROM campaign_perf cp
JOIN baseline b ON cp.category = b.category
ORDER BY cp.active_campaign, lift_pct DESC;


-- ============================================================
-- Q14: STORE x CATEGORY MATRIX
-- Purpose: Cross-tabulate revenue per store per category (5x5 matrix)
-- Key Findings:
--   - Category mix ratios are IDENTICAL across all 5 stores
--   - Downtown Flagship dominates every category (rank #1 across all)
--   - City Center Express ranks #5 in every category
--   - Store performance is scale-driven, not mix-driven
--   - Implication: store expansion should replicate the same category mix
-- ============================================================
SELECT 
    s.store_name,
    p.category,
    ROUND(SUM(ds.revenue_gbp), 0) AS total_revenue,
    ROUND(SUM(ds.gross_profit_gbp), 0) AS total_profit,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / SUM(SUM(ds.revenue_gbp)) OVER (PARTITION BY s.store_id), 2) AS pct_of_store_revenue,
    ROUND(SUM(ds.revenue_gbp) * 100.0 / SUM(SUM(ds.revenue_gbp)) OVER (PARTITION BY p.category), 2) AS pct_of_category_revenue,
    RANK() OVER (PARTITION BY p.category ORDER BY SUM(ds.revenue_gbp) DESC) AS store_rank_within_category
FROM daily_sales ds
JOIN stores s ON ds.store_id = s.store_id
JOIN products p ON ds.sku_id = p.sku_id
GROUP BY s.store_id, p.category
ORDER BY p.category, store_rank_within_category;


-- ============================================================
-- Q15: FORECASTING FEATURES TABLE (ML INPUT)
-- Purpose: Aggregate daily sales into ML-ready feature table with lags and moving averages
-- Key Findings:
--   - 1,096 daily rows output (matches 3-year date range exactly)
--   - Lag features (1, 7, 30, 365 days) capture short/medium/long temporal patterns
--   - 7-day moving average smooths weekly cycle
--   - 30-day moving average captures monthly trend
--   - Output is base input for XGBoost achieving 2.95% MAPE on 90-day holdout
--   - Feature engineering enhanced downstream with days_until_holiday features
-- ============================================================
WITH daily_agg AS (
    SELECT 
        sale_date,
        CAST(strftime('%Y', sale_date) AS INTEGER) AS year,
        CAST(strftime('%m', sale_date) AS INTEGER) AS month,
        CAST((CAST(strftime('%m', sale_date) AS INTEGER) - 1) / 3 + 1 AS INTEGER) AS quarter,
        CAST(strftime('%w', sale_date) AS INTEGER) AS day_of_week,
        CASE WHEN CAST(strftime('%w', sale_date) AS INTEGER) IN (0, 6) THEN 1 ELSE 0 END AS is_weekend,
        SUM(units_sold) AS units_sold,
        ROUND(SUM(revenue_gbp), 2) AS total_revenue,
        ROUND(SUM(gross_profit_gbp), 2) AS total_profit,
        ROUND(SUM(campaign_spend_allocated), 2) AS marketing_spend,
        CASE WHEN MAX(CASE WHEN active_campaign IS NOT NULL THEN 1 ELSE 0 END) = 1 THEN 1 ELSE 0 END AS has_campaign
    FROM daily_sales
    GROUP BY sale_date
)
SELECT 
    sale_date, year, month, quarter, day_of_week, is_weekend,
    units_sold, total_revenue, total_profit, marketing_spend,
    LAG(total_revenue, 1) OVER (ORDER BY sale_date) AS revenue_lag_1day,
    LAG(total_revenue, 7) OVER (ORDER BY sale_date) AS revenue_lag_7day,
    LAG(total_revenue, 30) OVER (ORDER BY sale_date) AS revenue_lag_30day,
    LAG(total_revenue, 365) OVER (ORDER BY sale_date) AS revenue_lag_365day,
    ROUND(AVG(total_revenue) OVER (ORDER BY sale_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0) AS ma_7day,
    ROUND(AVG(total_revenue) OVER (ORDER BY sale_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 0) AS ma_30day,
    has_campaign,
    CASE WHEN month IN (11, 12) THEN 1 ELSE 0 END AS is_holiday_season,
    CASE WHEN month = 12 THEN 1 ELSE 0 END AS is_december
FROM daily_agg
ORDER BY sale_date;


-- ============================================================
-- END OF ANALYTICAL QUERIES
-- ============================================================