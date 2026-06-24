# Ranking Methodology & Scoring Design

This document details the mathematical model, feature calculations, and weighting metrics used by the ranking engine.

---

## 1. Mathematical Formulation

To balance technical capability against availability constraints, the score is calculated as:

$$\text{Final Score} = Q_{\text{tech}} \times M_{\text{location}} \times M_{\text{notice}} \times M_{\text{salary}} \times M_{\text{engagement}}$$

This additive-multiplicative design ensures that a candidate who is highly qualified technically ($Q_{\text{tech}} \approx 1.0$) but completely unavailable (e.g. lives in Canada with no relocation, notice period 120 days, response rate $5\%$) receives a final score near zero ($0.0$), reflecting real-world recruiter behavior.

---

## 2. Technical Quality Score ($Q_{\text{tech}}$)

The technical quality score is additively composed of five vectors:

$$Q_{\text{tech}} = 0.30 \times S_{\text{exp}} + 0.25 \times S_{\text{title}} + 0.35 \times S_{\text{skills}} + 0.08 \times S_{\text{company}} + 0.02 \times S_{\text{edu}}$$

### A. Experience Years Score ($S_{\text{exp}}$)
Prefers the $5\text{–}9$ years range requested by the JD:
* $5.0 \le \text{Years} \le 9.0$: $1.0$
* $4.0 \le \text{Years} < 5.0$ or $9.0 < \text{Years} \le 12.0$: $0.8$
* $3.0 \le \text{Years} < 4.0$ or $12.0 < \text{Years} \le 15.0$: $0.5$
* Otherwise: $0.15$

### B. Title Alignment Score ($S_{\text{title}}$)
Matches current and past roles against target title hierarchies:
* **Core Title Match** (regex: `ai`, `ml`, `nlp`, `search`, `retrieval`, `recommender`, `ranking` + `engineer`, `developer`, `scientist`):
  * Current Title: $1.0$
  * Past Title: $0.8$
* **Adjacent Engineer Match** (e.g. `backend`, `data`, `software`): $0.6$
* **Disqualified Current Title** (e.g. `manager`, `hr`, `sales`, `marketing`): $0.05$

### C. Skills Alignment Score ($S_{\text{skills}}$)
Computes points based on skills matched against `CORE_AI_SKILLS` and `ADJACENT_SKILLS`:
$$\text{SkillPoints} = \sum_{s \in S_{\text{core}}} 8.0 \times P_s \times T_s \times \text{Years}_s + \sum_{s \in S_{\text{adj}}} 2.0 \times P_s \times T_s \times \text{Years}_s$$
Where:
* $P_s$ is the proficiency multiplier ($\text{beginner}=1, \text{intermediate}=2, \text{advanced}=3, \text{expert}=4$).
* $T_s$ is the trust factor: $1.0 + \min(\text{endorsements}, 50) / 20.0$.
* $\text{Years}_s$ is the duration: $\min(\text{duration\_months}/12, \text{cap})$.
* Normalization: $S_{\text{skills}} = \min(\text{SkillPoints} / 150.0, 1.0)$.

### D. Company Profile Score ($S_{\text{company}}$)
 Startup engineering cultures require product-building discipline. Candidates with service consulting backgrounds are penalized:
* **All Consulting**: If all past employers match `CONSULTING_COMPANIES` (e.g., TCS, Wipro, Infosys): $0.15$
* **Mixed Background**: If some consulting history is present: $0.7$
* **Stability Penalty**: If average job duration (tenure) $< 18$ months: score multiplied by $0.8$ (job hopper modifier).

### E. Education Tier Score ($S_{\text{edu}}$)
Prefers top academic institutions:
* Maximum tier among listed schools: $\text{tier\_1}=1.0$, $\text{tier\_2}=0.8$, $\text{tier\_3}=0.6$, $\text{tier\_4}/\text{unknown}=0.4$.

---

## 3. Availability Multipliers ($M_{\text{avail}}$)

### A. Location Fit ($M_{\text{location}}$)
Checks proximity to Noida/Pune for hybrid cadence:
* Local (Delhi NCR, Noida, Pune): $1.0$
* Willing to relocate from Tier-1 city (Bangalore, Mumbai, Hyderabad, etc.): $0.95$
* Willing to relocate from other cities: $0.8$
* Unwilling to relocate and country = India: $0.2$
* Unwilling to relocate and international: $0.05$

### B. Notice Period Decay ($M_{\text{notice}}$)
Early-stage startups need prompt onboarding:
* Notice $\le 30$ days: $1.0$
* Notice $\le 60$ days: $0.85$
* Notice $\le 90$ days: $0.55$
* Notice $> 90$ days: $0.1$

### C. Expected Salary Modifier ($M_{\text{salary}}$)
Funnels candidates into reasonable budget categories:
* Salary Max $\le 45$ LPA: $1.0$
* Salary Max $\le 60$ LPA: $0.75$
* Salary Max $> 60$ LPA: $0.4$

### D. Platform Engagement ($M_{\text{engagement}}$)
Calculated from login activity recency and message response rates:
$$M_{\text{engagement}} = \text{ActivityDecay} \times \left(0.3 + 0.7 \times \text{ResponseRate}\right)$$
* $\text{ActivityDecay}$ decays relative to the anchor date `2026-06-24`:
  * Active within 30 days: $1.0$
  * Active within 90 days: $0.9$
  * Active within 180 days: $0.6$
  * Active $> 180$ days: $0.2$

---

## 4. Deterministic Tie-Breaking Sort

To ensure stable reproduction outputs and satisfy [validate_submission.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/validate_submission.py) constraints:
1. Candidate scores are rounded to 4 decimal places.
2. The candidates are sorted using:
   $$\text{SortKey} = \left( -\text{Round}(\text{Score}, 4), \text{candidate\_id} \right)$$
3. If two candidates end up with the same formatted score (e.g. `0.8567`), the candidate with the lexicographically smaller ID (e.g. `CAND_0012624` before `CAND_0052335`) is assigned the higher rank.
