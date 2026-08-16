import sqlite3
import pandas as pd

# Connect to (or create) SQLite database file
conn = sqlite3.connect("paytm_payments.db")
cursor = conn.cursor()

# -------------------------------------------------------------
# 1. CREATE TABLES WITH PRIMARY & FOREIGN KEYS
# -------------------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id INTEGER PRIMARY KEY,
    merchant_name TEXT,
    category TEXT,
    region TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    signup_date DATE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id INTEGER,
    merchant_id INTEGER,
    transaction_time TIMESTAMP,
    amount_inr REAL,
    payment_method TEXT,
    status TEXT,
    risk_score INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id)
);
""")

# Load CSV data into SQLite database
merchants_df = pd.read_csv("merchants.csv")
users_df = pd.read_csv("users.csv")
ledger_df = pd.read_csv("ledger.csv")

merchants_df.to_sql("merchants", conn, if_exists="replace", index=False)
users_df.to_sql("users", conn, if_exists="replace", index=False)
ledger_df.to_sql("transactions", conn, if_exists="replace", index=False)

conn.commit()
print("✅ Database paytm_payments.db created and data loaded successfully!\n")

# -------------------------------------------------------------
# 2. REQUIRED SQL QUERIES (PART B)
# -------------------------------------------------------------

# Query 1: Basic Filtering & Sorting (SELECT, WHERE, ORDER BY, LIMIT)
print("--- Query 1: Top 5 Highest Value Captured Transactions ---")
q1 = """
SELECT transaction_id, user_id, amount_inr, payment_method, status 
FROM transactions 
WHERE status = 'captured' 
ORDER BY amount_inr DESC 
LIMIT 5;
"""
print(pd.read_sql_query(q1, conn))

# Query 2: Unique Payment Methods (DISTINCT)
print("\n--- Query 2: All Distinct Payment Methods ---")
q2 = "SELECT DISTINCT payment_method FROM transactions;"
print(pd.read_sql_query(q2, conn))

# Query 3: Merchant Transaction Counts (LEFT JOIN, GROUP BY)
print("\n--- Query 3: Merchant Summary (LEFT JOIN) ---")
q3 = """
SELECT m.merchant_id, m.merchant_name, m.category, COUNT(t.transaction_id) AS total_txns
FROM merchants m
LEFT JOIN transactions t ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.category
LIMIT 5;
"""
print(pd.read_sql_query(q3, conn))

# Query 4: Chargeback Impact (INNER JOIN, SUM, COUNT)
print("\n--- Query 4: Total Chargeback Impact ---")
q4 = """
SELECT 
    COUNT(t.transaction_id) AS chargeback_count,
    COUNT(DISTINCT t.user_id) AS unique_users_affected,
    SUM(t.amount_inr) AS total_chargeback_amount_inr
FROM transactions t
INNER JOIN merchants m ON t.merchant_id = m.merchant_id
WHERE t.status = 'chargeback';
"""
print(pd.read_sql_query(q4, conn))

# Query 5: Identify Burner Accounts (0 <= account_age_days < 30)
print("\n--- Query 5: Burner Account Chargebacks ---")
q5 = """
SELECT 
    t.transaction_id,
    t.user_id,
    u.signup_date,
    t.transaction_time,
    CAST((JULIANDAY(t.transaction_time) - JULIANDAY(u.signup_date)) AS INT) AS account_age_days,
    t.amount_inr,
    t.status
FROM transactions t
INNER JOIN users u ON t.user_id = u.user_id
WHERE t.status = 'chargeback'
  AND (JULIANDAY(t.transaction_time) - JULIANDAY(u.signup_date)) >= 0
  AND (JULIANDAY(t.transaction_time) - JULIANDAY(u.signup_date)) < 30;
"""
burner_results = pd.read_sql_query(q5, conn)
print(f"Burner account rows found: {len(burner_results)} (Target: 15)")

# Query 6: Velocity Attacks (10-minute buckets, >= 3 txns)
print("\n--- Query 6: Velocity Attack Clusters ---")
q6 = """
SELECT 
    user_id,
    STRFTIME('%Y-%m-%d %H:', transaction_time) || 
    PRINTF('%02d', (CAST(STRFTIME('%M', transaction_time) AS INT) / 10) * 10) AS time_bucket,
    COUNT(transaction_id) AS transaction_count
FROM transactions
GROUP BY user_id, time_bucket
HAVING transaction_count >= 3;
"""
velocity_results = pd.read_sql_query(q6, conn)
print(f"Velocity attack clusters found: {len(velocity_results)} (Target: 8)")
print(velocity_results)

conn.close()