# data-portfolio

Data analytics and machine learning projects — applied to real PM, ops, and startup delivery problems.

Built by **Nikhil Thomas A** — Delivery Program Manager & Fractional Head of Data.

🔗 [Portfolio Site](https://nikhil-thomas-a.github.io/portfolio/) · [LinkedIn](https://www.linkedin.com/in/nikhil-thomas-a-58538117a/) · [PM AI Hub](https://nikhil-thomas-a.github.io/pm-ai-hub)

---

## Why This Exists

Most data portfolios show that someone can write Python. This one shows something different: **what happens when a Delivery PM applies data science to the problems they actually face** — sprint predictability, delivery risk, and SaaS growth health.

Every project here started with a real operational question, not a dataset.

---

## Projects

| Project | Problem Solved | Tools | Business Impact |
|---|---|---|---|
| [Delivery Risk Predictor](./delivery-risk-predictor) | Which sprints will miss their target — *before* they miss it | scikit-learn, random forest, logistic regression | Early risk flags 2+ weeks ahead of deadline; reduces reactive escalations |
| [Sprint Velocity Analyser](./sprint-velocity-analyser) | Why does velocity vary so much sprint-to-sprint? | pandas, scipy, matplotlib, seaborn | Identifies systemic vs. random variance; informs planning buffer decisions |
| [Startup KPI Dashboard](./startup-kpi-dashboard) | Are we growing or just busy? | pandas, matplotlib, SaaS metrics | Single-view health check across MRR, churn, CAC/LTV — built for weekly leadership reviews |

---

## Project Deep-Dives

### Delivery Risk Predictor
**The question:** Can we predict sprint delivery failure early enough to act on it?

**The approach:** Trained a random forest classifier on sprint features — team size, story point load, dependency count, mid-sprint scope changes — to output a risk score per sprint at the halfway point.

**What it found:** Scope changes mid-sprint and high dependency counts are the two strongest predictors of delivery failure, outweighing team size or story point volume.

**Business relevance:** In a 10-sprint programme, catching 3 at-risk sprints two weeks early gives the PM time to re-scope, re-source, or reset stakeholder expectations — instead of explaining a miss after the fact.

📄 [Full business impact writeup →](./delivery-risk-predictor/BUSINESS_IMPACT.md)

---

### Sprint Velocity Analyser
**The question:** Is our velocity trend meaningful, or just noise?

**The approach:** Applied statistical decomposition to separate systemic velocity trends from sprint-to-sprint randomness. Used scipy for significance testing on velocity drops.

**What it found:** Most "velocity dips" teams worry about are statistically insignificant. Genuine systemic drops correlate with team changes and dependency spikes, not effort.

**Business relevance:** Stops leadership from reacting to noise. Changes the conversation from "why was velocity low?" to "is this drop actually significant?"

📄 [Full business impact writeup →](./sprint-velocity-analyser/BUSINESS_IMPACT.md)

---

### Startup KPI Dashboard
**The question:** What's the minimum viable data view a seed-stage startup needs every week?

**The approach:** Built a composable dashboard covering the six metrics that matter most at seed/Series A — MRR growth rate, net revenue retention, churn rate, CAC payback period, LTV:CAC ratio, and burn multiple.

**Business relevance:** Replaces 4 separate spreadsheets with one coherent view. Designed for a weekly 15-minute leadership review, not a 2-hour BI session.

---

## Skills Demonstrated

`Python` · `pandas` · `numpy` · `matplotlib` · `seaborn` · `scipy` · `scikit-learn` · `EDA` · `classification` · `feature importance` · `statistical significance testing` · `SaaS metrics` · `data storytelling` · `synthetic data generation`

---

## How to Run Any Project

Each project is self-contained with its own `README.md` and requirements.

```bash
cd delivery-risk-predictor   # or sprint-velocity-analyser / startup-kpi-dashboard
pip install -r requirements.txt
python main.py
```

All outputs (charts, reports) are saved locally. No external APIs required.

---

## About the Author

I'm a Delivery Program Manager who got tired of making gut-feel decisions when data was available. These projects are the result of applying ML and analytics to problems I've lived through managing engineering teams and delivery programmes.

Connect: [LinkedIn](https://www.linkedin.com/in/nikhil-thomas-a-58538117a/)
