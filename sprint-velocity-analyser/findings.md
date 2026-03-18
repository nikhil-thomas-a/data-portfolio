# Findings — Sprint Velocity Analyser

Plain-English interpretation of the analysis. Written as if presenting to a Head of Engineering or VP of Product — what the data shows, what it means in practice, and what to do about it.

---

## The short version

Three teams. 18 months. 108 sprints.

- **Team Alpha** is your benchmark — stable, experienced, predictable. But tech debt is quietly eroding their capacity.
- **Team Beta** is improving but inconsistent. Scope creep is their biggest problem — it affects more than half their sprints.
- **Team Gamma** is the most interesting story. They started rough but show the strongest upward trend of any team. If that trajectory holds, they'll match Beta within 6 months.

The single most damaging event across all three teams? A key person going absent. It costs more points per sprint than any other blocker — and it's the hardest to plan for.

---

## Chart by chart

### 1. Velocity trends — is each team getting faster, slower, or staying flat?

**What the chart shows:** Sprint velocity (completed story points) plotted over 36 sprints per team, with a 4-sprint rolling average to smooth noise and a regression trend line to show direction.

**Team Alpha (red):** Flat trend, slope of -0.12 points per sprint — effectively zero movement. Average velocity of 50 points, standard deviation of 8.4. This is what a mature, stable team looks like. The variation you see is normal sprint-to-sprint noise, not a structural problem. The rolling average barely moves.

