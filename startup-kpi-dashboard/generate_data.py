"""
Startup KPI Dashboard — Data Generator
=======================================
Generates 24 months of realistic SaaS startup KPI data for a B2B SaaS product
moving from early traction to growth stage.

Metrics generated:
  Revenue:    MRR, ARR, new MRR, expansion MRR, churned MRR
  Growth:     MoM growth rate, ARR growth rate
  Customers:  Total, new, churned, net new
  Retention:  Gross revenue retention, net revenue retention, logo churn rate
  Efficiency: CAC, LTV, LTV:CAC ratio, payback period (months)
  Product:    DAU, MAU, DAU/MAU ratio, feature adoption rate
  Support:    Tickets opened, avg response time (hrs), CSAT score

Run this once before running the dashboard analysis.
"""

import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
import os

np.random.seed(7)

# ── CONFIG ─────────────────────────────────────────────────────────────────────

START_DATE     = date(2023, 1, 1)
MONTHS         = 24
STARTING_MRR   = 12_000      # £12k MRR at start
STARTING_CUSTS = 18          # 18 customers at start
AVG_CONTRACT   = 650         # avg monthly contract value (£)

# Growth curve: accelerates in months 8-16, stabilises after
def growth_rate(month):
    if month < 6:   return np.random.normal(0.06, 0.015)   # 6% MoM early
    if month < 14:  return np.random.normal(0.09, 0.020)   # 9% MoM growth phase
    return          np.random.normal(0.07, 0.018)           # 7% MoM maturity

# ── GENERATE ───────────────────────────────────────────────────────────────────

def main():
    os.makedirs("data", exist_ok=True)
    rows = []

    mrr       = STARTING_MRR
    customers = STARTING_CUSTS

    for i in range(MONTHS):
        month_date  = START_DATE + relativedelta(months=i)
        month_label = month_date.strftime("%Y-%m")
        month_num   = i + 1

        # ── Revenue ─────────────────────────────────────────────────────────
        gr          = growth_rate(i)
        new_mrr     = max(500, mrr * gr + np.random.normal(0, 300))
        expansion   = max(0,   mrr * np.random.normal(0.015, 0.005))  # upsell
        churn_rate  = np.random.normal(0.020, 0.005) if i < 12 else np.random.normal(0.015, 0.004)
        churned_mrr = max(0, mrr * churn_rate)

        prev_mrr    = mrr
        mrr         = mrr + new_mrr + expansion - churned_mrr
        arr         = mrr * 12

        mom_growth  = (mrr - prev_mrr) / prev_mrr if prev_mrr > 0 else 0

        # ── Customers ───────────────────────────────────────────────────────
        new_custs     = max(1, int(new_mrr / AVG_CONTRACT))
        churned_custs = max(0, int(round(customers * churn_rate * 0.8)))
        customers     = customers + new_custs - churned_custs
        logo_churn    = churned_custs / max(1, customers) * 100

        # ── Retention ───────────────────────────────────────────────────────
        grr = max(0.70, 1 - churn_rate) * 100                          # gross revenue retention
        nrr = min(130, grr + np.random.normal(8, 2))                   # net revenue retention

        # ── Unit economics ───────────────────────────────────────────────────
        # CAC improves over time as marketing becomes more efficient
        cac         = max(800, np.random.normal(2200 - i * 35, 150))
        ltv         = (AVG_CONTRACT * 12) / (churn_rate * 12)          # LTV = ARPU / churn
        ltv_cac     = ltv / cac
        payback     = cac / max(1, AVG_CONTRACT)                        # months to recover CAC

        # ── Product engagement ───────────────────────────────────────────────
        mau         = int(customers * np.random.normal(3.2, 0.4))      # avg 3.2 users per customer
        dau         = int(mau * np.random.normal(0.38, 0.05))           # DAU/MAU ~38%
        dau_mau     = dau / max(1, mau)
        adoption    = min(0.95, 0.45 + i * 0.018 + np.random.normal(0, 0.03))  # improves over time

        # ── Support ──────────────────────────────────────────────────────────
        tickets     = max(1, int(customers * np.random.normal(1.8, 0.5)))
        response_hr = max(0.5, np.random.normal(5.5 - i * 0.08, 0.8))  # improving response time
        csat        = min(5.0, max(3.0, np.random.normal(4.1 + i * 0.01, 0.2)))

        rows.append({
            "month":            month_label,
            "month_num":        month_num,
            "mrr":              round(mrr, 2),
            "arr":              round(arr, 2),
            "new_mrr":          round(new_mrr, 2),
            "expansion_mrr":    round(expansion, 2),
            "churned_mrr":      round(churned_mrr, 2),
            "mom_growth_pct":   round(mom_growth * 100, 2),
            "customers":        customers,
            "new_customers":    new_custs,
            "churned_customers":churned_custs,
            "logo_churn_pct":   round(logo_churn, 2),
            "grr_pct":          round(grr, 2),
            "nrr_pct":          round(nrr, 2),
            "cac":              round(cac, 2),
            "ltv":              round(ltv, 2),
            "ltv_cac_ratio":    round(ltv_cac, 2),
            "payback_months":   round(payback, 1),
            "mau":              mau,
            "dau":              dau,
            "dau_mau_ratio":    round(dau_mau, 3),
            "feature_adoption": round(adoption, 3),
            "support_tickets":  tickets,
            "avg_response_hrs": round(response_hr, 1),
            "csat_score":       round(csat, 2),
        })

    df = pd.DataFrame(rows)
    df.to_csv("data/kpi_monthly.csv", index=False)

    print(f"✅ Generated {len(df)} months of KPI data")
    print(f"   MRR: £{df.iloc[0]['mrr']:,.0f} → £{df.iloc[-1]['mrr']:,.0f}")
    print(f"   ARR: £{df.iloc[0]['arr']:,.0f} → £{df.iloc[-1]['arr']:,.0f}")
    print(f"   Customers: {df.iloc[0]['customers']} → {df.iloc[-1]['customers']}")
    print(f"\n{df[['month','mrr','customers','nrr_pct','ltv_cac_ratio']].tail(6).to_string()}")


if __name__ == "__main__":
    main()
