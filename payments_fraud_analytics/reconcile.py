import pandas as pd

def reconcile_payments(ledger_df, gateway_df):
    # 1. Missing in Gateway
    missing_in_gateway = ledger_df[~ledger_df["transaction_id"].isin(gateway_df["transaction_id"])]
    
    # 2. Extra in Gateway (Missing in Ledger)
    extra_in_gateway = gateway_df[~gateway_df["transaction_id"].isin(ledger_df["transaction_id"])]
    
    # Pairwise comparison on common transactions
    merged = pd.merge(
        ledger_df, gateway_df, 
        on="transaction_id", 
        suffixes=("_ledger", "_gateway")
    )
    
    # 3. Amount Mismatches
    amount_mismatches = merged[merged["amount_inr_ledger"] != merged["amount_inr_gateway"]].copy()
    amount_mismatches["difference_inr"] = amount_mismatches["amount_inr_gateway"] - amount_mismatches["amount_inr_ledger"]
    
    # 4. Status Mismatches
    status_mismatches = merged[merged["status_ledger"] != merged["status_gateway"]].copy()
    
    return missing_in_gateway, extra_in_gateway, amount_mismatches, status_mismatches