**Team Beta (blue):** Slight positive trend but high variance (σ=10.8 vs Alpha's 8.4). The rolling average oscillates more than Alpha's — this team has good sprints and bad sprints in clusters, which usually points to external dependencies or unplanned work landing in batches.

**Team Gamma (green):** Clear positive trend — slope of +0.80 points per sprint, which is statistically significant (r=0.61, p<0.001). Started at roughly 15–20 points in early sprints, now regularly hitting 35–40. The learning curve is visible in the data. Standard deviation of 14.0 reflects a team still finding consistency, but the direction is right.

**What to do with this:** Alpha needs protecting from further tech debt accumulation or it will start declining. Beta needs to stabilise — investigate what's causing the cluster variance. Gamma needs time and should not be overloaded with dependencies or scope changes right now — they're on a good trajectory and disruption will knock them back.

---

### 2. Team comparison — velocity, predictability, and carryover distributions

**What the chart shows:** Violin plots for each team across three metrics. The width of the violin at any point shows how often that value occurred — fat in the middle means most values cluster there, thin at the extremes means outliers.

**Velocity:** Alpha's violin is tall and narrow — consistent high output. Gamma's is wide and spread low — high variance, lower output. Beta sits between them. No surprises here, but the shape matters: Gamma's width tells you they occasionally hit good sprints (30–35 pts) and occasionally collapse (10–15 pts). That's a planning problem — you can't rely on their capacity being consistent.

**Predictability (completed ÷ committed):** Alpha at 0.93 means they complete 93% of what they commit to on average. Gamma at 0.80 means one in five points they commit to doesn't get done. In a sprint of 25 points, that's 5 points of carryover every single sprint. Multiply that over a quarter and you have a significant planning gap.

**Carryover:** Gamma accumulates 7 points of carryover per sprint on average, totalling 252 points over 18 months — roughly 5 full sprints worth of work that got committed to but never completed. That's a backlog management problem as much as a delivery problem.

**What to do with this:** Set Gamma's committed points 15–20% below their historical average until predictability improves. Under-committing and over-delivering builds confidence and reduces carryover. For Alpha, watch the lower tail of their velocity distribution — any sustained drop there is an early warning sign.

---

### 3. Blocker impact — which blocker types cost the most story points?

**What the chart shows:** Two views. Left: average story points lost per sprint when each blocker type occurs. Right: how frequently each blocker appears per team.

**Key person absent** causes the highest average points lost — over 12 points per occurrence. That's nearly a quarter of Alpha's average sprint velocity wiped out by one person being unavailable. This is the most damaging single event type precisely because it's unpredictable and teams rarely have true redundancy on critical skills.

**Scope change** is second most damaging at ~10 points lost. The mechanism is double — scope is added (increasing the denominator) while the team's capacity doesn't change, and the context switching from planning the new work costs time on top.

**Tech debt** is the most *frequent* blocker across all three teams — it shows up more often than anything else. Its per-incident impact is lower (~6 points) but its frequency makes it the highest cumulative drag on velocity over time.

**Dependency delay** and **infrastructure issues** are moderately damaging and tend to be the most fixable — they're external blockers that process improvements (better dependency tracking, infrastructure-as-code) can systematically reduce.

**What to do with this:** For key person risk — map critical knowledge holders and start cross-training now, before someone leaves or goes on leave. For tech debt — it needs a dedicated allocation each sprint (commonly 10–15% of capacity) or it compounds. For scope change — any mid-sprint scope addition should be flagged in the RAID log and require a formal trade-off decision, not a quiet addition to the board.

---

### 4. Team size vs velocity — does adding people actually increase output?

**What the chart shows:** Scatter plot of team size (x-axis) against velocity (y-axis) for each team, with a regression line showing the correlation direction.

**The finding is counterintuitive but important:** All three teams show a *negative* correlation between team size and velocity. Alpha: r=-0.08, Beta: r=-0.21, Gamma: r=-0.22. None are strongly negative, but none are positive.

This doesn't mean bigger teams are worse. It reflects two things: first, sprint-to-sprint team size variation is usually caused by *absence* rather than intentional sizing — someone is out, the team shrinks, and that's usually also a bad sprint for other reasons. Second, the teams in this dataset are all in the 4–8 person range where coordination costs aren't the dominant factor yet — at 15+ people you'd see different dynamics.

**What to do with this:** Don't interpret this as "hire fewer people." Interpret it as "team composition stability matters more than headcount." A team of 6 consistent people will outperform a team of 8 with frequent churn or absenteeism. Focus on reducing unplanned absences and maintaining stable team membership during critical delivery periods.

---

### 5. Carryover & scope creep — when do teams overcommit?

**What the chart shows:** Two charts. Top: carryover points per sprint over time for each team. Bottom: how many sprints had scope added mid-sprint, and the average points added when it happened.

**Carryover over time:** Gamma's carryover is volatile — spikes of 15–20 points in early sprints, gradually stabilising. Beta has consistent mid-level carryover that doesn't improve much over time, which suggests the root cause isn't team maturity but planning habits. Alpha's carryover is low and flat — a sign of disciplined sprint planning and honest estimation.

**Scope creep:** Beta is the most affected — scope was added in 53% of their sprints. That means more than half their sprints had mid-sprint additions that weren't in the original commitment. Even when the average addition is only 5–6 points, the disruption of replanning mid-sprint costs more than the points suggest. Gamma at 42% and Alpha at 28% show the same pattern at different severity levels.

**What to do with this:** Scope added mid-sprint should be an exception, not a norm. The fix is upstream — better sprint planning, a clearer definition of ready for backlog items, and a team agreement that new requests go into the *next* sprint's backlog unless something is genuinely on fire. Track scope creep rate as a team health metric alongside velocity.

---

### 6. Predictability heatmap — consistency by team, quarter by quarter

**What the chart shows:** Each cell is the average predictability score (completed ÷ committed) for one team in one quarter. Green = closer to 1.0 (delivered what was committed). Yellow/red = more was committed than delivered.

**Alpha** is consistently dark green — 0.90–0.96 across all six quarters. One dip to 0.84 in the final quarter worth watching. **Beta** fluctuates more — some strong quarters (0.92) and some weak ones (0.82), which maps to the variance we saw in the velocity distribution. **Gamma** starts weakest (0.72–0.75 in early quarters) and improves to 0.84–0.88 by the end — the learning curve again, visible in quarterly snapshots.

**What to do with this:** Use this view in quarterly planning conversations. A team with consistently high predictability can be given stretch goals — they've earned the trust. A team with declining predictability needs a capacity conversation before more scope is added. Predictability is the metric that connects team performance to business planning reliability.

---

## Summary table

| Metric | Alpha | Beta | Gamma |
|--------|-------|------|-------|
| Avg velocity | 50 pts | 37 pts | 27 pts |
| Velocity std dev | 8.4 | 10.8 | 14.0 |
| Predictability | 93% | 88% | 80% |
| Avg carryover / sprint | 4.4 pts | 6.5 pts | 7.0 pts |
| Total carryover (18 months) | 159 pts | 233 pts | 252 pts |
| Sprints with scope creep | 28% | 53% | 42% |
| Avg bugs reported / sprint | 3.0 | 4.1 | 4.2 |
| Velocity trend | Flat | Slight positive | **Strong positive** |
| Top blocker | Tech debt | Tech debt | Tech debt |

---

## Three things to act on first

**1. Protect Gamma's trajectory.** They're improving faster than any other team. Disrupting them with dependencies, re-orgs, or scope changes now is the highest-risk move. Give them stable conditions for two more quarters.

**2. Address tech debt on Alpha before it becomes a velocity problem.** It's the most frequent blocker and Alpha is your most reliable team. A dedicated tech debt sprint every quarter is cheaper than the compounding drag.

**3. Fix Beta's scope creep habit.** 53% of sprints had mid-sprint additions. That's a planning culture problem, not a capacity problem. The fix is a team agreement and a sprint goal that the team actually defends.

---

*Analysis by Nikhil Thomas A — [Portfolio](https://nikhil-thomas-a.github.io/portfolio/) · [LinkedIn](https://www.linkedin.com/in/nikhil-thomas-a-58538117a/)*
