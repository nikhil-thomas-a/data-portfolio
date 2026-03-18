"""
Delivery Risk Predictor — Data Generator
==========================================
Generates labelled sprint data for a binary classification model.
Target: will this sprint be delayed? (1 = delayed, 0 = on track)

Features generated per sprint:
  - team_size, sprint_number, committed_points
  - scope_change_pct    (% of committed points added mid-sprint)
  - dependency_count    (external dependencies this sprint)
  - tech_debt_hrs       (estimated tech debt hours in sprint)
  - key_person_risk     (1 if key person flagged as risk)
  - unplanned_work_pct  (% of capacity consumed by unplanned work)
  - prev_sprint_carryover (carryover from last sprint)
  - team_tenure_months  (avg team tenure — proxy for maturity)
  - sprint_goal_clarity (1-5 score, rated at planning)
  - stakeholder_changes (number of stakeholder direction changes)
  - delayed             (target: 1 = sprint ended with >20% carryover)

Run this before running train.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(99)

N = 600   # total sprints


def generate():
    os.makedirs("data", exist_ok=True)

    rows = []
    for i in range(N):
        # Team characteristics
        team_size        = np.random.randint(3, 10)
        sprint_number    = np.random.randint(1, 50)
        team_tenure      = max(1, np.random.normal(14, 8))       # months

        # Sprint inputs
        committed        = np.random.randint(20, 80)
        scope_change_pct = max(0, np.random.exponential(8))       # usually low, occasionally high
        dependency_count = np.random.poisson(1.8)
        tech_debt_hrs    = max(0, np.random.exponential(6))
        key_person_risk  = int(np.random.random() < 0.15)
        unplanned_pct    = max(0, np.random.beta(2, 8) * 100)
        prev_carryover   = max(0, np.random.exponential(5))
        goal_clarity     = np.random.randint(1, 6)                # 1=vague, 5=crystal clear
        stakeholder_chg  = np.random.poisson(0.6)

        # ── Build delay probability from features ─────────────────────────
        # Each feature adds to a log-odds of delay
        log_odds = (
            -1.5                                   # base (most sprints succeed)
            + scope_change_pct  * 0.08             # scope creep is bad
            + dependency_count  * 0.30             # dependencies add risk
            + tech_debt_hrs     * 0.06             # tech debt slows teams
            + key_person_risk   * 1.20             # key person risk is large
            + unplanned_pct     * 0.04             # unplanned work disrupts
            + prev_carryover    * 0.12             # carryover compounds
            - goal_clarity      * 0.25             # clarity helps
            + stakeholder_chg   * 0.45             # direction changes hurt
            - team_tenure       * 0.03             # experienced teams cope better
            + np.random.normal(0, 0.5)             # noise
        )
        prob_delay = 1 / (1 + np.exp(-log_odds))
        delayed    = int(np.random.random() < prob_delay)

        rows.append({
            "sprint_id":            i + 1,
            "team_size":            team_size,
            "sprint_number":        sprint_number,
            "committed_points":     committed,
            "scope_change_pct":     round(scope_change_pct, 2),
            "dependency_count":     dependency_count,
            "tech_debt_hrs":        round(tech_debt_hrs, 1),
            "key_person_risk":      key_person_risk,
            "unplanned_work_pct":   round(unplanned_pct, 2),
            "prev_sprint_carryover":round(prev_carryover, 1),
            "team_tenure_months":   round(team_tenure, 1),
            "sprint_goal_clarity":  goal_clarity,
            "stakeholder_changes":  stakeholder_chg,
            "delayed":              delayed,
        })

    df  = pd.DataFrame(rows)
    df.to_csv("data/sprints_labelled.csv", index=False)

    delay_rate = df["delayed"].mean()
    print(f"✅ Generated {N} labelled sprints")
    print(f"   Delay rate: {delay_rate:.1%}  ({df['delayed'].sum()} delayed / {N} total)")
    print(f"\n{df.head(5).to_string()}")
    return df


if __name__ == "__main__":
    generate()
