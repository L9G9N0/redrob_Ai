# Release & Submission Checklist

This document details the checklist and validation procedures before building a release candidate or making a portal submission.

---

## 1. Submission Verification Steps

Before exporting `team_redrob.csv` for submission:

1. **Verify Raw Database**:
   Confirm that the `candidates.jsonl` database file is unmodified and has the exact expected line count:
   ```bash
   wc -l candidates.jsonl
   ```
2. **Execute Ranking Pipeline**:
   Run the candidate ranker to generate the submission output file:
   ```bash
   python3 rank.py --candidates candidates.jsonl --out team_redrob.csv
   ```
3. **Run Formatting Compliance Validator**:
   Execute the submission checker to verify format alignment:
   ```bash
   python3 validate_submission.py team_redrob.csv
   ```
   * **Verification**: Command must exit with output `Submission is valid.`

---

## 2. Roster Integrity Verification Checklist

Ensure the final ranked CSV meets all constraints:
* [x] **Row Count**: CSV contains exactly 1 header row + 100 candidate data rows.
* [x] **Ranks Range**: Ranks span sequentially from 1 to 100 with no duplicates.
* [x] **Score Sorting**: Candidate score column is non-increasing.
* [x] **Tie-Breaker Resolution**: Any candidates with identical scores are sorted in ascending lexicographical order by `candidate_id`.
* [x] **No Honeypots**: Checked that no candidate IDs matching the 193 honeypot profiles are present in the top 100 rows.
* [x] **Justification Integrity**: Every reasoning note is strictly under 245 characters and contains no AI templates or repeated openers.
