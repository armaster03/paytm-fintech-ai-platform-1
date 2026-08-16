import os
import pandas as pd
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("dashboard_charts", exist_ok=True)

# Load data
ledger = pd.read_csv("ledger.csv")
merchants = pd.read_csv("merchants.csv")
gateway = pd.read_csv("gateway_export.csv")

ledger["transaction_time"] = pd.to_datetime(ledger["transaction_time"])
ledger["date"] = ledger["transaction_time"].dt.date
df = pd.merge(ledger, merchants, on="merchant_id", how="left")

# -------------------------------------------------------------
# Layer 1: Headline Scorecards Image (headline_scorecards.png)
# -------------------------------------------------------------
common = pd.merge(ledger, gateway, on="transaction_id", suffixes=("_ledger", "_gateway"))
matched_rows = common[(common["amount_inr_ledger"] == common["amount_inr_gateway"]) & 
                      (common["status_ledger"] == common["status_gateway"])]
match_rate = len(matched_rows) / len(ledger)

total_gmv = ledger["amount_inr"].sum()
overall_success_rate = (ledger["status"] == "captured").sum() / len(ledger)
chargeback_ratio = (ledger["status"] == "chargeback").sum() / len(ledger)

fig, ax = plt.subplots(figsize=(8, 4))
ax.axis("off")

card_text = (
    f"  PAYTM PAYMENTS & FRAUD DASHBOARD\n"
    f"  ==========================================\n\n"
    f"  • Total GMV:                  ₹{total_gmv:,.2f}\n"
    f"  • Overall Success Rate:        {overall_success_rate:.2%}\n"
    f"  • Reconciliation Match Rate:  {match_rate:.2%}\n"
    f"  • Platform Chargeback Ratio:  {chargeback_ratio:.2%}\n"
)

ax.text(0.05, 0.5, card_text, fontsize=13, family="monospace", va="center",
        bbox=dict(boxstyle="round,pad=1", facecolor="#e6f2ff", edgecolor="#0056b3", lw=2))

plt.title("Layer 1: Headline Scorecards", fontsize=14, fontweight="bold", pad=10)
plt.tight_layout()
plt.savefig("dashboard_charts/headline_scorecards.png", dpi=300, bbox_inches="tight")
plt.close()

# -------------------------------------------------------------
# Layer 2: Trends Layer (trend_gmv_chargebacks.png)
# -------------------------------------------------------------
daily_stats = ledger.groupby("date").agg(
    daily_gmv=("amount_inr", "sum"),
    daily_chargebacks=("status", lambda s: (s == "chargeback").sum())
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 4))
ax2 = ax1.twinx()

ax1.plot(daily_stats["date"], daily_stats["daily_gmv"], color="#1f77b4", marker="o", linewidth=2, label="Daily GMV (INR)")
ax2.bar(daily_stats["date"], daily_stats["daily_chargebacks"], color="#d62728", alpha=0.4, label="Chargeback Count")

ax1.set_xlabel("Date")
ax1.set_ylabel("Daily GMV (INR)", color="#1f77b4")
ax2.set_ylabel("Chargeback Count", color="#d62728")
plt.title("Layer 2: Daily GMV & Chargeback Count Trend (30 Days)", fontweight="bold")
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig("dashboard_charts/trend_gmv_chargebacks.png", dpi=300, bbox_inches="tight")
plt.close()

# -------------------------------------------------------------
# Layer 3: Breakdown Layer (breakdown_gmv_method_category.png)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

gmv_by_method = df.groupby("payment_method")["amount_inr"].sum().sort_values(ascending=False)
gmv_by_method.plot(kind="bar", ax=ax1, color="#2ca02c")
ax1.set_title("GMV by Payment Method")
ax1.set_ylabel("GMV (INR)")

gmv_by_cat = df.groupby("category")["amount_inr"].sum().sort_values(ascending=False)
gmv_by_cat.plot(kind="bar", ax=ax2, color="#ff7f0e")
ax2.set_title("GMV by Category")
ax2.set_ylabel("GMV (INR)")

plt.suptitle("Layer 3: GMV Breakdown", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("dashboard_charts/breakdown_gmv_method_category.png", dpi=300, bbox_inches="tight")
plt.close()

# -------------------------------------------------------------
# Layer 4: Details Layer Table (top10_merchants_table.png)
# -------------------------------------------------------------
merchant_stats = df.groupby(["merchant_id", "merchant_name"]).agg(
    txn_count=("transaction_id", "count"),
    chargeback_count=("status", lambda s: (s == "chargeback").sum())
).reset_index()

merchant_stats["chargeback_ratio"] = merchant_stats["chargeback_count"] / merchant_stats["txn_count"]
merchant_stats["high_risk_flag"] = merchant_stats["chargeback_ratio"].apply(
    lambda r: "HIGH RISK (>1%)" if r > 0.01 else "NORMAL"
)

top10 = merchant_stats.sort_values(by="txn_count", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 4))
ax.axis("off")

table_data = []
headers = ["Merchant ID", "Name", "Txn Count", "Chargeback Ratio", "Risk Flag"]
for _, r in top10.iterrows():
    table_data.append([
        r["merchant_id"], r["merchant_name"], r["txn_count"], 
        f"{r['chargeback_ratio']:.2%}", r["high_risk_flag"]
    ])

table = ax.table(cellText=table_data, colLabels=headers, loc="center", cellLoc="center")
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.1, 1.4)

for i, r in enumerate(top10.iterrows()):
    if r[1]["high_risk_flag"] == "HIGH RISK (>1%)":
        table[(i + 1, 4)].set_facecolor("#ffcccc")

plt.title("Layer 4: Top 10 Merchants by Txn Volume & Risk Flags", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig("dashboard_charts/top10_merchants_table.png", dpi=300, bbox_inches="tight")
plt.close()

print("Dashboard generation complete! Output files in dashboard_charts/:")
for f in os.listdir("dashboard_charts"):
    print(f" - dashboard_charts/{f}")