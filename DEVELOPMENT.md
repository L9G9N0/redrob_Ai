# Development Setup & Workflow Guidelines

This document details the local setup, code styles, testing workflows, and submission verification processes for development.

---

## 1. Local Environment Configuration

This project relies exclusively on the **Python Standard Library**. No package installations are required.

### System Verification
* Ensure Python 3.8+ is installed:
  ```bash
  python3 --version
  ```
* Verify the candidate database file is extracted:
  ```bash
  wc -l candidates.jsonl
  # Output must show exactly 100001 lines (100,000 candidate rows + 1 trailing newline)
  ```

---

## 2. Ingestion & Ranking Execution

To run the pipeline and output candidate rankings locally:
```bash
python3 rank.py --candidates candidates.jsonl --out team_redrob.csv
```

### Format Verification
Verify the generated file conforms to submission constraints:
```bash
python3 validate_submission.py team_redrob.csv
```

---

## 3. Running Test Suites

Execute all unit, integration, and performance benchmarking tests:
```bash
python3 run_tests.py
```

### Test Coverage Breakdown
1. **`TestHoneypots`**: Asserts that `check_honeypots` accurately flags impossible synthetic patterns.
2. **`TestScoring`**: Verifies experience tiers, locations, expected salaries, and title score metrics.
3. **`TestReasoningFlaws`**: Validates resolution of screening comment issues (Senior title corrections, toxic positivity, template bucket removals, and prefix variations).
4. **`TestIntegration`**: Runs end-to-end evaluations on a mock dataset of 105 candidates.
5. **`TestPerformance`**: Scores 5,000 profiles on CPU and projects execution latency for 100,000 candidates to ensure it is under 120 seconds.

---

## 4. Code Standards & Patterns

* **Python Standard Library Focus**: Under no circumstances import external modules (e.g. `pandas`, `numpy`, `scikit-learn`). Doing so will violate stage constraints.
* **Keep Logic Deterministic**: Ensure all float values are rounded to 4 decimal places before sorting.
* **Maintain Lexicographical ID Resolution**: When sorting scores, always resolve ties using `candidate_id` in ascending lexicographical order.
