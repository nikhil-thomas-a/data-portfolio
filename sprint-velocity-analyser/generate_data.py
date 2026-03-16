"""
Sprint Velocity Analyser — Data Generator
==========================================
Generates realistic synthetic sprint data for a 3-team startup over 18 months.

Each team has different characteristics:
  - Team Alpha:  Stable senior team, consistent velocity
  - Team Beta:   Growing team, improving over time with occasional disruption
  - Team Gamma:  New team, high variance, learning curve visible in data

Run this once to create data/sprints.csv before running the analysis.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
import os

np.random.seed(42)

# ── CONFIG ─────────────────────────────────────────────────────────────────────

TEAMS = {
    "Alpha": {
        "base_velocity": 52,
        "std":           6,
        "trend":         0.0,     # stable
        "churn_rate":    0.05,    # low churn
    },
    "Beta": {
        "base_velocity": 34,
        "std":           9,
        "trend":         0.4,     # improving
        "churn_rate":    0.12,
    },
    "Gamma": {
        "base_velocity": 24,
        "std":           12,
        "trend":         0.6,     # steeper learning curve
        "churn_rate":    0.20,    # high early churn
    },
}

NUM_SPRINTS    = 36    # 18 months of 2-week sprints
SPRINT_DAYS    = 14
START_DATE     = date(2024, 1, 8)

BLOCKERS       = ["None", "Dependency delay", "Tech debt", "Scope change",
                  "Key person absent", "Infrastructure issue", "External API issue"]
BLOCKER_IMPACT = {"None": 0, "Dependency delay": -8, "Tech debt": -6,
                  "Scope change": -10, "Key person absent": -12,
                  "Infrastructure issue": -7, "External API issue": -5}

# ── GENERATORS ─────────────────────────────────────────────────────────────────

def gen_team_sprints(team_name, cfg):
    rows = []
    for i in range(NUM_SPRINTS):
        sprint_start = START_DATE + timedelta(days=i * SPRINT_DAYS)
        sprint_end   = sprint_start + timedelta(days=SPRINT_DAYS - 1)
        sprint_num   = i + 1

        # Trend + noise
        trend_boost   = cfg["trend"] * i
        base          = cfg["base_velocity"] + trend_boost
        committed     = max(10, int(np.random.normal(base, cfg["std"])))

        # Team size varies with churn
        team_size = max(3, int(np.random.normal(6, 1)))
        if np.random.random() < cfg["churn_rate"]:
            team_size = max(3, team_size - 1)

        # Blocker
        blocker_probs = [0.45, 0.12, 0.10, 0.12, 0.08, 0.07, 0.06]
        blocker       = np.random.choice(BLOCKERS, p=blocker_probs)
        blocker_hit   = BLOCKER_IMPACT[blocker]

        # Scope creep
        scope_added = 0
        if np.random.random() < 0.30:
            scope_added = np.random.randint(2, 10)

        # Completed = committed + scope_added + blocker impact + noise
        noise     = np.random.normal(0, 3)
        completed = max(0, int(committed + scope_added + blocker_hit + noise))
        completed = min(completed, committed + scope_added + 5)  # can't complete far over scope

        # Carryover
        carryover = max(0, (committed + scope_added) - completed)

        # Bugs reported during sprint
        bugs = max(0, int(np.random.poisson(2 + (carryover * 0.3))))

        # Unplanned work (% of sprint)
        unplanned_pct = round(np.random.beta(2, 8) * 100, 1)

        # Ceremonies time (hours)
        planning_hrs  = round(np.random.normal(3.0, 0.5), 1)
        retro_hrs     = round(np.random.normal(1.5, 0.3), 1)
        standup_hrs   = round(team_size * SPRINT_DAYS * 0.25, 1)  # ~15min per person per day

        # Predictability score (completed / committed, capped 0-1)
        predictability = round(min(1.0, completed / max(1, committed)), 3)

        rows.append({
            "team":             team_name,
            "sprint_number":    sprint_num,
            "sprint_start":     sprint_start.isoformat(),
            "sprint_end":       sprint_end.isoformat(),
            "team_size":        team_size,
            "committed_points": committed,
            "scope_added":      scope_added,
            "completed_points": completed,
            "carryover_points": carryover,
            "velocity":         completed,           # velocity = completed points
            "predictability":   predictability,
            "primary_blocker":  blocker,
            "bugs_reported":    bugs,
            "unplanned_pct":    unplanned_pct,
            "planning_hrs":     planning_hrs,
            "retro_hrs":        retro_hrs,
            "standup_hrs":      standup_hrs,
        })
    return rows


def main():
    os.makedirs("data", exist_ok=True)
    all_rows = []
    for team, cfg in TEAMS.items():
        all_rows.extend(gen_team_sprints(team, cfg))

    df = pd.DataFrame(all_rows)
    df = df.sort_values(["team", "sprint_number"]).reset_index(drop=True)
    df.to_csv("data/sprints.csv", index=False)

    print(f"✅ Generated {len(df)} sprint records across {df['team'].nunique()} teams")
    print(f"   Date range: {df['sprint_start'].min()} → {df['sprint_end'].max()}")
    print(f"\nShape: {df.shape}")
    print(df.head(6).to_string())


if __name__ == "__main__":
    main()
