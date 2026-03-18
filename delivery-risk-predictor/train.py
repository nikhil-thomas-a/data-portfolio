"""
Delivery Risk Predictor — Model Training & Evaluation
=======================================================
Binary classifier: will this sprint be delayed?

Models compared:
  - Logistic Regression  (baseline, interpretable)
  - Random Forest        (ensemble, handles non-linearity)
  - Gradient Boosting    (best accuracy, less interpretable)

Evaluation:
  - Train/test split (80/20)
  - ROC-AUC, precision, recall, F1
  - Confusion matrices
  - Feature importance (Random Forest)
  - SHAP-style manual importance plot

Outputs all charts to outputs/charts/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
import os

from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.preprocessing     import StandardScaler
from sklearn.linear_model      import LogisticRegression
from sklearn.ensemble          import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics           import (roc_auc_score, classification_report,
                                        confusion_matrix, roc_curve, ConfusionMatrixDisplay)
from sklearn.pipeline          import Pipeline

warnings.filterwarnings("ignore")
os.makedirs("outputs/charts", exist_ok=True)

# ── STYLE ──────────────────────────────────────────────────────────────────────

COLOURS = {"lr": "#0091FF", "rf": "#30A46C", "gb": "#E5484D"}

plt.rcParams.update({
    "figure.facecolor":   "#FAFAFA",
    "axes.facecolor":     "#FAFAFA",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": False,
    "axes.grid":          True,
    "grid.color":         "#EEEEEE",
    "grid.linewidth":     0.8,
    "font.family":        "sans-serif",
    "font.size":          11,
    "axes.titlesize":     13,
    "axes.titleweight":   "bold",
    "xtick.labelsize":    9,
    "ytick.labelsize":    9,
})

def save(name):
    plt.tight_layout()
    plt.savefig(f"outputs/charts/{name}.png", dpi=150, bbox_inches="tight",
                facecolor="#FAFAFA")
    plt.close()
    print(f"  ✅ {name}.png")


# ── LOAD & SPLIT ───────────────────────────────────────────────────────────────

print("\n── Loading data ──")
df = pd.read_csv("data/sprints_labelled.csv")

FEATURES = [
    "team_size", "sprint_number", "committed_points",
    "scope_change_pct", "dependency_count", "tech_debt_hrs",
    "key_person_risk", "unplanned_work_pct", "prev_sprint_carryover",
    "team_tenure_months", "sprint_goal_clarity", "stakeholder_changes",
]
TARGET = "delayed"

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"   Train: {len(X_train)}  |  Test: {len(X_test)}")
print(f"   Delay rate — Train: {y_train.mean():.1%}  |  Test: {y_test.mean():.1%}")


# ── MODELS ─────────────────────────────────────────────────────────────────────

print("\n── Training models ──")

models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  LogisticRegression(max_iter=1000, random_state=42)),
    ]),
    "Random Forest": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  RandomForestClassifier(n_estimators=200, max_depth=8,
                                           random_state=42, n_jobs=-1)),
    ]),
    "Gradient Boosting": Pipeline([
        ("scaler", StandardScaler()),
        ("model",  GradientBoostingClassifier(n_estimators=200, max_depth=4,
                                               learning_rate=0.05, random_state=42)),
    ]),
}

results = {}
for name, pipeline in models.items():
    pipeline.fit(X_train, y_train)
    y_pred  = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)
    cv_auc  = cross_val_score(pipeline, X, y, cv=5, scoring="roc_auc").mean()
    report  = classification_report(y_test, y_pred, output_dict=True)

    results[name] = {
        "pipeline":  pipeline,
        "y_pred":    y_pred,
        "y_proba":   y_proba,
        "auc":       auc,
        "cv_auc":    cv_auc,
        "precision": report["1"]["precision"],
        "recall":    report["1"]["recall"],
        "f1":        report["1"]["f1-score"],
        "cm":        confusion_matrix(y_test, y_pred),
    }
    print(f"   {name:25s}  AUC={auc:.3f}  CV-AUC={cv_auc:.3f}  "
          f"F1={report['1']['f1-score']:.3f}")


# ── 1. ROC CURVES ──────────────────────────────────────────────────────────────

print("\n── 1. ROC curves ──")
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_title("ROC Curves — All Models")

ax.plot([0, 1], [0, 1], color="#CCCCCC", linestyle="--", linewidth=1, label="Random (AUC=0.50)")

short = {"Logistic Regression": "lr", "Random Forest": "rf", "Gradient Boosting": "gb"}
for name, res in results.items():
    fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
    ax.plot(fpr, tpr, color=COLOURS[short[name]], linewidth=2.2,
            label=f"{name} (AUC={res['auc']:.3f})")

ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.legend(fontsize=10, framealpha=0.7)
ax.set_xlim(-0.01, 1.01)
ax.set_ylim(-0.01, 1.01)

save("01_roc_curves")


# ── 2. MODEL COMPARISON ────────────────────────────────────────────────────────

print("\n── 2. Model comparison ──")
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle("Model Performance Comparison", fontsize=14, fontweight="bold", color="#222222")

metric_data = {
    "ROC-AUC":  {n: r["auc"]       for n, r in results.items()},
    "Precision": {n: r["precision"] for n, r in results.items()},
    "Recall":    {n: r["recall"]    for n, r in results.items()},
}

for ax, (metric, vals) in zip(axes, metric_data.items()):
    names  = list(vals.keys())
    values = list(vals.values())
    cols   = [COLOURS[short[n]] for n in names]
    bars   = ax.bar(names, values, color=cols, alpha=0.82, width=0.5)
    ax.set_ylim(0, 1.1)
    ax.set_title(metric)
    ax.set_ylabel("Score")
    ax.set_xticklabels([n.replace(" ", "\n") for n in names], fontsize=9)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", fontsize=9, color="#444444")

save("02_model_comparison")


# ── 3. CONFUSION MATRICES ──────────────────────────────────────────────────────

print("\n── 3. Confusion matrices ──")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
fig.suptitle("Confusion Matrices (Test Set)", fontsize=14, fontweight="bold", color="#222222")

for ax, (name, res) in zip(axes, results.items()):
    disp = ConfusionMatrixDisplay(res["cm"], display_labels=["On Track", "Delayed"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title(name, fontsize=11)
    ax.grid(False)

save("03_confusion_matrices")


# ── 4. FEATURE IMPORTANCE ─────────────────────────────────────────────────────

print("\n── 4. Feature importance ──")
rf_model     = results["Random Forest"]["pipeline"].named_steps["model"]
importances  = rf_model.feature_importances_
feat_imp     = pd.Series(importances, index=FEATURES).sort_values(ascending=True)

# Human-readable labels
labels = {
    "team_size":              "Team size",
    "sprint_number":          "Sprint number",
    "committed_points":       "Committed points",
    "scope_change_pct":       "Scope change %",
    "dependency_count":       "Dependency count",
    "tech_debt_hrs":          "Tech debt (hrs)",
    "key_person_risk":        "Key person risk",
    "unplanned_work_pct":     "Unplanned work %",
    "prev_sprint_carryover":  "Prev. carryover",
    "team_tenure_months":     "Team tenure",
    "sprint_goal_clarity":    "Goal clarity",
    "stakeholder_changes":    "Stakeholder changes",
}
feat_imp.index = [labels[f] for f in feat_imp.index]

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Feature Importance — Random Forest\n(higher = stronger predictor of sprint delay)",
             fontweight="bold", color="#222222")

colours_bar = ["#E5484D" if v > feat_imp.mean() else "#0091FF" for v in feat_imp.values]
ax.barh(feat_imp.index, feat_imp.values, color=colours_bar, alpha=0.82, height=0.6)
ax.axvline(feat_imp.mean(), color="#888888", linestyle="--", linewidth=1,
           label=f"Mean importance ({feat_imp.mean():.3f})")
ax.set_xlabel("Feature importance (Gini)")
ax.legend(fontsize=9)

red_patch   = mpatches.Patch(color="#E5484D", alpha=0.82, label="Above average importance")
blue_patch  = mpatches.Patch(color="#0091FF", alpha=0.82, label="Below average importance")
ax.legend(handles=[red_patch, blue_patch], fontsize=9, framealpha=0.6)

save("04_feature_importance")


# ── 5. RISK SCORE DISTRIBUTION ────────────────────────────────────────────────

print("\n── 5. Risk score distribution ──")
best_proba = results["Gradient Boosting"]["y_proba"]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Risk Score Distribution — Gradient Boosting", fontsize=14,
             fontweight="bold", color="#222222")

# Histogram by actual outcome
ax = axes[0]
mask_ok    = y_test == 0
mask_delay = y_test == 1
ax.hist(best_proba[mask_ok],    bins=20, alpha=0.65, color="#30A46C", label="On track (actual)")
ax.hist(best_proba[mask_delay], bins=20, alpha=0.65, color="#E5484D", label="Delayed (actual)")
ax.axvline(0.5, color="#888888", linestyle="--", linewidth=1.2, label="Decision threshold (0.5)")
ax.set_xlabel("Predicted probability of delay")
ax.set_ylabel("Count")
ax.set_title("Predicted Risk Score by Actual Outcome")
ax.legend(fontsize=9, framealpha=0.6)

# Risk banding
ax = axes[1]
bands = pd.cut(best_proba, bins=[0, 0.33, 0.66, 1.0],
               labels=["Low risk\n(0–33%)", "Medium risk\n(33–66%)", "High risk\n(66–100%)"])
delay_by_band = pd.DataFrame({"band": bands, "delayed": y_test.values})
rates = delay_by_band.groupby("band", observed=True)["delayed"].mean() * 100
counts = delay_by_band.groupby("band", observed=True)["delayed"].count()

cols = ["#30A46C", "#F76B15", "#E5484D"]
bars = ax.bar(rates.index, rates.values, color=cols, alpha=0.82, width=0.5)
ax.set_title("Actual Delay Rate by Predicted Risk Band")
ax.set_ylabel("Actual delay rate (%)")
ax.set_ylim(0, 100)
for bar, (rate, count) in zip(bars, zip(rates.values, counts.values)):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f"{rate:.0f}%\n(n={count})", ha="center", fontsize=9, color="#444444")

save("05_risk_score_distribution")


# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────

print("\n── Final results ──")
best = max(results.items(), key=lambda x: x[1]["auc"])
print(f"\n  Best model: {best[0]}")
print(f"  AUC:        {best[1]['auc']:.3f}")
print(f"  Precision:  {best[1]['precision']:.3f}")
print(f"  Recall:     {best[1]['recall']:.3f}")
print(f"  F1:         {best[1]['f1']:.3f}")
print(f"\n  Top 3 delay predictors (Random Forest):")
rf_imp = pd.Series(
    results["Random Forest"]["pipeline"].named_steps["model"].feature_importances_,
    index=FEATURES
).sort_values(ascending=False)
for feat, imp in rf_imp.head(3).items():
    print(f"    {labels[feat]:30s}  importance={imp:.4f}")

print("\n✅ All charts saved to outputs/charts/\n")
