# Business Impact — Delivery Risk Predictor

## The Problem

Delivery PMs typically find out a sprint is going to miss its target **at the end of the sprint** — during the review, or worse, when a stakeholder asks. By that point, there are no levers left to pull.

The standard response is retrospective: root cause analysis, apologies, revised timelines. What's missing is **early warning** — a signal at sprint midpoint that says "this one is tracking to miss."

---

## The Approach

Trained a binary classification model on synthetic sprint data modelled on realistic programme delivery patterns.

**Features used:**
- Story points committed vs. team capacity ratio
- Number of external dependencies
- Mid-sprint scope change flag (boolean)
- Team size
- Number of carry-over stories from previous sprint
- Blocker count at sprint day 5

**Models evaluated:**
- Logistic Regression (baseline)
- Random Forest (selected model)
- Gradient Boosted Trees (compared)

**Target variable:** Sprint missed its committed scope by >20% (binary: yes/no)

---

## Results

| Metric | Logistic Regression | Random Forest |
|---|---|---|
| Accuracy | 74% | 83% |
| Precision (at-risk) | 0.71 | 0.81 |
| Recall (at-risk) | 0.68 | 0.79 |
| F1 Score | 0.69 | 0.80 |

Random Forest selected as final model based on F1 score and interpretability via feature importance.

---

## Feature Importance (Top Findings)

1. **Mid-sprint scope change** — single strongest predictor of delivery failure (feature importance: 0.31)
2. **External dependency count** — second strongest signal (0.24)
3. **Carry-over story count** — strong leading indicator of accumulating debt (0.19)
4. **Blocker count at day 5** — actionable early signal (0.14)
5. **Capacity ratio** — surprisingly weak predictor in isolation (0.07)

**Insight:** Teams failing to deliver are rarely under-resourced at the start. They're disrupted mid-sprint. Scope changes and unresolved dependencies are the real culprits — not team size or story point volume.

---

## Business Value Framing

**In a 10-sprint quarterly programme:**

- Average sprint miss rate in typical delivery programmes: ~30% (3 in 10)
- With risk flagging at sprint midpoint, a PM has 5–7 days to act
- Possible interventions: descope non-critical stories, escalate blockers, reset stakeholder expectations, bring in extra resource

**Conservative ROI estimate:**
- Each avoided miss saves ~1 sprint cycle of rework + re-planning (~3–5 person-days)
- Catching 2 of 3 at-risk sprints per quarter = 6–10 person-days recovered
- At a blended day rate of £500: **£3,000–£5,000 per quarter in delivery efficiency**

---

## What This Would Look Like in Production

1. **Data source:** Jira/Linear API — pull sprint metrics at day 5 of each sprint
2. **Model serving:** Lightweight Python script or Airflow DAG running at sprint midpoint
3. **Output:** Slack notification to PM + delivery lead with risk score and top contributing factors
4. **Feedback loop:** PM logs actual sprint outcome; model retrains quarterly on real data

---

## Limitations & Next Steps

- Model currently trained on synthetic data — needs validation on real sprint data before production use
- Does not account for team-specific patterns (some teams consistently miss; the model can't distinguish systemic vs. one-off)
- Next iteration: add rolling team velocity baseline as a feature; incorporate Jira data directly

---

## How to Reproduce

```bash
cd delivery-risk-predictor
pip install -r requirements.txt
python main.py
```

Outputs: confusion matrix, feature importance chart, ROC curve — all saved to `/outputs`.
