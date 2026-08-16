import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, 
    recall_score, f1_score, roc_auc_score, roc_curve
)

print("=" * 70)
print("PART 2: CREDIT RISK & LENDING ML PIPELINE")
print("=" * 70)

# =============================================================================
# TASK A: EDA & PREPROCESSING
# =============================================================================
df = pd.read_csv("credit_applicants.csv")

# 1. Report default rate & missing bureau score %
total_rows = len(df)
default_rate = df["default"].mean()
missing_bureau_pct = df["credit_bureau_score"].isna().mean()

print(f"\n[Task A] Dataset EDA:")
print(f" - Total Applicants: {total_rows}")
print(f" - Measured Default Rate: {default_rate:.2%} ({df['default'].sum()}/{total_rows})")
print(f" - Missing Bureau Score (Thin-File): {missing_bureau_pct:.2%} ({df['credit_bureau_score'].isna().sum()}/{total_rows})")

# Engineer binary is_thin_file flag BEFORE splitting/imputing
df["is_thin_file"] = df["credit_bureau_score"].isna().astype(int)

# One-hot encode employment_type
df = pd.get_dummies(df, columns=["employment_type"], drop_first=False, dtype=int)

# Separate features and target
X = df.drop(columns=["applicant_id", "default"])
y = df["default"]

# 2. Train/Test split: 75/25, stratified on default, random_state=42
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# Compute median of credit_bureau_score ONLY on training split
train_bureau_median = X_train["credit_bureau_score"].median()
print(f" - Training-derived median bureau score: {train_bureau_median:.2f}")

# Impute missing values using train median
X_train["credit_bureau_score"] = X_train["credit_bureau_score"].fillna(train_bureau_median)
X_test["credit_bureau_score"] = X_test["credit_bureau_score"].fillna(train_bureau_median)

# Scale numeric features with StandardScaler (fit on train only)
numeric_cols = ["age", "monthly_income_inr", "existing_loans_count", 
                "credit_utilization_ratio", "upi_monthly_inflow_inr", 
                "bounced_payments_count", "credit_bureau_score"]

scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

# =============================================================================
# TASK B: CLASSIFICATION MODELS
# =============================================================================
# 1. Train Logistic Regression & Decision Tree
log_reg = LogisticRegression(random_state=42, max_iter=1000)
log_reg.fit(X_train_scaled, y_train)

dt_clf = DecisionTreeClassifier(random_state=42)
dt_clf.fit(X_train_scaled, y_train)

# Predictions
y_pred_log = log_reg.predict(X_test_scaled)
y_prob_log = log_reg.predict_proba(X_test_scaled)[:, 1]

y_pred_dt = dt_clf.predict(X_test_scaled)
y_prob_dt = dt_clf.predict_proba(X_test_scaled)[:, 1]

def evaluate_model(y_true, y_pred, y_prob):
    cm = confusion_matrix(y_true, y_pred)
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob)
    return cm, acc, prec, rec, f1, auc

cm_log, acc_log, prec_log, rec_log, f1_log, auc_log = evaluate_model(y_test, y_pred_log, y_prob_log)
cm_dt, acc_dt, prec_dt, rec_dt, f1_dt, auc_dt = evaluate_model(y_test, y_pred_dt, y_prob_dt)

print("\n" + "=" * 70)
print("TASK B: MODEL COMPARISON TABLE (SIDE BY SIDE)")
print("=" * 70)
comp_df = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"],
    "Logistic Regression": [acc_log, prec_log, rec_log, f1_log, auc_log],
    "Decision Tree": [acc_dt, prec_dt, rec_dt, f1_dt, auc_dt]
})
print(comp_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\nConfusion Matrix (Logistic Regression):")
print(cm_log)
print("Confusion Matrix (Decision Tree):")
print(cm_dt)

# 2. Risk-Based Pricing Table (using Logistic Regression predicted probabilities on FULL dataset)
X_full_scaled = df.drop(columns=["applicant_id", "default"]).copy()
X_full_scaled["credit_bureau_score"] = X_full_scaled["credit_bureau_score"].fillna(train_bureau_median)
X_full_scaled[numeric_cols] = scaler.transform(X_full_scaled[numeric_cols])

df["pred_default_prob"] = log_reg.predict_proba(X_full_scaled)[:, 1]

# Divide into 4 Risk Tiers via Quartiles
df["risk_tier"] = pd.qcut(df["pred_default_prob"], q=4, labels=[
    "Tier 1: Low Risk (10-14% APR)",
    "Tier 2: Medium Risk (15-18% APR)",
    "Tier 3: High Risk (19-24% APR)",
    "Tier 4: Extreme Risk (Rejected / 28%+ APR)"
])

pricing_summary = df.groupby("risk_tier", observed=False).agg(
    applicant_count=("applicant_id", "count"),
    avg_pred_prob=("pred_default_prob", "mean"),
    actual_default_rate=("default", "mean")
).reset_index()

print("\n" + "=" * 70)
print("TASK B: RISK-BASED PRICING TABLE")
print("=" * 70)
print(pricing_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# =============================================================================
# TASK C: ANOMALY DETECTION (ISOLATION FOREST)
# =============================================================================
behaviour = pd.read_csv("txn_behaviour.csv")

# Extract behavioural numeric features & standardize
behaviour_features = behaviour[["txn_hour", "is_new_device", "txn_amount_inr"]]
scaler_iso = StandardScaler()
behaviour_scaled = scaler_iso.fit_transform(behaviour_features)

# Contamination = 15 / 265 ≈ 0.0566
iso_forest = IsolationForest(contamination=15 / 265, random_state=42)
behaviour["anomaly_pred"] = iso_forest.fit_predict(behaviour_scaled)

# Isolation Forest tags anomalies as -1
behaviour["is_flagged"] = (behaviour["anomaly_pred"] == -1).astype(int)

# Ground truth: txn_id starting with BTXNA
behaviour["is_ground_truth_anomaly"] = behaviour["txn_id"].str.startswith("BTXNA").astype(int)

seeded_anomalies = behaviour[behaviour["is_ground_truth_anomaly"] == 1]
flagged_seeded = seeded_anomalies["is_flagged"].sum()
total_seeded = len(seeded_anomalies)
recall_iso = flagged_seeded / total_seeded

print("\n" + "=" * 70)
print("TASK C: ANOMALY DETECTION RESULTS (ISOLATION FOREST)")
print("=" * 70)
print(f"Total Transactions: {len(behaviour)}")
print(f"Ground Truth Injected Anomalies (BTXNA*): {total_seeded}")
print(f"Total Flagged as Anomalous (-1): {behaviour['is_flagged'].sum()}")
print(f"Flagged Seeded Anomalies: {flagged_seeded} / {total_seeded}")
print(f"Isolation Forest Anomaly Recall: {recall_iso:.2%}")
print("=" * 70)