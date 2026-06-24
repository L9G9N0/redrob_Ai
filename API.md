# CLI & Data API Specifications

This document details the command-line interface arguments, input schemas, and output validation formats for the candidate ranker.

---

## 1. Command-Line Interface Reference

The engine is executed as a standalone Python CLI.

```bash
python3 rank.py --candidates <path_to_jsonl> [--out <path_to_csv>] [--is-mock]
```

### Options Reference
| Flag | Short | Type | Default | Description |
| :--- | :---: | :---: | :---: | :--- |
| `--candidates` | `-c` | `string` | N/A | **Required**. Filepath to the raw `candidates.jsonl` dataset. |
| `--out` | `-o` | `string` | `team_redrob.csv` | Output file destination path for the top-100 ranked candidates. |
| `--is-mock` | `-m` | `flag` | `False` | Run logic using test templates instead of audited maps (used in unit tests). |

---

## 2. Ingestion Format (candidates.jsonl)

The input file must contain one JSON object per line. The structure must match the [candidate_schema.json](file:///Users/legend27648/agy-cli-projects/redrob_Ai/candidate_schema.json) specification.

### Data Model Structure
```json
{
  "candidate_id": "CAND_0046132",
  "profile": {
    "anonymized_name": "Applicant A",
    "current_title": "AI Research Engineer",
    "years_of_experience": 4.3,
    "location": "Noida, India",
    "country": "India"
  },
  "skills": [
    {
      "name": "Information Retrieval",
      "proficiency": "expert",
      "duration_months": 24,
      "endorsements": 15
    }
  ],
  "career_history": [
    {
      "company": "Verloopio",
      "title": "ML Engineer",
      "duration_months": 25.5,
      "is_current": true
    }
  ],
  "redrob_signals": {
    "notice_period_days": 30,
    "expected_salary_range_inr_lpa": {
      "min": 25.0,
      "max": 35.0
    },
    "last_active_date": "2026-06-20",
    "recruiter_response_rate": 0.94,
    "willing_to_relocate": false
  }
}
```

---

## 3. Serialization Schema (team_redrob.csv)

The output CSV file contains exactly **100 data rows** plus a single header row.

### CSV Fields Breakdown
| Column Name | Type | Constraints | Description |
| :--- | :---: | :---: | :--- |
| `candidate_id` | `string` | Format `CAND_XXXXXXX` (7 digits) | Unique ID of the candidate. |
| `rank` | `int` | `1` to `100` | Roster position, sorted ascending (Rank 1 is best). |
| `score` | `float` | Non-increasing order | Final calculated candidate score, rounded to 4 decimals. |
| `reasoning` | `string` | Under 245 characters | Factual and unique candidate screening notes. |
