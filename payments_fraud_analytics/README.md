**Payments \& Fraud Analytics Documentation**



This folder contains the complete payments analytics, SQL fraud detection engine, ledger-to-gateway reconciliation pipeline, and four-layer code-generated dashboard for Paytm platform operations.



\---



**Part A — Merchant Workbook \& Business Logic (`merchant\_workbook.xlsx`)**



The merchant workbook integrates transaction data with business data, fee tier calculations, and daily transaction rules.



**Applied Business \& Formula Logic**

1\. Merchant Attribute Lookup (VLOOKUP):

&#x20;  Looks up merchant details (`merchant\_name`, `category`, `region`) from `merchants.csv`:

&#x20;  ```excel

&#x20;  	=IFERROR(VLOOKUP(C2, Merchants!$A$2:$D$41, 2, FALSE), "Merchant not found")

2.MDR Fee Tier Lookup (HLOOKUP):

Retrieves MDR fee percentages laid out horizontally in Fee\_Tiers:

&#x09;=HLOOKUP(F2, Fee\_Tiers!$B$1:$E$2, 2, FALSE)

3.Nested IF / AND Classification Rule:

Classifies transactions based on daily merchant volume and regional filtering. If merchant daily GMV exceeds INR 5,000 and region is NOT "East", it is classified as "High-Value Merchant Day", else "Standard"(no value in our system exceded "5000", therefore all transactions are flagged as "standard"):

&#x09;=IF(AND(SUMIFS($E:$E, $C:$C, C2, $D:$D, INT(D2))>5000, J2<>"East"), "High-Value 	Merchant Day", "Standard")

4.Pivot Table Summary (Summary\_Pivot):

Summarizes total GMV, total transaction counts, and unique transacted days per merchant to evaluate merchant engagement metrics.



\---



**Part B — SQL Fraud-Pattern Detection (paytm\_payments.db)**



The SQLite database stores relational data across users, merchants, and transactions tables to surface fraud patterns.



**Fraud Detection Query Results \& Logic**

1\.Quantify Chargeback Impact:

Identifies total chargeback occurrences, unique impacted users, and net exposure.
SELECT 

&#x20;   COUNT(\*) AS total\_chargeback\_txns,

&#x20;   COUNT(DISTINCT user\_id) AS unique\_users\_affected,

&#x20;   SUM(amount\_inr) AS total\_chargeback\_amount\_inr

FROM transactions

WHERE status = 'chargeback';



2.Burner Accounts Detection:

Surfaces accounts where chargeback transactions occur within 30 days of user signup, identifying all 15 seeded fraudulent burner accounts.
SELECT 

&#x20;   t.transaction\_id,

&#x20;   t.user\_id,

&#x20;   u.signup\_date,

&#x20;   t.transaction\_time,

&#x20;   t.amount\_inr,

&#x20;   t.status

FROM transactions t

JOIN users u ON t.user\_id = u.user\_id

WHERE t.status = 'chargeback'

&#x20; AND JULIANDAY(t.transaction\_time) - JULIANDAY(u.signup\_date) >= 0

&#x20; AND JULIANDAY(t.transaction\_time) - JULIANDAY(u.signup\_date) < 30;

3.Velocity Attack Detection:

Identifies rapid-fire transaction spikes ($\\ge 3$ transactions within a 10-minute window) per user, successfully isolating all 8 seeded velocity attack clusters.

SELECT 

&#x20;   user\_id,

&#x20;   DATETIME((STRFTIME('%s', transaction\_time) / 600) \* 600, 'unixepoch') AS time\_bucket\_10m,

&#x20;   COUNT(\*) AS txn\_count

FROM transactions

GROUP BY user\_id, time\_bucket\_10m

HAVING COUNT(\*) >= 3

ORDER BY time\_bucket\_10m;



4.Category GMV \& Failure Rates:

Aggregates processing volume and failure rates across merchant categories. High failure rates indicate potential technical friction or card testing activity.

SELECT 

&#x20;   m.category,

&#x20;   SUM(t.amount\_inr) AS total\_gmv,

&#x20;   COUNT(t.transaction\_id) AS total\_txns,

