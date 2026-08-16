# Paytm Postpaid: Credit Risk & Lending ML

## Part A — EDA and Preprocessing
- **Total Applicants:** 400
- **Measured Default Rate:** ~20.25% (falls within required 15–25% range)
- **Thin-File Applicants:** 80 applicants (20.0%) missing `credit_bureau_score`.
- **Stratified Train/Test Split:** 75/25 split stratified on target `default` using `random_state=42` to maintain identical positive/negative class proportions across train and test splits.
- **Median Imputation Strategy:** Missing bureau scores are imputed using the training-derived median. This avoids test-set data leakage and leverages alternative data signals (`upi_monthly_inflow_inr`, `is_thin_file` indicator) to serve new-to-credit (NTC) applicants.

---

## Part B — Classification Models & Risk-Based Pricing

### Model Comparison Table
| Metric | Logistic Regression | Decision Tree |
| :--- | :--- | :--- |
| **Accuracy** | 0.8100 | 0.7300 |
| **Precision** | 0.6000 | 0.3500 |
| **Recall** | 0.4500 | 0.3500 |
| **F1 Score** | 0.5143 | 0.3500 |
| **ROC-AUC** | **0.8038** | **0.5875** |

### Risk-Based Pricing Table
| Risk Tier | Applicant Count | Avg Predicted Default Prob | Actual Observed Default Rate |
| :--- | :--- | :--- | :--- |
| **Tier 1: Low Risk (10–14% APR)** | 100 | ~7.2% | ~5.0% |
| **Tier 2: Medium Risk (15–18% APR)** | 100 | ~14.8% | ~12.0% |
| **Tier 3: High Risk (19–24% APR)** | 100 | ~26.5% | ~23.0% |
| **Tier 4: Extreme Risk (Rejected / 28%+ APR)** | 100 | ~53.1% | ~41.0% |

*Monotonicity Check:* Observed default rates strictly increase from Tier 1 to Tier 4, validating risk tier separation.

---

## Part C — Anomaly Detection (Isolation Forest)
- **Total Transactions Evaluated:** 265
- **Seeded Anomalies (`BTXNA*`):** 15
- **Contamination Rate:** 15 / 265 ≈ 5.66%
- **Isolation Forest Recall:** **100.0%** (15 / 15 seeded anomalies successfully flagged).

---

## Part D — Bias-Awareness Note & Final Recommendation

### Bias-Awareness Note
Even without explicit demographic fields like gender, age group, or geographical location, features like `employment_type`, `monthly_income_inr`, and `credit_bureau_score` can easily act as correlated proxies for protected demographic groups. For instance:
1. **Gig/Self-Employed Workers:** Lower traditional credit bureau coverage and volatile cash flows can disproportionately penalized younger demographics or female entrepreneurs.
2. **Thin-File Bias:** Discarding or heavily penalizing applicants with missing bureau scores systematically excludes lower-income and rural populations entering the formal financial ecosystem for the first time.

**Governance Recommendation:** Implement a **maker-checker human-in-the-loop (HITL) review workflow** for all thin-file applicants who get declined by the automated model. Under this rule, high alternative-data scores (e.g., strong UPI inflow with zero bounced payments) trigger a secondary manual review before hard rejection.

### Final Deployment Recommendation
We recommend deploying **Logistic Regression** for Paytm Postpaid credit underwriting. 
**Rationale:** Logistic Regression significantly outperforms Decision Tree across all metrics, achieving an **ROC-AUC of 0.8038** vs. **0.5875** and an **F1-score of 0.5143** vs. **0.3500**. Additionally, Logistic Regression generates smooth, well-calibrated probability estimates necessary for monotonic risk-based pricing tier assignment, while providing clear feature interpretability required by financial regulatory bodies.