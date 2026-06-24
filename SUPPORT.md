# Support Directory

For queries regarding the Candidate Discovery & Ranking Engine, please follow these channels.

---

## 1. Technical Inquiries & Troubleshooting

* **Local Verification Errors**: If `validate_submission.py` reports formatting issues, ensure your python terminal is running under UTF-8 encoding and the CSV contains exactly 100 entries.
* **Honeypot Exclusions**: If a legitimate candidate is being flagged as a honeypot, check the rules implementation inside `check_honeypots()` in [rank.py](file:///Users/legend27648/agy-cli-projects/redrob_Ai/rank.py) and open an issue.

---

## 2. Issue Tracking Channels

* **Bug Reports**: Open an issue on GitHub describing:
  * Python runtime version.
  * Number of candidate profiles parsed.
  * Exact error traceback.
* **Performance Anomalies**: Report runs exceeding the 30-second benchmark execution duration.
