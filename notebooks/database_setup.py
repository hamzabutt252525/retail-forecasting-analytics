"""
DATABASE SETUP
Creates SQLite database and loads all tables with indexes
"""

import pandas as pd
import sqlite3
import time
import os

db_path = '../data/retail_analytics.db'

# Fresh start
if os.path.exists(db_path):
    os.remove(db_path)
    print("Removed existing database")

conn = sqlite3.connect(db_path)
print(f"Created database: {db_path}")

# Load tables
print("\nLoading products...")
start = time.time()
products = pd.read_csv('../data/products.csv')
products.to_sql('products', conn, if_exists='replace', index=False)
print(f"  Loaded {len(products):,} products in {time.time()-start:.1f}s")

print("\nLoading stores...")
stores = pd.read_csv('../data/stores.csv')
stores.to_sql('stores', conn, if_exists='replace', index=False)
print(f"  Loaded {len(stores):,} stores")

print("\nLoading campaigns...")
campaigns = pd.read_csv('../data/campaigns.csv')
campaigns.to_sql('campaigns', conn, if_exists='replace', index=False)
print(f"  Loaded {len(campaigns):,} campaigns")

print("\nLoading daily sales (this takes 30-60 seconds)...")
start = time.time()
daily_sales = pd.read_csv('../data/daily_sales.csv')
daily_sales.to_sql('daily_sales', conn, if_exists='replace', index=False)
print(f"  Loaded {len(daily_sales):,} daily sales in {time.time()-start:.1f}s")

print("\nLoading daily summary...")
daily_summary = pd.read_csv('../data/daily_summary.csv')
daily_summary.to_sql('daily_summary', conn, if_exists='replace', index=False)
print(f"  Loaded {len(daily_summary):,} daily summary records")

# Create indexes
print("\nCreating indexes...")
start = time.time()
cursor = conn.cursor()

cursor.execute("CREATE INDEX idx_sales_date ON daily_sales(sale_date)")
cursor.execute("CREATE INDEX idx_sales_sku ON daily_sales(sku_id)")
cursor.execute("CREATE INDEX idx_sales_store ON daily_sales(store_id)")
cursor.execute("CREATE INDEX idx_sales_campaign ON daily_sales(active_campaign)")
cursor.execute("CREATE INDEX idx_summary_date ON daily_summary(sale_date)")

conn.commit()
print(f"  Created 5 indexes in {time.time()-start:.1f}s")

# Verify
print("\nDatabase verification:")
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
for _, row in tables.iterrows():
    count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {row['name']}", conn).iloc[0]['cnt']
    print(f"  {row['name']}: {count:,} rows")

conn.close()

file_size_mb = os.path.getsize(db_path) / 1024 / 1024
print(f"\n{'='*60}")
print("DATABASE READY")
print(f"{'='*60}")
print(f"Database file: {db_path}")
print(f"File size: {file_size_mb:.1f} MB")