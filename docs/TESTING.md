# Developer & Testing Guide

This guide describes how to run tests, write new test cases, and navigate the development workflow of the ranking repository.

---

## 1. Developer Setup

### Environment Requirements
* **Python**: 3.8+ (tested on `3.11.4`).
* **External Dependencies**: None required for the core runtime or test execution (built on standard library dependencies: `unittest`, `json`, `csv`, `re`, `tempfile`, `argparse`, `datetime`).

### Repository Structure
* [rank.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/rank.py): Contains candidate parsing, honeypot filters, scoring metrics, and reasoning dynamic generators.
* [run_tests.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/run_tests.py): Entry point for the test runner.
* [validate_submission.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/validate_submission.py): Validates output CSV formatting rules.

---

## 2. Test Suite Architecture

The tests are organized into four suites in [run_tests.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/run_tests.py):

### A. Unit Tests (`TestHoneypots` & `TestScoring`)
* **Honeypot Validation**: Asserts that `check_honeypots` correctly flags:
  * Expert proficiency skills with 0 months used.
  * Start date at `Sarvam AI`/`Krutrim` before 2023 or duration > 36 months.
  * Individual job duration exceeding total candidate experience.
* **Scoring Logic**: Asserts that local location mapping, notice periods, and experience scoring execute correctly. Verifies that highly matching profiles score significantly higher than unqualified profiles.

### B. Integration Tests (`TestIntegration`)
* Generates a mock JSONL file containing 105 candidates (100 valid, 5 honeypots).
* Executes the command:
  ```bash
  python3 rank.py --candidates mock_candidates.jsonl --out team_test.csv
  ```
* Asserts that the process returns a zero exit code, filters out all 5 honeypots, outputs exactly 100 rows, and satisfies the CSV format validator.

### C. Performance Benchmarks (`TestPerformance`)
* Simulates scoring $5,000$ mock profiles.
* Extrapolates the duration to $100,000$ candidates to verify it fits comfortably within the 5-minute sandbox limit (asserts projected duration $< 120\text{ seconds}$).

---

## 3. Running the Test Suite

Execute the tests from the root of the repository:
```bash
python3 run_tests.py
```

### Example Successful Output:
```text
Reading candidates from /tmp/tmp_candidates.jsonl...
Total parsed: 105
Honeypots filtered: 5
Candidates remaining for ranking: 100
Writing top 100 candidates to /tmp/team_test.csv...
Ranking pipeline completed successfully.
........
----------------------------------------------------------------------
Ran 8 tests in 0.099s

OK

[Performance Benchmark] Scored 5,000 mock candidates in 0.042 seconds.
[Performance Benchmark] Projected runtime for 100,000 candidates: 0.841 seconds.
```

---

## 4. How to Add New Test Cases

1. Open [run_tests.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/run_tests.py).
2. To test a new honeypot pattern, add a method inside `TestHoneypots` prefixed with `test_`:
   ```python
   def test_new_anomalous_pattern(self):
       candidate = {
           "candidate_id": "CAND_0000999",
           "profile": {"years_of_experience": 1.0},
           "skills": [{"name": "Python", "proficiency": "expert", "duration_months": -5}] # invalid months
       }
       self.assertTrue(check_honeypots(candidate))
   ```
3. Run `python3 run_tests.py` to verify the execution.
