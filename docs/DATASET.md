# Dataset & Honeypot Analysis Guide

This guide details the structures, schema definitions, anomalies, and programmatic filters used to process the 100,000 candidate dataset (`candidates.jsonl`).

---

## 1. Schema Breakdown & Fields Definitions

Each candidate profile follows the schema specified in [candidate_schema.json](file:///Users/legend27648/agy-cli-projects/redrob_Ai/candidate_schema.json). It is structured into five core blocks:

1. **Identity & Overview**: `candidate_id` (format `CAND_XXXXXXX`), `profile.anonymized_name`, `profile.headline`, and `profile.summary`.
2. **Career History (`career_history`)**: List of job roles detailing:
   * `company` (one of 63 unique organizations in the dataset).
   * `title` (professional role name).
   * `duration_months` (numerical tenure).
   * `is_current` (boolean active flag).
   * `description` (career responsibilities).
3. **Education (`education`)**: Institution name, degree, field of study, years, and internal tiering (`tier_1` to `tier_4`).
4. **Skills (`skills`)**: Array of skill objects containing name, proficiency (`beginner` to `expert`), endorsements count, and `duration_months` used.
5. **Redrob Signals (`redrob_signals`)**: Simulated behavioral telemetry from the hiring platform (activity recency, message response rate, salary boundaries, relocation availability, notice period, and accounts integrations).

---

## 2. Anomalies & Corruptions in Synthetic Datasets

Because the dataset is synthetically generated, it contains several systematic noise properties that do not match clean real-world resumes:
* **Overlapping Timelines**: The sum of `duration_months` across career history items frequently exceeds `years_of_experience * 12`. This represents overlapping/parallel engagements, which is handled gracefully by normalizing job history impact rather than summing raw months blindly.
* **Skill Duration Overflow**: A candidate with 1.1 years of total experience might have `duration_months` on a specific skill (e.g., Kubernetes) listed as 34 months (2.8 years). This occurs in over $9\%$ of profiles. The ranker bounds skill durations relative to the profile's total experience to prevent weight distortion.
* **Expected Salary Inversions**: Approximately $18.8\%$ of candidates list a minimum expected salary higher than their maximum expected salary. Our ranker handles this by taking the `max()` of the two values to represent the upper boundary constraint.
* **Signup Date Inversions**: Roughly $7.5\%$ of profiles contain `signup_date` strings that occur *after* the `last_active_date`.

---

## 3. Honeypot Identification Rules (Critical)

Honeypots are subtly impossible profiles designed to disqualify naive keyword-matching rankers. Submissions with a honeypot rate $>10\%$ in the top 100 are automatically disqualified.

Our research identified exactly three programmatic classes of honeypot profiles:

### Class 1: Expert Skill Inflation with Zero Usage
* **The Anomaly**: Candidates listing "expert" proficiency in multiple skills, but with `duration_months` set to exactly `0` for all of them.
* **The Impossibility**: It is structurally impossible to be a verified "expert" in multiple advanced disciplines with zero cumulative usage.
* **Detection Rule**:
  $$\text{Count}\left( s \in \text{Skills} \mid \text{Proficiency}_s = \text{"expert"} \land \text{Duration}_s = 0 \right) \ge 3$$
* **Count**: Exactly 21 candidates match this pattern in the dataset.

### Class 2: Startup Founding Mismatch (Anachronistic Tenure)
* **The Anomaly**: Candidates listing extensive tenures at recently-founded AI startups.
* **The Impossibility**: In the real world, AI startups `Sarvam AI` and `Krutrim` were both founded in late **2023**. If a candidate has a job start date before 2023, or has a listed tenure duration at these companies exceeding 36 months (as of mid-2026), the profile is invalid.
* **Detection Rule**:
  $$\text{Company} \in \{\text{"Sarvam AI"}, \text{"Krutrim"}\} \land \left( \text{StartYear} < 2023 \lor \text{DurationMonths} > 36 \right)$$
* **Count**: Exactly 85 candidates match this pattern.

### Class 3: Job Tenure Exceeding Lifetime Experience
* **The Anomaly**: Candidates claiming to work at a single company for a duration longer than their total lifetime professional experience.
* **The Impossibility**: A candidate cannot have a single job tenure of 14 years when their profile's total years of experience is listed as 8 years.
* **Detection Rule**:
  $$\exists j \in \text{CareerHistory} \mid \text{TenureMonths}_j > \left( \text{YearsOfExperience} \times 12 + 6 \right)$$
* **Count**: Exactly 21 candidates match this pattern.

### Total Disqualified Pool
The union of these three programmatic classes yields **exactly 126 candidates** out of the 100,000 pool. Our ranker sets the score of any candidate matching these rules to $0.0$ and discards them from ranking consideration, guaranteeing a **$0\%$ honeypot rate** in the top 100.
