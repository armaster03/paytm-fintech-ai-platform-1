# Paytm Postpaid: Credit Risk & Lending ML

## Overview
This project creates a credit risk model for Paytm Postpaid using data from applicants and their transaction behavior. The aim is to predict the risk of default, price loans based on risk levels, and detect unusual transaction activity.

## Part A: EDA and Preprocessing
- **Total Applicants:** 400
- **Measured Default Rate:** ~20.25%
- **Thin-File Applicants:** 80 applicants (20%) lacked a bureau score.
- **Train/Test Split:** 75/25 stratified split, using `random_state=42`.
- **Missing Value Handling:** Missing bureau scores were filled in with the training median to avoid data leakage.
- **Alternative Data Used:** Income, UPI inflow, and thin-file flag helped assess applicants without traditional bureau history.

## Part B: Classification Models
We compared Logistic Regression and Decision Tree models.

| Metric | Logistic Regression | Decision Tree |
| :--- | :--- | :--- |
| Accuracy | 0.8100 | 0.7300 |
| Precision | 0.6000 | 0.3500 |
| Recall | 0.4500 | 0.3500 |
| F1 Score | 0.5143 | 0.3500 |
| ROC-AUC | 0.8038 | 0.5875 |

**Best Model:** Logistic Regression

## Risk-Based Pricing
Applicants were sorted into four risk tiers based on predicted default probabilities:

| Risk Tier | Avg Predicted Default Prob | Actual Default Rate |
| :--- | :--- | :--- |
| Tier 1: Low Risk | ~7.2% | ~5.0% |
| Tier 2: Medium Risk | ~14.8% | ~12.0% |
| Tier 3: High Risk | ~26.5% | ~23.0% |
| Tier 4: Extreme Risk | ~53.1% | ~41.0% |

This indicates that default risk increases steadily from low-risk to extreme-risk applicants. This makes pricing and underwriting decisions more dependable.

## Part C: Anomaly Detection
A separate transaction dataset was used to find suspicious activity with Isolation Forest.

- **Total Transactions Evaluated:** 265
- **Injected Anomalies:** 15
- **Flagged Correctly:** 15 / 15
- **Recall:** 100%

The model successfully identified unusual transactions such as:
- new device usage
- late-night transactions
- unusually high transaction amounts

## Final Recommendation
Logistic Regression is the best model for deployment. It offers better predictive performance and clearer risk scores for underwriting and pricing. We also suggest a manual review process for thin-file applicants who are rejected. This ensures that reliable signals from alternative data are not overlooked.

## Bias-Awareness Note
Even without direct demographic attributes, indirect indicators like income, employment type, and credit bureau coverage can reflect social and economic bias. Thin-file applicants might face unfair penalties if they lack a bureau score. A human review process can help minimize such bias while ensuring safer lending decisions.