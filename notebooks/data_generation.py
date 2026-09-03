"""
RETAIL SALES FORECASTING WITH MARKETING CAMPAIGN IMPACT
Data Generation Script
Author: Hamza Butt

Generates realistic retail sales data with marketing campaign events:
- 100 SKUs across 5 categories
- 5 store locations
- 36 months of daily data (Jan 2023 - Dec 2025)
- Marketing campaigns embedded (Ramadan, Black Friday, Back-to-School, etc.)
- Weather and external variables
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

# =====================================
# CONFIGURATION
# =====================================
np.random.seed(42)
random.seed(42)
fake = Faker('en_US')
Faker.seed(42)

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days + 1  # 1096 days

# Portfolio config
NUM_SKUS = 100
NUM_STORES = 5

# Product categories with characteristics
CATEGORIES = {
    'Apparel': {
        'sku_count': 30,
        'base_daily_sales': 25,      # avg units per store per day
        'price_range': (25, 150),
        'seasonality': 'moderate',   # Q4 spike, summer dip
        'campaign_lift': 1.8,        # 80% lift during campaigns
        'weather_sensitive': True
    },
    'Electronics': {
        'sku_count': 20,
        'base_daily_sales': 8,
        'price_range': (100, 800),
        'seasonality': 'strong',     # Massive Q4, Black Friday
        'campaign_lift': 2.2,
        'weather_sensitive': False
    },
    'Home Goods': {
        'sku_count': 20,
        'base_daily_sales': 12,
        'price_range': (30, 250),
        'seasonality': 'moderate',
        'campaign_lift': 1.5,
        'weather_sensitive': False
    },
    'Groceries': {
        'sku_count': 20,
        'base_daily_sales': 60,
        'price_range': (3, 25),
        'seasonality': 'weak',       # Consistent daily demand
        'campaign_lift': 1.2,
        'weather_sensitive': True
    },
    'Seasonal': {
        'sku_count': 10,
        'base_daily_sales': 15,
        'price_range': (20, 100),
        'seasonality': 'extreme',    # Christmas, Halloween, Easter driven
        'campaign_lift': 2.5,
        'weather_sensitive': True
    }
}

# Store locations
STORES = [
    {'store_id': 'ST001', 'store_name': 'Downtown Flagship', 'location': 'Urban', 'size': 'Large', 'volume_multiplier': 1.8},
    {'store_id': 'ST002', 'store_name': 'Marina Mall', 'location': 'Mall', 'size': 'Large', 'volume_multiplier': 1.5},
    {'store_id': 'ST003', 'store_name': 'Suburban Plaza', 'location': 'Suburban', 'size': 'Medium', 'volume_multiplier': 1.0},
    {'store_id': 'ST004', 'store_name': 'City Center Express', 'location': 'Urban', 'size': 'Small', 'volume_multiplier': 0.7},
    {'store_id': 'ST005', 'store_name': 'Airport Outlet', 'location': 'Airport', 'size': 'Small', 'volume_multiplier': 0.9}
]

# Marketing campaigns (real-world retail calendar)
CAMPAIGNS = [
    # 2023
    {'name': 'New Year Sale 2023', 'start': '2023-01-01', 'end': '2023-01-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.2, 'marketing_spend': 45000},
    {'name': 'Ramadan Season 2023', 'start': '2023-03-22', 'end': '2023-04-21', 'categories': ['Groceries', 'Apparel', 'Home Goods'], 'intensity': 1.6, 'marketing_spend': 85000},
    {'name': 'Eid Al-Fitr 2023', 'start': '2023-04-21', 'end': '2023-04-28', 'categories': ['Apparel', 'Electronics', 'Groceries'], 'intensity': 2.0, 'marketing_spend': 120000},
    {'name': 'Summer Sale 2023', 'start': '2023-06-15', 'end': '2023-07-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.4, 'marketing_spend': 65000},
    {'name': 'Back to School 2023', 'start': '2023-08-15', 'end': '2023-09-10', 'categories': ['Apparel', 'Electronics'], 'intensity': 1.5, 'marketing_spend': 70000},
    {'name': 'Black Friday 2023', 'start': '2023-11-24', 'end': '2023-11-27', 'categories': ['Electronics', 'Apparel', 'Home Goods'], 'intensity': 3.0, 'marketing_spend': 200000},
    {'name': 'Cyber Monday 2023', 'start': '2023-11-27', 'end': '2023-11-28', 'categories': ['Electronics'], 'intensity': 2.5, 'marketing_spend': 100000},
    {'name': 'Christmas 2023', 'start': '2023-12-10', 'end': '2023-12-25', 'categories': ['Apparel', 'Electronics', 'Seasonal', 'Home Goods'], 'intensity': 2.2, 'marketing_spend': 180000},
    
    # 2024
    {'name': 'New Year Sale 2024', 'start': '2024-01-01', 'end': '2024-01-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.3, 'marketing_spend': 50000},
    {'name': 'Ramadan Season 2024', 'start': '2024-03-11', 'end': '2024-04-10', 'categories': ['Groceries', 'Apparel', 'Home Goods'], 'intensity': 1.7, 'marketing_spend': 95000},
    {'name': 'Eid Al-Fitr 2024', 'start': '2024-04-10', 'end': '2024-04-17', 'categories': ['Apparel', 'Electronics', 'Groceries'], 'intensity': 2.1, 'marketing_spend': 130000},
    {'name': 'Summer Sale 2024', 'start': '2024-06-15', 'end': '2024-07-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.5, 'marketing_spend': 75000},
    {'name': 'Back to School 2024', 'start': '2024-08-15', 'end': '2024-09-10', 'categories': ['Apparel', 'Electronics'], 'intensity': 1.6, 'marketing_spend': 80000},
    {'name': 'Black Friday 2024', 'start': '2024-11-29', 'end': '2024-12-02', 'categories': ['Electronics', 'Apparel', 'Home Goods'], 'intensity': 3.2, 'marketing_spend': 220000},
    {'name': 'Cyber Monday 2024', 'start': '2024-12-02', 'end': '2024-12-03', 'categories': ['Electronics'], 'intensity': 2.6, 'marketing_spend': 110000},
    {'name': 'Christmas 2024', 'start': '2024-12-10', 'end': '2024-12-25', 'categories': ['Apparel', 'Electronics', 'Seasonal', 'Home Goods'], 'intensity': 2.3, 'marketing_spend': 195000},
    
    # 2025
    {'name': 'New Year Sale 2025', 'start': '2025-01-01', 'end': '2025-01-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.3, 'marketing_spend': 55000},
    {'name': 'Ramadan Season 2025', 'start': '2025-02-28', 'end': '2025-03-30', 'categories': ['Groceries', 'Apparel', 'Home Goods'], 'intensity': 1.7, 'marketing_spend': 100000},
    {'name': 'Eid Al-Fitr 2025', 'start': '2025-03-30', 'end': '2025-04-06', 'categories': ['Apparel', 'Electronics', 'Groceries'], 'intensity': 2.2, 'marketing_spend': 135000},
    {'name': 'Summer Sale 2025', 'start': '2025-06-15', 'end': '2025-07-15', 'categories': ['Apparel', 'Home Goods'], 'intensity': 1.5, 'marketing_spend': 80000},
    {'name': 'Back to School 2025', 'start': '2025-08-15', 'end': '2025-09-10', 'categories': ['Apparel', 'Electronics'], 'intensity': 1.6, 'marketing_spend': 85000},
    {'name': 'Black Friday 2025', 'start': '2025-11-28', 'end': '2025-12-01', 'categories': ['Electronics', 'Apparel', 'Home Goods'], 'intensity': 3.3, 'marketing_spend': 230000},
    {'name': 'Cyber Monday 2025', 'start': '2025-12-01', 'end': '2025-12-02', 'categories': ['Electronics'], 'intensity': 2.7, 'marketing_spend': 115000},
    {'name': 'Christmas 2025', 'start': '2025-12-10', 'end': '2025-12-25', 'categories': ['Apparel', 'Electronics', 'Seasonal', 'Home Goods'], 'intensity': 2.4, 'marketing_spend': 210000},
]

# =====================================
# TABLE 1: PRODUCTS (SKUs)
# =====================================
print("="*60)
print("GENERATING RETAIL FORECASTING DATASET")
print("="*60)
print("\nGenerating products table...")

products_data = []
sku_counter = 1

for category, config in CATEGORIES.items():
    for i in range(config['sku_count']):
        sku_id = f"SKU{str(sku_counter).zfill(4)}"
        price = round(np.random.uniform(config['price_range'][0], config['price_range'][1]), 2)
        cost = round(price * np.random.uniform(0.4, 0.6), 2)  # 40-60% margin
        
        if category == 'Apparel':
            name = f"{fake.color_name()} {random.choice(['Shirt', 'Dress', 'Jacket', 'Pants', 'Shoes'])}"
        elif category == 'Electronics':
            name = f"{random.choice(['Ultra', 'Pro', 'Smart', 'Elite'])} {random.choice(['Phone', 'Tablet', 'Laptop', 'Headphones', 'Speaker'])}"
        elif category == 'Home Goods':
            name = f"{random.choice(['Modern', 'Classic', 'Rustic'])} {random.choice(['Chair', 'Lamp', 'Cushion', 'Vase', 'Rug'])}"
        elif category == 'Groceries':
            name = f"{random.choice(['Organic', 'Premium', 'Fresh'])} {random.choice(['Coffee', 'Tea', 'Cereal', 'Snacks', 'Beverages'])}"
        else:  # Seasonal
            name = f"{random.choice(['Holiday', 'Festive', 'Seasonal'])} {random.choice(['Decor', 'Gift Set', 'Ornament', 'Wreath', 'Lights'])}"
        
        products_data.append({
            'sku_id': sku_id,
            'product_name': name,
            'category': category,
            'unit_price': price,
            'unit_cost': cost,
            'margin_pct': round((price - cost) / price * 100, 2)
        })
        sku_counter += 1

products_df = pd.DataFrame(products_data)
print(f"  Created {len(products_df)} products across {len(CATEGORIES)} categories")

# =====================================
# TABLE 2: STORES
# =====================================
print("\nGenerating stores table...")
stores_df = pd.DataFrame(STORES)
print(f"  Created {len(stores_df)} stores")

# =====================================
# TABLE 3: CAMPAIGNS
# =====================================
print("\nGenerating campaigns table...")
campaigns_data = []
for i, camp in enumerate(CAMPAIGNS, 1):
    campaigns_data.append({
        'campaign_id': f"CAMP{str(i).zfill(3)}",
        'campaign_name': camp['name'],
        'start_date': camp['start'],
        'end_date': camp['end'],
        'target_categories': ', '.join(camp['categories']),
        'marketing_spend_gbp': camp['marketing_spend'],
        'intensity_multiplier': camp['intensity']
    })
campaigns_df = pd.DataFrame(campaigns_data)
print(f"  Created {len(campaigns_df)} marketing campaigns")

# =====================================
# TABLE 4: DAILY SALES (THE BIG ONE)
# =====================================
print("\nGenerating daily sales table (this takes 2-4 minutes)...")

# Build campaign lookup for fast checking
campaign_lookup = {}
for camp in CAMPAIGNS:
    start = datetime.strptime(camp['start'], '%Y-%m-%d')
    end = datetime.strptime(camp['end'], '%Y-%m-%d')
    current = start
    while current <= end:
        date_str = current.strftime('%Y-%m-%d')
        if date_str not in campaign_lookup:
            campaign_lookup[date_str] = []
        campaign_lookup[date_str].append(camp)
        current += timedelta(days=1)

sales_data = []

for sku_row in products_df.itertuples():
    category = sku_row.category
    config = CATEGORIES[category]
    base_price = sku_row.unit_price
    base_daily = config['base_daily_sales']
    
    # Per-SKU variation (some SKUs are bestsellers, others slow movers)
    sku_popularity = np.random.beta(2, 5)  # skewed distribution
    sku_multiplier = 0.3 + sku_popularity * 1.7  # range: 0.3 to 2.0
    
    for store_row in stores_df.itertuples():
        store_id = store_row.store_id
        store_mult = store_row.volume_multiplier
        
        # Iterate through all days
        current_date = START_DATE
        while current_date <= END_DATE:
            date_str = current_date.strftime('%Y-%m-%d')
            day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
            month = current_date.month
            
            # Base sales calculation
            base_units = base_daily * sku_multiplier * store_mult
            
            # Day of week effect (weekend boost)
            if day_of_week in [5, 6]:  # Sat, Sun
                dow_mult = 1.4
            elif day_of_week == 4:  # Friday
                dow_mult = 1.2
            else:
                dow_mult = 0.9
            
            # Seasonality effect by category
            season_mult = 1.0
            if config['seasonality'] == 'strong':
                # Electronics: massive Q4
                if month in [11, 12]:
                    season_mult = 1.6
                elif month in [1, 2]:
                    season_mult = 0.8
            elif config['seasonality'] == 'moderate':
                # Apparel/Home: Q4 boost, summer dip
                if month in [11, 12]:
                    season_mult = 1.4
                elif month in [7, 8]:
                    season_mult = 0.9
            elif config['seasonality'] == 'extreme':
                # Seasonal: Christmas peak, dead most of year
                if month == 12:
                    season_mult = 3.5
                elif month in [10, 11]:
                    season_mult = 1.8
                elif month in [3, 4]:  # Easter
                    season_mult = 1.5
                else:
                    season_mult = 0.4
            elif config['seasonality'] == 'weak':
                # Groceries: consistent
                season_mult = 1.0 + np.random.uniform(-0.05, 0.05)
            
            # Campaign effect
            campaign_mult = 1.0
            active_campaign = None
            campaign_spend_share = 0
            
            if date_str in campaign_lookup:
                for camp in campaign_lookup[date_str]:
                    if category in camp['categories']:
                        campaign_mult *= camp['intensity']
                        active_campaign = camp['name']
                        # Allocate a share of marketing spend to this SKU-store-day
                        campaign_spend_share = camp['marketing_spend'] / (len(camp['categories']) * NUM_STORES * (datetime.strptime(camp['end'], '%Y-%m-%d') - datetime.strptime(camp['start'], '%Y-%m-%d')).days) / NUM_SKUS
            
            # Weather effect (simplified - random shock on some days)
            weather_mult = 1.0
            if config['weather_sensitive']:
                if np.random.random() < 0.05:  # 5% of days have weather event
                    weather_mult = np.random.uniform(0.6, 0.85)  # bad weather reduces sales
            
            # Random noise
            noise = np.random.normal(1.0, 0.15)
            noise = max(0.5, min(1.5, noise))  # cap noise
            
            # Calculate final units sold
            units_sold = base_units * dow_mult * season_mult * campaign_mult * weather_mult * noise
            units_sold = max(0, int(round(units_sold)))
            
            # Revenue and cost
            revenue = units_sold * base_price
            cost = units_sold * sku_row.unit_cost
            gross_profit = revenue - cost
            
            # Sometimes zero sales (stockout, no demand)
            if np.random.random() < 0.02:  # 2% chance
                units_sold = 0
                revenue = 0
                cost = 0
                gross_profit = 0
            
            sales_data.append({
                'sale_date': date_str,
                'sku_id': sku_row.sku_id,
                'store_id': store_id,
                'units_sold': units_sold,
                'revenue_gbp': round(revenue, 2),
                'cost_gbp': round(cost, 2),
                'gross_profit_gbp': round(gross_profit, 2),
                'active_campaign': active_campaign if active_campaign else 'None',
                'campaign_spend_allocated': round(campaign_spend_share, 2) if active_campaign else 0,
                'is_weekend': 1 if day_of_week in [5, 6] else 0,
                'day_of_week': day_of_week,
                'month': month,
                'year': current_date.year,
                'quarter': (month - 1) // 3 + 1
            })
            
            current_date += timedelta(days=1)

daily_sales_df = pd.DataFrame(sales_data)
print(f"  Created {len(daily_sales_df):,} daily sales records")

# =====================================
# TABLE 5: DAILY AGGREGATE SUMMARY (pre-aggregated for Tableau)
# =====================================
print("\nGenerating daily aggregate summary...")

daily_summary = daily_sales_df.groupby(['sale_date']).agg(
    total_units_sold=('units_sold', 'sum'),
    total_revenue=('revenue_gbp', 'sum'),
    total_cost=('cost_gbp', 'sum'),
    total_gross_profit=('gross_profit_gbp', 'sum'),
    total_marketing_spend=('campaign_spend_allocated', 'sum'),
    active_skus=('sku_id', 'nunique'),
    active_stores=('store_id', 'nunique')
).reset_index()

daily_summary['sale_date_dt'] = pd.to_datetime(daily_summary['sale_date'])
daily_summary['day_of_week'] = daily_summary['sale_date_dt'].dt.dayofweek
daily_summary['month'] = daily_summary['sale_date_dt'].dt.month
daily_summary['year'] = daily_summary['sale_date_dt'].dt.year
daily_summary['quarter'] = daily_summary['sale_date_dt'].dt.quarter
daily_summary['is_weekend'] = (daily_summary['day_of_week'].isin([5, 6])).astype(int)
daily_summary = daily_summary.drop(columns=['sale_date_dt'])

print(f"  Created {len(daily_summary):,} daily summary records")

# =====================================
# SAVE FILES
# =====================================
print("\nSaving files to data/ folder...")

products_df.to_csv('../data/products.csv', index=False)
stores_df.to_csv('../data/stores.csv', index=False)
campaigns_df.to_csv('../data/campaigns.csv', index=False)
daily_sales_df.to_csv('../data/daily_sales.csv', index=False)
daily_summary.to_csv('../data/daily_summary.csv', index=False)

print("\n" + "="*60)
print("DATA GENERATION COMPLETE")
print("="*60)
print(f"Products (SKUs):        {len(products_df):,}")
print(f"Stores:                 {len(stores_df):,}")
print(f"Marketing Campaigns:    {len(campaigns_df):,}")
print(f"Daily Sales Records:    {len(daily_sales_df):,}")
print(f"Daily Summary Records:  {len(daily_summary):,}")
print(f"\nDate range: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
print(f"Total days: {TOTAL_DAYS}")
print(f"\nFiles saved to ../data/ folder")