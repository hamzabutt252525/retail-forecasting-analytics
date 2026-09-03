import sqlite3
import pandas as pd

conn = sqlite3.connect('../data/retail_analytics.db')

try:
    result = pd.read_sql("""
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
        ROUND(((cp.campaign_avg_daily - b.baseline_daily) * cp.campaign_days) / NULLIF(cp.marketing_spend_gbp, 0), 1) AS incremental_roi
    FROM campaign_perf cp
    CROSS JOIN baseline b
    ORDER BY incremental_roi DESC
    """, conn)
    
    print(f"SUCCESS: {len(result)} rows")
    print(result.head(10).to_string())
    
except Exception as e:
    print(f"ERROR: {e}")

conn.close()