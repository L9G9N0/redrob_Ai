# Contributing Guidelines

Thank you for contributing to the Candidate Discovery & Ranking Engine. Please review these development guidelines before proposing changes.

---

## 1. Zero-Dependency Constraint (Critical)

To comply with स्टेज constraints and prevent sandbox execution errors:
* **Python Standard Library Only**: Do not import external packages (e.g. `pandas`, `numpy`, `scikit-learn`, `requests`) inside `rank.py` or `run_tests.py`.
* All JSON parsing, math scoring, regex matching, and CSV serialization must be handled using native Python standard libraries.

---

## 2. Coding Styles & Standards

* **PEP 8 Compliance**: Follow standard Python conventions.
* **Deterministic Tie-Breaking**: Any scoring logic adjustments must maintain float precision rounding (`round(score, 4)`) and sort ties lexicographically ascending by candidate ID.
* **Preserve Comments**: Do not modify existing comments in areas you are not refactoring.

---

## 3. Workflow for Proposing Code Updates

1. **Branch Naming**: Use descriptive prefixes:
   * `feat/` for scoring weights updates or honeypot indicators.
   * `fix/` for parsing anomalies or float precision tie-breaks.
   * `docs/` for architecture updates.
2. **Execute Validation Checks**:
   * Run the test suite:
     ```bash
     python3 run_tests.py
     ```
   * Validate the generated submission file:
     ```bash
     python3 validate_submission.py team_redrob.csv
     ```
3. **Open Pull Request**: Clearly document your changes, performance impacts, and test outputs in the description.