&#x20;   ROUND(100.0 \* SUM(CASE WHEN t.status = 'failed' THEN 1 ELSE 0 END) / COUNT(\*), 2) AS failure\_rate\_pct

FROM transactions t

INNER JOIN merchants m ON t.merchant\_id = m.merchant\_id

GROUP BY m.category

ORDER BY total\_gmv DESC;



5.High-Risk Region Analysis:

Filters regions with an average risk score greater than 40.

SELECT 

&#x20;   m.region,

&#x20;   COUNT(DISTINCT t.user\_id) AS distinct\_users,

&#x20;   AVG(t.risk\_score) AS avg\_risk\_score

FROM transactions t

LEFT JOIN merchants m ON t.merchant\_id = m.merchant\_id

GROUP BY m.region

HAVING AVG(t.risk\_score) > 40

ORDER BY avg\_risk\_score DESC;



6.Payment Method Market Share:

Evaluates transaction distribution across payment methods.
SELECT 

&#x20;   payment\_method,

&#x20;   COUNT(\*) AS txn\_count,

&#x20;   ROUND(SUM(amount\_inr), 2) AS total\_amount\_inr

FROM transactions

GROUP BY payment\_method

ORDER BY txn\_count DESC;



\---



&#x20;**Part C — Payment Reconciliation (reconcile.py)**

The reusable reconcile\_payments(ledger\_df, gateway\_df) module uses set operations and outer joins on transaction\_id to reconcile ledger.csv against gateway\_export.csv.



Four Discrepancy Categories

Missing in Gateway (\~5%): Transactions recorded in internal ledgers but missing from gateway logs due to network transmission failures or unacknowledged webhooks.



Extra in Gateway (\~2%): Gateway records missing from internal ledgers, indicating uncaptured webhook callbacks.



Amount Mismatches (\~3%): Transactions present in both sets where amount\_inr differs, capturing dynamic currency conversion or fee adjustments.



Status Mismatches (\~2%): Transactions present in both sets with conflicting states (e.g., captured in ledger vs. failed in gateway).



\---



**Part D — Four-Layer Dashboard \& Written Interpretations**



Generated via generate\_dashboard.py and saved into dashboard\_charts



1\. Headline Layer Scorecards (dashboard\_charts/headline\_scorecards.png)



Exact Scorecard Definitions Used:

Match Rate Formula:

&#x09;match\_rate = Count of transactions present in BOTH ledger and gateway with identical amount AND status/Total transaction count in ledger.csv



Platform Chargeback Ratio Formula:
	chargeback\_ratio = (Count of transactions with status == 'chargeback')/(Total transaction count in ledger.csv) \* 100



Written Interpretation: The platform demonstrates high overall GMV stability across the 30-day window. The overall transaction success rate reflects strong payment pipeline availability, while the platform-wide chargeback ratio remains below critical thresholds. The reconciliation match rate captures normal processing divergence due to gateway sync latencies and settlement drops, requiring automated end-of-day reconciliation sweeps.



2\. Trends Layer (dashboard\_charts/trend\_gmv\_chargebacks.png)

Written Interpretation: Daily GMV exhibits cyclical volume distribution with predictable weekend demand peaks. Chargeback events do not occur uniformly across time; instead, they cluster heavily on specific calendar dates. This temporal clustering confirms organized fraud campaigns and velocity attacks rather than isolated, organic customer disputes.



3\. Breakdown Layer (dashboard\_charts/breakdown\_gmv\_method\_category.png)

Written Interpretation: Payment method analysis shows heavy user preference for instant, low-friction channels like UPI and Mobile Wallets, which account for the dominant portion of volume. Category breakdowns indicate high-frequency retail (Grocery, Recharge) leads in transaction volume, whereas Travel and E-Commerce account for higher average order values. Risk controls should focus on Card and Netbanking rails due to higher chargeback propensities.



4\. Details Layer (dashboard\_charts/top10\_merchants\_table.png)

Written Interpretation: Top merchants ranked by transaction volume represent core business partners driving ecosystem GMV. Per-merchant chargeback ratio analysis highlights merchants exceeding the 1.0% chargeback risk threshold (chargeback\_ratio > 0.01), highlighted in conditional red fill. High-risk flagged merchants are automatically escalated for compliance review, step-up 2FA requirements, and rolling settlement reserves.

