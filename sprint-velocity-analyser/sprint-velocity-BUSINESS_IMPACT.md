# Business Impact — Sprint Velocity Analyser

## The Problem

Sprint velocity is one of the most watched — and most misunderstood — metrics in agile delivery.

Teams and stakeholders react to every dip. A 20% velocity drop triggers retrospectives, management conversations, and sometimes team restructuring. But most velocity variation is **statistical noise, not a signal**. Reacting to noise is expensive and demoralising.

The question this project answers: **Is this velocity change real, or should we just ignore it?**

---

## The Approach

Applied time-series decomposition and statistical significance testing to sprint velocity data.

**Techniques used:**
- Rolling mean + standard deviation to establish velocity baseline and natural variance range
- Mann-Whitney U test to detect statistically significant drops between sprint cohorts
- Decomposition into trend, seasonality (team rhythm), and residual (noise) components
- Correlation analysis between velocity drops and external events (team changes, dependency spikes, holiday periods)

---

## Key Findings

### 1. Most velocity dips are not significant
In simulated 20-sprint programmes, approximately **65–70% of sprint-to-sprint velocity drops fall within 1 standard deviation** of the team's natural variance. They are noise. They don't require a retro, a root cause analysis, or a management escalation.

### 2. Genuine systemic drops have identifiable causes
Statistically significant drops (p < 0.05 on Mann-Whitney) correlated strongly with:
- Team composition changes (new joiner ramp-up, member leaving)
- Dependency spikes — specifically sprints with 3+ external blockers
- Post-release sprints (technical debt surfacing)

### 3. Holiday/capacity effects are overstated
Partial-capacity sprints (e.g., around holidays) show lower absolute velocity, but **velocity-per-person-day remains stable**. Teams account for it naturally.

---

## Business Value Framing

**The cost of reacting to noise:**
- Each unnecessary retrospective: ~3 hours of team time (facilitation + participation)
- Each unjustified "why is velocity down?" conversation with leadership: ~1–2 hours of PM time
- Each sprint planning session adjusted for a phantom trend: risk of under-committing and underdelivering value

**In a 50-person engineering org running 5 squads over a year:**
- ~60 sprints per squad × 5 squads = 300 sprint cycles
- If 65% of velocity dips are noise: ~195 "false alarm" dips
- If even 20% trigger unnecessary overhead (1 hour each): **195 × 0.2 × 1hr = 39 person-hours wasted annually on noise**

**The value of this tool:** Stop reacting to the 65%. Focus attention on the 35% that are real.

---

## Recommended Use

This analyser is designed to be run at the end of each sprint as a 30-second sanity check:

- **Green:** Velocity change is within normal variance. No action needed.
- **Amber:** Change is notable but not statistically significant. Worth monitoring.
- **Red:** Statistically significant drop (p < 0.05). Warrants a root cause conversation.

---

## What This Would Look Like in Production

1. **Data source:** Jira/Linear sprint reports via API
2. **Trigger:** Automated run on sprint close
3. **Output:** Slack message to PM with significance result + recommended action
4. **Dashboard:** Rolling chart showing velocity ± 1SD band, with flagged significant drops highlighted

---

## Limitations & Next Steps

- Statistical significance thresholds assume roughly normal velocity distribution — may need adjustment for very small teams (n < 5)
- Does not currently separate velocity by story type (bugs vs. features vs. tech debt)
- Next iteration: add capacity-normalised velocity (points per person-day) as primary metric

---

## How to Reproduce

```bash
cd sprint-velocity-analyser
pip install -r requirements.txt
python main.py
```

Outputs: velocity trend chart, significance test results, decomposition plot — all saved to `/outputs`.
