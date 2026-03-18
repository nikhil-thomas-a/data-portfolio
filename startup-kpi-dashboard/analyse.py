"""
Startup KPI Dashboard — Analysis
==================================
Full analysis of 24 months of SaaS KPI data.
Covers revenue growth, retention, unit economics, product engagement, and support health.

Sections:
  1. Revenue trajectory (MRR, ARR, growth rate)
  2. Customer growth and churn
  3. Retention metrics (GRR, NRR)
  4. Unit economics (CAC, LTV, LTV:CAC, payback)
  5. Product engagement (DAU/MAU)
  6. Support health
  7. Executive summary dashboard

Outputs all charts to outputs/charts/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("outputs/charts", exist_ok=True)

# ── STYLE ──────────────────────────────────────────────────────────────────────

C = {
    "mrr":    "#0091FF",
    "arr":    "#30A46C",
    "churn":  "#E5484D",
    "nrr":    "#8E4EC6",
    "cac":    "#F76B15",
    "ltv":    "#30A46C",
    "engage": "#0091FF",
    "dark":   "#1A1A2E",
    "muted":  "#888888",
    "grid":   "#EEEEEE",
}

plt.rcParams.update({
    "figure.facecolor":   "#FAFAFA",
    "axes.facecolor":     "#FAFAFA",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": False,
    "axes.grid":          True,
    "grid.color":         C["grid"],
    "grid.linewidth":     0.8,
    "font.family":        "sans-serif",
    "font.size":          11,
    "axes.titlesize":     13,
    "axes.titleweight":   "bold",
    "axes.labelcolor":    "#444444",
    "xtick.color":        "#888888",
    "ytick.color":        "#888888",
    "xtick.labelsize":    9,
    "ytick.labelsize":    9,
})

def save(name):
    plt.tight_layout()
    plt.savefig(f"outputs/charts/{name}.png", dpi=150, bbox_inches="tight",
                facecolor="#FAFAFA")
    plt.close()
    print(f"  ✅ {name}.png")

def gbp(x, _): return f"£{x/1000:.0f}k"
def pct(x, _): return f"{x:.0f}%"


# ── LOAD ───────────────────────────────────────────────────────────────────────

print("\n── Loading data ──")
df = pd.read_csv("data/kpi_monthly.csv")
df["month_dt"] = pd.to_datetime(df["month"])
x  = range(len(df))
xl = df["month"].tolist()
xt = list(range(0, len(df), 3))   # quarterly x-ticks

print(f"   {len(df)} months  |  MRR £{df['mrr'].iloc[0]:,.0f} → £{df['mrr'].iloc[-1]:,.0f}")
print(f"   ARR £{df['arr'].iloc[0]:,.0f} → £{df['arr'].iloc[-1]:,.0f}")
print(f"   Customers {df['customers'].iloc[0]} → {df['customers'].iloc[-1]}")


# ── 1. REVENUE TRAJECTORY ─────────────────────────────────────────────────────

print("\n── 1. Revenue trajectory ──")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Revenue Growth — 24 Months", fontsize=14, fontweight="bold", color="#222222")

# MRR + waterfall components
ax = axes[0]
ax.fill_between(x, df["mrr"], alpha=0.12, color=C["mrr"])
ax.plot(x, df["mrr"], color=C["mrr"], linewidth=2.5, label="MRR")
ax.bar(x, df["new_mrr"], bottom=0, alpha=0.3, color=C["arr"], width=0.6, label="New MRR")
ax.bar(x, -df["churned_mrr"], alpha=0.3, color=C["churn"], width=0.6, label="Churned MRR")
ax.set_title("MRR with New vs Churned")
ax.set_ylabel("£")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(gbp))
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9, framealpha=0.6)

# MoM growth rate
ax2 = axes[1]
colours_bar = [C["arr"] if v >= 0 else C["churn"] for v in df["mom_growth_pct"]]
ax2.bar(x, df["mom_growth_pct"], color=colours_bar, alpha=0.8, width=0.7)
ax2.axhline(df["mom_growth_pct"].mean(), color=C["muted"], linewidth=1.2,
            linestyle="--", label=f"Mean {df['mom_growth_pct'].mean():.1f}%")
ax2.set_title("Month-on-Month Growth Rate (%)")
ax2.set_ylabel("%")
ax2.set_xticks(xt)
ax2.set_xticklabels([xl[i] for i in xt], rotation=30)
ax2.legend(fontsize=9, framealpha=0.6)

save("01_revenue_trajectory")


# ── 2. CUSTOMER GROWTH & CHURN ────────────────────────────────────────────────

print("\n── 2. Customer growth & churn ──")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Customer Growth & Churn", fontsize=14, fontweight="bold", color="#222222")

ax = axes[0]
ax.fill_between(x, df["customers"], alpha=0.12, color=C["mrr"])
ax.plot(x, df["customers"], color=C["mrr"], linewidth=2.5, label="Total customers")
ax2_twin = ax.twinx()
ax2_twin.bar(x, df["new_customers"], alpha=0.35, color=C["arr"], width=0.6, label="New")
ax2_twin.bar(x, -df["churned_customers"], alpha=0.35, color=C["churn"], width=0.6, label="Churned")
ax2_twin.set_ylabel("New / Churned per month", color=C["muted"])
ax2_twin.tick_params(axis="y", colors=C["muted"])
ax2_twin.spines["right"].set_visible(False)
ax.set_title("Total Customers + Monthly Movements")
ax.set_ylabel("Total customers")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9, framealpha=0.6)

ax = axes[1]
ax.fill_between(x, df["logo_churn_pct"], alpha=0.15, color=C["churn"])
ax.plot(x, df["logo_churn_pct"], color=C["churn"], linewidth=2, label="Logo churn %")
ax.axhline(2.0, color=C["muted"], linewidth=1, linestyle=":", label="2% benchmark")
ax.set_title("Monthly Logo Churn Rate (%)")
ax.set_ylabel("%")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9, framealpha=0.6)

save("02_customer_churn")


# ── 3. RETENTION: GRR & NRR ───────────────────────────────────────────────────

print("\n── 3. Retention metrics ──")
fig, ax = plt.subplots(figsize=(12, 5))
ax.set_title("Revenue Retention — GRR vs NRR  (100% = perfect retention, >100% = expansion)",
             fontweight="bold", color="#222222")

ax.fill_between(x, df["nrr_pct"], 100, where=df["nrr_pct"] >= 100,
                alpha=0.15, color=C["arr"], label="Expansion zone (NRR > 100%)")
ax.fill_between(x, df["grr_pct"], 100, where=df["grr_pct"] < 100,
                alpha=0.12, color=C["churn"], label="Churn drag (GRR < 100%)")
ax.plot(x, df["nrr_pct"], color=C["nrr"], linewidth=2.5, label=f"NRR (avg {df['nrr_pct'].mean():.0f}%)")
ax.plot(x, df["grr_pct"], color=C["mrr"], linewidth=2, linestyle="--",
        label=f"GRR (avg {df['grr_pct'].mean():.0f}%)")
ax.axhline(100, color="#AAAAAA", linewidth=1, linestyle="-")
ax.axhline(110, color=C["arr"], linewidth=0.8, linestyle=":", alpha=0.6, label="110% NRR target")
ax.set_ylabel("%")
ax.set_ylim(75, 135)
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9, framealpha=0.6, loc="lower right")

save("03_retention_grr_nrr")


# ── 4. UNIT ECONOMICS ─────────────────────────────────────────────────────────

print("\n── 4. Unit economics ──")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Unit Economics", fontsize=14, fontweight="bold", color="#222222")

# LTV:CAC
ax = axes[0]
colours_ltvcac = [C["arr"] if v >= 3 else C["churn"] for v in df["ltv_cac_ratio"]]
ax.bar(x, df["ltv_cac_ratio"], color=colours_ltvcac, alpha=0.8, width=0.7)
ax.axhline(3.0, color=C["muted"], linewidth=1.5, linestyle="--", label="3:1 benchmark")
ax.set_title("LTV:CAC Ratio")
ax.set_ylabel("Ratio")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9)

# CAC over time
ax = axes[1]
ax.fill_between(x, df["cac"], alpha=0.12, color=C["cac"])
ax.plot(x, df["cac"], color=C["cac"], linewidth=2.2)
ax.set_title("Customer Acquisition Cost (£)")
ax.set_ylabel("£")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"£{v:,.0f}"))
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)

# Payback period
ax = axes[2]
ax.fill_between(x, df["payback_months"], alpha=0.12, color=C["nrr"])
ax.plot(x, df["payback_months"], color=C["nrr"], linewidth=2.2)
ax.axhline(12, color=C["muted"], linewidth=1, linestyle="--", label="12-month benchmark")
ax.set_title("CAC Payback Period (months)")
ax.set_ylabel("Months")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9)

save("04_unit_economics")


# ── 5. PRODUCT ENGAGEMENT ─────────────────────────────────────────────────────

print("\n── 5. Product engagement ──")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Product Engagement", fontsize=14, fontweight="bold", color="#222222")

ax = axes[0]
ax.fill_between(x, df["mau"], alpha=0.12, color=C["engage"])
ax.plot(x, df["mau"], color=C["engage"], linewidth=2.2, label="MAU")
ax2t = ax.twinx()
ax2t.plot(x, df["dau_mau_ratio"] * 100, color=C["nrr"], linewidth=2,
          linestyle="--", label="DAU/MAU %")
ax2t.set_ylabel("DAU/MAU %", color=C["nrr"])
ax2t.tick_params(axis="y", colors=C["nrr"])
ax2t.spines["right"].set_visible(False)
ax.set_title("Monthly Active Users + DAU/MAU Ratio")
ax.set_ylabel("Users")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
lines1, l1 = ax.get_legend_handles_labels()
lines2, l2 = ax2t.get_legend_handles_labels()
ax.legend(lines1 + lines2, l1 + l2, fontsize=9, framealpha=0.6)

ax = axes[1]
ax.fill_between(x, df["feature_adoption"] * 100, alpha=0.15, color=C["arr"])
ax.plot(x, df["feature_adoption"] * 100, color=C["arr"], linewidth=2.2)
ax.set_title("Feature Adoption Rate (%)")
ax.set_ylabel("%")
ax.set_ylim(0, 100)
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)

save("05_product_engagement")


# ── 6. SUPPORT HEALTH ─────────────────────────────────────────────────────────

print("\n── 6. Support health ──")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Support Health", fontsize=14, fontweight="bold", color="#222222")

ax = axes[0]
ax.bar(x, df["support_tickets"], color=C["mrr"], alpha=0.7, width=0.7)
ax.plot(x, df["avg_response_hrs"] * 5, color=C["cac"], linewidth=2,
        label="Avg response time (scaled)")
ax.set_title("Support Tickets + Response Time")
ax.set_ylabel("Tickets / month")
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9)

ax = axes[1]
ax.fill_between(x, df["csat_score"], alpha=0.15, color=C["arr"])
ax.plot(x, df["csat_score"], color=C["arr"], linewidth=2.2)
ax.axhline(4.0, color=C["muted"], linewidth=1, linestyle="--", label="4.0 benchmark")
ax.set_title("CSAT Score (out of 5)")
ax.set_ylabel("Score")
ax.set_ylim(3.0, 5.0)
ax.set_xticks(xt)
ax.set_xticklabels([xl[i] for i in xt], rotation=30)
ax.legend(fontsize=9)

save("06_support_health")


# ── 7. EXECUTIVE SUMMARY DASHBOARD ────────────────────────────────────────────

print("\n── 7. Executive summary dashboard ──")
latest = df.iloc[-1]
prev   = df.iloc[-2]

def delta(col, fmt="£"):
    v, p = latest[col], prev[col]
    chg  = v - p
    pct  = chg / abs(p) * 100 if p != 0 else 0
    sign = "+" if chg >= 0 else ""
    if fmt == "£": return f"{sign}£{chg:,.0f} ({sign}{pct:.1f}%)"
    return f"{sign}{chg:.1f} ({sign}{pct:.1f}%)"

fig = plt.figure(figsize=(16, 9))
fig.suptitle(f"Executive KPI Dashboard — {latest['month']}",
             fontsize=16, fontweight="bold", color="#222222", y=0.98)

metrics = [
    ("MRR",          f"£{latest['mrr']:,.0f}",            delta("mrr"),      C["mrr"]),
    ("ARR",          f"£{latest['arr']:,.0f}",             delta("arr"),      C["arr"]),
    ("Customers",    f"{latest['customers']}",              f"+{latest['new_customers']} new", C["mrr"]),
    ("NRR",          f"{latest['nrr_pct']:.0f}%",          f"GRR: {latest['grr_pct']:.0f}%", C["nrr"]),
    ("LTV:CAC",      f"{latest['ltv_cac_ratio']:.1f}x",    f"Payback: {latest['payback_months']:.0f}mo", C["cac"]),
    ("DAU/MAU",      f"{latest['dau_mau_ratio']*100:.0f}%", f"MAU: {latest['mau']:,}", C["engage"]),
    ("CSAT",         f"{latest['csat_score']:.1f}/5",       f"Tickets: {latest['support_tickets']}", C["arr"]),
    ("MoM Growth",   f"{latest['mom_growth_pct']:.1f}%",   f"Avg: {df['mom_growth_pct'].mean():.1f}%", C["mrr"]),
]

for i, (label, value, sub, colour) in enumerate(metrics):
    ax = fig.add_subplot(2, 4, i + 1)
    ax.set_facecolor("#FAFAFA")
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])

    ax.add_patch(plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=True,
                                facecolor=colour + "10", edgecolor=colour + "30",
                                linewidth=1.5, transform=ax.transAxes))
    ax.text(0.5, 0.75, label, transform=ax.transAxes, ha="center",
            fontsize=10, color="#888888", fontweight="normal")
    ax.text(0.5, 0.48, value, transform=ax.transAxes, ha="center",
            fontsize=20, color=colour, fontweight="bold")
    ax.text(0.5, 0.22, sub, transform=ax.transAxes, ha="center",
            fontsize=9, color="#888888")

save("07_executive_dashboard")


# ── SUMMARY ───────────────────────────────────────────────────────────────────

print("\n── Summary ──")
print(f"  Final MRR:      £{df['mrr'].iloc[-1]:,.0f}")
print(f"  Final ARR:      £{df['arr'].iloc[-1]:,.0f}")
print(f"  MRR growth:     {((df['mrr'].iloc[-1]/df['mrr'].iloc[0])-1)*100:.0f}% over 24 months")
print(f"  Avg NRR:        {df['nrr_pct'].mean():.1f}%")
print(f"  Avg LTV:CAC:    {df['ltv_cac_ratio'].mean():.1f}x")
print(f"  Final CSAT:     {df['csat_score'].iloc[-1]:.1f}/5")
print("\n✅ All charts saved to outputs/charts/\n")
