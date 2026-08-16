import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set fixed random seeds for 100% reproducibility across environments
random.seed(42)
np.random.seed(42)

CATEGORIES = ["grocery", "food_delivery", "recharge", "bill_payment", "travel", "ecommerce", "entertainment"]
REGIONS = ["North", "South", "East", "West"]
METHODS = ["UPI", "Wallet", "Card", "Netbanking"]
METHOD_WEIGHTS = [0.55, 0.20, 0.15, 0.10]
AMOUNTS_INR = [49, 99, 149, 299, 499, 799, 1499, 2999, 4999]
AMOUNT_WEIGHTS = [0.18, 0.16, 0.14, 0.14, 0.12, 0.10, 0.08, 0.05, 0.03]

# --- 1. 40 Merchants ---
merchants = pd.DataFrame({
    "merchant_id": range(1, 41),
    "merchant_name": [f"Merchant_{i:03d}" for i in range(1, 41)],
    "category": [random.choice(CATEGORIES) for _ in range(40)],
    "region": [random.choice(REGIONS) for _ in range(40)],
})

# --- 2. 350 Established Users (signed up 30-730 days before window start) ---
window_start = datetime(2026, 1, 1)
users = pd.DataFrame({
    "user_id": range(1, 351),
    "signup_date": [window_start - timedelta(days=random.randint(30, 730)) for _ in range(350)],
})

# --- 3. 500 Baseline Transactions over a 30-day window ---
rows = []
for i in range(500):
    txn_time = window_start + timedelta(
        days=random.randint(0, 29),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    status = np.random.choice(["captured", "failed", "chargeback"], p=[0.92, 0.06, 0.02])
    rows.append({
        "transaction_id": f"TXN{100000 + i}",
        "user_id": random.randint(1, 350),
        "merchant_id": random.randint(1, 40),
        "transaction_time": txn_time,
        "amount_inr": np.random.choice(AMOUNTS_INR, p=AMOUNT_WEIGHTS),
        "payment_method": np.random.choice(METHODS, p=METHOD_WEIGHTS),
        "status": status,
        "risk_score": random.randint(0, 100),
    })

# --- 4. Inject 15 "burner account" chargeback frauds (< 30 days old) ---
next_user_id = 351
for i in range(15):
    txn_time = window_start + timedelta(days=random.randint(10, 29), hours=random.randint(0, 23))
    signup = txn_time - timedelta(days=random.randint(1, 25))
    users = pd.concat([users, pd.DataFrame([{"user_id": next_user_id, "signup_date": signup}])], ignore_index=True)
    rows.append({
        "transaction_id": f"TXN{200000 + i}",
        "user_id": next_user_id,
        "merchant_id": random.randint(1, 40),
        "transaction_time": txn_time,
        "amount_inr": random.choice([999, 1999, 2999, 4999]),
        "payment_method": "Card",
        "status": "chargeback",
        "risk_score": random.randint(70, 100),
    })
    next_user_id += 1

# --- 5. Inject 8 Velocity-Attack Clusters (4 rapid-fire txns within 5 mins) ---
for cluster in range(8):
    victim_user = random.randint(1, 350)
    base_time = window_start + timedelta(days=random.randint(0, 29), hours=random.randint(0, 23))
    for k in range(4):
        rows.append({
            "transaction_id": f"TXN{300000 + cluster * 4 + k}",
            "user_id": victim_user,
            "merchant_id": random.randint(1, 40),
            "transaction_time": base_time + timedelta(minutes=k),
            "amount_inr": random.choice([299, 399, 499]),
            "payment_method": "Card",
            "status": "captured" if k == 3 else "failed",
            "risk_score": random.randint(60, 95),
        })

ledger = pd.DataFrame(rows)  # 500 + 15 + 32 = 547 rows total

# Export clean files
merchants.to_csv("merchants.csv", index=False)
users.to_csv("users.csv", index=False)
ledger.to_csv("ledger.csv", index=False)

# --- 6. Build the Discrepant "Gateway Export" Copy ---
gateway = ledger.copy()
n = len(gateway)

# 5% missing rows
missing_idx = np.random.choice(n, size=int(0.05 * n), replace=False)
gateway = gateway.drop(index=missing_idx).reset_index(drop=True)

# 3% amount mismatches
mismatch_idx = np.random.choice(len(gateway), size=int(0.03 * n), replace=False)
gateway.loc[mismatch_idx, "amount_inr"] = gateway.loc[mismatch_idx, "amount_inr"] + \
    np.random.choice([-100, -50, 50, 100], size=len(mismatch_idx))

# 2% extra rows
extra_rows = []
for i in range(int(0.02 * n)):
    extra_rows.append({
        "transaction_id": f"TXNX{9000 + i}",
        "user_id": random.randint(1, 350),
        "merchant_id": random.randint(1, 40),
        "transaction_time": window_start + timedelta(days=random.randint(0, 29)),
        "amount_inr": random.choice(AMOUNTS_INR),
        "payment_method": random.choice(METHODS),
        "status": "captured",
        "risk_score": random.randint(0, 100),
    })
gateway = pd.concat([gateway, pd.DataFrame(extra_rows)], ignore_index=True)

# 2% status mismatches
status_idx = np.random.choice(len(gateway), size=int(0.02 * n), replace=False)
gateway.loc[status_idx, "status"] = "failed"

# Export gateway export file
gateway.to_csv("gateway_export.csv", index=False)
print("Data generation complete! 4 CSV files generated successfully.")