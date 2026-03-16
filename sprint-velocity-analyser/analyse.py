"""
Sprint Velocity Analyser — Analysis
=====================================
Full exploratory data analysis of sprint performance across three teams.

Sections:
  1. Data loading & validation
  2. Velocity trends over time
  3. Predictability analysis
  4. Blocker impact analysis
  5. Team size vs velocity correlation
  6. Carryover & scope creep patterns
  7. Key findings summary

Outputs all charts to outputs/charts/
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("outputs/charts", exist_ok=True)

# ── STYLE ──────────────────────────────────────────────────────────────────────

TEAM_COLOURS = {
    "Alpha": "#E5484D",   # red
    "Beta":  "#0091FF",   # blue
    "Gamma": "#30A46C",   # green
}

plt.rcParams.update({
    "figure.facecolor":  "#FAFAFA",
    "axes.facecolor":    "#FAFAFA",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom":False,
    "axes.grid":         True,
    "grid.color":        "#E8E8E8",
    "grid.linewidth":    0.8,
    "font.family":       "sans-serif",
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "axes.labelcolor":   "#444444",
    "xtick.color":       "#888888",
    "ytick.color":       "#888888",
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
})

def save(name):
    plt.tight_layout()
    plt.savefig(f"outputs/charts/{name}.png", dpi=150, bbox_inches="tight",
                facecolor="#FAFAFA")
    plt.close()
    print(f"  ✅ Saved {name}.png")


# ── 1. LOAD & VALIDATE ─────────────────────────────────────────────────────────

print("\n── 1. Loading data ──")
df = pd.read_csv("data/sprints.csv", parse_dates=["sprint_start", "sprint_end"])

print(f"   Rows: {len(df)}  |  Teams: {df['team'].nunique()}  |  "
      f"Sprints per team: {df.groupby('team')['sprint_number'].count().to_dict()}")
print(f"   Date range: {df['sprint_start'].min().date()} → {df['sprint_end'].max().date()}")
print(f"\n   Nulls: {df.isnull().sum().sum()}")
print(f"   Velocity range: {df['velocity'].min()} – {df['velocity'].max()} points")
print(f"   Mean predictability by team:\n{df.groupby('team')['predictability'].mean().round(3)}")


# ── 2. VELOCITY TRENDS ─────────────────────────────────────────────────────────

print("\n── 2. Velocity trends ──")

fig, axes = plt.subplots(3, 1, figsize=(13, 11), sharex=False)
fig.suptitle("Sprint Velocity Over Time — All Teams", fontsize=15, fontweight="bold",
             y=1.01, color="#222222")

for ax, (team, grp) in zip(axes, df.groupby("team")):
    colour = TEAM_COLOURS[team]
    grp = grp.sort_values("sprint_number")
    x   = grp["sprint_number"]
    y   = grp["velocity"]

    # Rolling average (window=4)
    rolling = y.rolling(4, min_periods=2).mean()

    # Trend line
    slope, intercept, r, p, _ = stats.linregress(x, y)
    trend_y = slope * x + intercept

    ax.fill_between(x, y, alpha=0.12, color=colour)
    ax.plot(x, y, color=colour, linewidth=1.5, alpha=0.7, marker="o",
            markersize=3.5, label="Sprint velocity")
    ax.plot(x, rolling, color=colour, linewidth=2.5, linestyle="--",
            label="4-sprint rolling avg")
    ax.plot(x, trend_y, color="#888888", linewidth=1.2, linestyle=":",
            label=f"Trend (slope={slope:+.2f})")

    # Mean line
    mean_v = y.mean()
    ax.axhline(mean_v, color=colour, linewidth=0.8, linestyle="-", alpha=0.4)
    ax.text(x.max() + 0.3, mean_v, f"μ={mean_v:.0f}", color=colour,
            fontsize=8.5, va="center")

    ax.set_title(f"Team {team}", color=colour, pad=6)
    ax.set_ylabel("Story points")
    ax.set_xlabel("Sprint number")
    ax.legend(fontsize=8, loc="lower right", framealpha=0.6)
    ax.set_xlim(0.5, grp["sprint_number"].max() + 1.5)

save("01_velocity_trends")


# ── 3. TEAM COMPARISON ─────────────────────────────────────────────────────────

print("\n── 3. Team comparison ──")

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle("Team Velocity Distribution", fontsize=14, fontweight="bold",
             color="#222222")

metrics = [
    ("velocity",         "Completed story points", "Velocity"),
    ("predictability",   "Completed / Committed",  "Predictability"),
    ("carryover_points", "Points not completed",   "Carryover"),
]

for ax, (col, ylabel, title) in zip(axes, metrics):
    data  = [df[df["team"] == t][col].values for t in TEAM_COLOURS]
    parts = ax.violinplot(data, positions=[1, 2, 3], showmedians=True,
                          showextrema=True)

    for i, (pc, (team, colour)) in enumerate(zip(parts["bodies"], TEAM_COLOURS.items())):
        pc.set_facecolor(colour)
        pc.set_alpha(0.55)

    parts["cmedians"].set_color("#222222")
    parts["cmedians"].set_linewidth(2)
    parts["cmins"].set_color("#AAAAAA")
    parts["cmaxes"].set_color("#AAAAAA")
    parts["cbars"].set_color("#AAAAAA")

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(list(TEAM_COLOURS.keys()))
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Colour x-tick labels
    for tick, colour in zip(ax.get_xticklabels(), TEAM_COLOURS.values()):
        tick.set_color(colour)
        tick.set_fontweight("bold")

save("02_team_comparison")


# ── 4. BLOCKER IMPACT ──────────────────────────────────────────────────────────

print("\n── 4. Blocker impact ──")

# Points lost = committed + scope_added - completed  (when negative = over-delivery)
df["points_lost"] = (df["committed_points"] + df["scope_added"]) - df["completed_points"]
df["points_lost"]  = df["points_lost"].clip(lower=0)

blocker_stats = (
    df.groupby("primary_blocker")
      .agg(
          avg_points_lost=("points_lost",  "mean"),
          avg_predictability=("predictability", "mean"),
          frequency=("primary_blocker",  "count"),
      )
      .round(2)
      .sort_values("avg_points_lost", ascending=True)
)

fig, axes = plt.subplots(1, 2, figsize=(13, 6))
fig.suptitle("Blocker Impact on Delivery", fontsize=14, fontweight="bold",
             color="#222222")

# Chart A: Avg points lost per blocker
colours_bar = ["#30A46C" if b == "None" else "#E5484D"
               for b in blocker_stats.index]
axes[0].barh(blocker_stats.index, blocker_stats["avg_points_lost"],
             color=colours_bar, edgecolor="none", height=0.6)
axes[0].set_xlabel("Avg story points lost per sprint")
axes[0].set_title("Average Points Lost by Blocker Type")
for i, (val, label) in enumerate(zip(blocker_stats["avg_points_lost"],
                                      blocker_stats.index)):
    axes[0].text(val + 0.1, i, f"{val:.1f}", va="center", fontsize=9,
                 color="#444444")

# Chart B: Frequency heatmap (team × blocker)
pivot = df.groupby(["team", "primary_blocker"])["sprint_number"].count().unstack(fill_value=0)
sns.heatmap(pivot, ax=axes[1], cmap="YlOrRd", annot=True, fmt="d",
            linewidths=0.5, linecolor="#F0F0F0", cbar_kws={"label": "Occurrences"},
            annot_kws={"size": 9})
axes[1].set_title("Blocker Frequency by Team")
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].tick_params(axis="x", rotation=35)

save("03_blocker_impact")


# ── 5. TEAM SIZE vs VELOCITY ────────────────────────────────────────────────────

print("\n── 5. Team size vs velocity ──")

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Team Size vs Velocity — Does Bigger = Faster?", fontweight="bold",
             color="#222222")

for team, grp in df.groupby("team"):
    colour = TEAM_COLOURS[team]
    slope, intercept, r, p, _ = stats.linregress(grp["team_size"], grp["velocity"])
    x_range = np.linspace(grp["team_size"].min(), grp["team_size"].max(), 100)

    ax.scatter(grp["team_size"], grp["velocity"], color=colour, alpha=0.55,
               s=45, zorder=3, label=f"Team {team}")
    ax.plot(x_range, slope * x_range + intercept, color=colour,
            linewidth=1.8, linestyle="--", alpha=0.7)
    ax.text(grp["team_size"].max() + 0.05, slope * grp["team_size"].max() + intercept,
            f"r={r:.2f}", color=colour, fontsize=8.5)

ax.set_xlabel("Team size (people)")
ax.set_ylabel("Velocity (story points)")
ax.legend(framealpha=0.6)

# Annotation
ax.text(0.02, 0.97,
        "Note: correlation between team size and velocity varies by team maturity.",
        transform=ax.transAxes, fontsize=8.5, color="#888888", va="top")

save("04_teamsize_vs_velocity")


# ── 6. CARRYOVER & SCOPE CREEP ─────────────────────────────────────────────────

print("\n── 6. Carryover & scope creep ──")

fig, axes = plt.subplots(2, 1, figsize=(13, 9))
fig.suptitle("Carryover & Scope Creep Patterns", fontsize=14, fontweight="bold",
             color="#222222")

# Chart A: Carryover over time per team
for team, grp in df.groupby("team"):
    grp = grp.sort_values("sprint_number")
    colour = TEAM_COLOURS[team]
    axes[0].plot(grp["sprint_number"], grp["carryover_points"], color=colour,
                 linewidth=1.6, marker="o", markersize=3, alpha=0.8, label=f"Team {team}")
    axes[0].fill_between(grp["sprint_number"], grp["carryover_points"],
                          alpha=0.08, color=colour)

axes[0].set_ylabel("Carryover (story points)")
axes[0].set_xlabel("Sprint number")
axes[0].set_title("Carryover Points Per Sprint")
axes[0].legend(framealpha=0.6)
axes[0].axhline(df["carryover_points"].mean(), color="#AAAAAA", linewidth=1,
                linestyle=":", label="Overall mean")

# Chart B: Scope creep frequency
scope_df = df[df["scope_added"] > 0].groupby("team").agg(
    sprints_with_scope=("scope_added", "count"),
    avg_scope_added=("scope_added", "mean"),
).reset_index()

x  = np.arange(len(scope_df))
w  = 0.35
b1 = axes[1].bar(x - w/2, scope_df["sprints_with_scope"], w,
                  color=[TEAM_COLOURS[t] for t in scope_df["team"]],
                  alpha=0.8, label="Sprints affected")
b2 = axes[1].bar(x + w/2, scope_df["avg_scope_added"], w,
                  color=[TEAM_COLOURS[t] for t in scope_df["team"]],
                  alpha=0.4, label="Avg points added")

axes[1].set_xticks(x)
axes[1].set_xticklabels(scope_df["team"])
axes[1].set_ylabel("Count / Points")
axes[1].set_title("Scope Creep by Team")
axes[1].legend(framealpha=0.6)

for bar in b1:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 str(int(bar.get_height())), ha="center", fontsize=8.5, color="#444444")
for bar in b2:
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                 f"{bar.get_height():.1f}", ha="center", fontsize=8.5, color="#444444")

save("05_carryover_scope")


# ── 7. PREDICTABILITY HEATMAP ──────────────────────────────────────────────────

print("\n── 7. Predictability heatmap ──")

# Quarter x team predictability
df["quarter"] = df["sprint_start"].dt.to_period("Q").astype(str)
pred_pivot = df.groupby(["quarter", "team"])["predictability"].mean().unstack()

fig, ax = plt.subplots(figsize=(11, 4))
sns.heatmap(pred_pivot.T, ax=ax, cmap="RdYlGn", vmin=0.6, vmax=1.0,
            annot=True, fmt=".2f", linewidths=0.5, linecolor="#F0F0F0",
            annot_kws={"size": 10},
            cbar_kws={"label": "Predictability (completed/committed)"})
ax.set_title("Quarterly Predictability by Team  (1.0 = perfect delivery)",
             fontweight="bold", color="#222222", pad=10)
ax.set_xlabel("")
ax.set_ylabel("")
ax.tick_params(axis="x", rotation=30)

save("06_predictability_heatmap")


# ── 8. SUMMARY STATS ───────────────────────────────────────────────────────────

print("\n── 8. Summary statistics ──")

summary = df.groupby("team").agg(
    sprints=("sprint_number", "count"),
    avg_velocity=("velocity", "mean"),
    velocity_std=("velocity", "std"),
    avg_predictability=("predictability", "mean"),
    avg_carryover=("carryover_points", "mean"),
    total_carryover=("carryover_points", "sum"),
    scope_creep_pct=("scope_added", lambda x: (x > 0).mean() * 100),
    avg_bugs=("bugs_reported", "mean"),
).round(2)

print(summary.to_string())
summary.to_csv("outputs/summary_stats.csv")
print("\n  ✅ Saved outputs/summary_stats.csv")


# ── 9. KEY FINDINGS ────────────────────────────────────────────────────────────

print("\n── Key Findings ──────────────────────────────────────────────────────────")

for team in ["Alpha", "Beta", "Gamma"]:
    g = df[df["team"] == team]
    slope, _, r, p, _ = stats.linregress(g["sprint_number"], g["velocity"])
    top_blocker = g[g["primary_blocker"] != "None"]["primary_blocker"].value_counts().index[0]
    print(f"\n  Team {team}:")
    print(f"    Avg velocity:     {g['velocity'].mean():.1f} pts  (σ={g['velocity'].std():.1f})")
    print(f"    Trend:            {slope:+.2f} pts/sprint (r={r:.2f}, p={p:.3f})")
    print(f"    Predictability:   {g['predictability'].mean():.1%}")
    print(f"    Avg carryover:    {g['carryover_points'].mean():.1f} pts")
    print(f"    Top blocker:      {top_blocker}")

print("\n✅ All charts saved to outputs/charts/\n")
