**Payments & Fraud Analytics Documentation**



This folder contains the complete payments analytics, SQL fraud detection engine, ledger-to-gateway reconciliation pipeline, and four-layer code-generated dashboard for Paytm platform operations.



---



**Part A — Merchant Workbook & Business Logic (`merchant_workbook.xlsx`)**



The merchant workbook integrates transaction data with business data, fee tier calculations, and daily transaction rules.



**Applied Business & Formula Logic**

1. Merchant Attribute Lookup (VLOOKUP):

 Looks up merchant details
  (`merchant\_name`, `category`, `region`) from `merchants.csv`:

  ```excel

 	=IFERROR(VLOOKUP(C2, Merchants!$A$2:$D$41, 2, FALSE), "Merchant not found")

2.MDR Fee Tier Lookup (HLOOKUP):

Retrieves MDR fee percentages laid out horizontally in Fee\_Tiers:

=HLOOKUP(F2, Fee_Tiers!$B$1:$E$2, 2, FALSE)

3.Nested IF / AND Classification Rule:

Classifies transactions based on daily merchant volume and regional filtering. If merchant daily GMV exceeds INR 5,000 and region is NOT "East", it is classified as "High-Value Merchant Day", else "Standard"(no value in our system exceded "5000", therefore all transactions are flagged as "standard"):

=IF(AND(SUMIFS($E:$E, $C:$C, C2, $D:$D, INT(D2))>5000, J2<>"East"), "High-Value 	Merchant Day", "Standard")

4.Pivot Table Summary (Summary_Pivot):

Summarizes total GMV, total transaction counts, and unique transacted days per merchant to evaluate merchant engagement metrics.



\---



**Part B — SQL Fraud-Pattern Detection (paytm\_payments.db)**



The SQLite database stores relational data across users, merchants, and transactions tables to surface fraud patterns.



Query 1
This query filters transactions with the status captured and sorts them by amount in descending order to find the highest-value successful transactions. It helps identify large payment activity and validate successful transaction patterns.

SELECT transaction_id, user_id, amount_inr, payment_method, status
FROM transactions
WHERE status = 'captured'
ORDER BY amount_inr DESC
LIMIT 5;
RESULTS: 
 transaction_id  user_id  amount_inr payment_method    status
0      TXN100046      208        4999     Netbanking  captured
1      TXN100051      216        4999            UPI  captured
2      TXN100075      151        4999            UPI  captured
3      TXN100158      213        4999            UPI  captured
4      TXN100220       62        4999         Wallet  captured


Query 2
This query returns all unique payment methods used in the payment dataset. It is useful for analyzing channel distribution and confirming the payment methods available across transactions.
q2 = "SELECT DISTINCT payment_method FROM transactions;"
print(pd.read_sql_query(q2, conn))
RESULTS:
  payment_method
0         Wallet
1            UPI
2     Netbanking
3           Card
Query 3
This query uses a left join between merchants and transactions to count transactions per merchant. It helps identify which merchants are processing the highest number of payments and provides a quick operational summary.

SELECT m.merchant_id, m.merchant_name, m.category, COUNT(t.transaction_id) AS total_txns
FROM merchants m
LEFT JOIN transactions t ON m.merchant_id = t.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.category
LIMIT 5;
RESULTS:
   merchant_id merchant_name   category  total_txns
0            1  Merchant_001  ecommerce           9
1            2  Merchant_002    grocery          10
2            3  Merchant_003    grocery          17
3            4  Merchant_004  ecommerce           9
4            5  Merchant_005   recharge          11

Query 4
This query calculates the total chargeback count, unique affected users, and total amount lost due to chargebacks. It provides a financial risk summary for fraud impact analysis.

SELECT 
    COUNT(t.transaction_id) AS chargeback_count,
    COUNT(DISTINCT t.user_id) AS unique_users_affected,
    SUM(t.amount_inr) AS total_chargeback_amount_inr
FROM transactions t
INNER JOIN merchants m ON t.merchant_id = m.merchant_id
WHERE t.status = 'chargeback';

RESULTS:
   chargeback_count  unique_users_affected  total_chargeback_amount_inr
0                28                     27                        54472

Query 5
This query identifies chargeback transactions created by users within 30 days of signup, flagging burner or newly created accounts used for suspicious activity. It helps detect rapid account abuse and early-stage fraud behavior.

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
RESULTS:
Burner account rows found: 15 (Target: 15)

Query 6
This query groups transactions into 10-minute buckets by user and flags clusters with 3 or more transactions. It helps detect velocity-based fraud patterns where a user performs excessive transactions in a short time window.

SELECT 
    user_id,
    STRFTIME('%Y-%m-%d %H:', transaction_time) || 
    PRINTF('%02d', (CAST(STRFTIME('%M', transaction_time) AS INT) / 10) * 10) AS time_bucket,
    COUNT(transaction_id) AS transaction_count
FROM transactions
GROUP BY user_id, time_bucket
HAVING transaction_count >= 3;

RESULTS:   user_id       time_bucket  transaction_count
0       59  2026-01-09 21:00                  4
1       73  2026-01-12 09:00                  4
2      154  2026-01-02 22:00                  4
3      200  2026-01-01 22:00                  4
4      229  2026-01-12 12:00                  4
5      287  2026-01-14 14:00                  4
6      314  2026-01-02 18:00                  4
7      345  2026-01-23 09:00                  4




**Part C — Payment Reconciliation (reconcile.py)**

The reusable reconcile_payments(ledger_df, gateway_df) module uses set operations and outer joins on transaction_id to reconcile ledger.csv against gateway_export.csv.



Four Discrepancy Categories

Missing in Gateway (~5%): Transactions recorded in internal ledgers but missing from gateway logs due to network transmission failures or unacknowledged webhooks.



Extra in Gateway (~2%): Gateway records missing from internal ledgers, indicating uncaptured webhook callbacks.



Amount Mismatches (~3%): Transactions present in both sets where amount_inr differs, capturing dynamic currency conversion or fee adjustments.



Status Mismatches (~2%): Transactions present in both sets with conflicting states (e.g., captured in ledger vs. failed in gateway).



\---



**Part D — Four-Layer Dashboard & Written Interpretations**



Generated via generate_dashboard.py and saved into dashboard_charts



1\. Headline Layer Scorecards (dashboard_charts/headline_scorecards.png)



Exact Scorecard Definitions Used:

Match Rate Formula:

match_rate = Count of transactions present in BOTH ledger and gateway with identical amount AND status/Total transaction count in ledger.csv



Platform Chargeback Ratio Formula:
	chargeback_ratio = (Count of transactions with status == 'chargeback')/(Total transaction count in ledger.csv) \* 100



Written Interpretation: The platform demonstrates high overall GMV stability across the 30-day window. The overall transaction success rate reflects strong payment pipeline availability, while the platform-wide chargeback ratio remains below critical thresholds. The reconciliation match rate captures normal processing divergence due to gateway sync latencies and settlement drops, requiring automated end-of-day reconciliation sweeps.



2. Trends Layer (dashboard_charts/trend_gmv_chargebacks.png)

Written Interpretation: Daily GMV exhibits cyclical volume distribution with predictable weekend demand peaks. Chargeback events do not occur uniformly across time; instead, they cluster heavily on specific calendar dates. This temporal clustering confirms organized fraud campaigns and velocity attacks rather than isolated, organic customer disputes.



3. Breakdown Layer (dashboard_charts/breakdown_gmv_method_category.png)

Written Interpretation: Payment method analysis shows heavy user preference for instant, low-friction channels like UPI and Mobile Wallets, which account for the dominant portion of volume. Category breakdowns indicate high-frequency retail (Grocery, Recharge) leads in transaction volume, whereas Travel and E-Commerce account for higher average order values. Risk controls should focus on Card and Netbanking rails due to higher chargeback propensities.



4. Details Layer (dashboard_charts/top10_merchants_table.png)

Written Interpretation: Top merchants ranked by transaction volume represent core business partners driving ecosystem GMV. Per-merchant chargeback ratio analysis highlights merchants exceeding the 1.0% chargeback risk threshold (chargeback\_ratio > 0.01), highlighted in conditional red fill. High-risk flagged merchants are automatically escalated for compliance review, step-up 2FA requirements, and rolling settlement reserves.

