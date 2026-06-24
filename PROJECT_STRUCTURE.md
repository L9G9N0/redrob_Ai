# Project Structure Guide

This document maps the folder layout and files of the Candidate Discover & Ranking Engine repository.

---

## 1. Directory Tree Layout

```text
.
├── candidates.jsonl                   # Raw 100,000 candidate dataset (JSON Lines format)
├── candidate_schema.json              # Official JSON schema defining candidate structure
├── rank.py                            # Core ingestion, scoring, and ranking engine
├── run_tests.py                       # Test suite (Unit, Integration, and Benchmarks)
├── validate_submission.py             # Validation script for CSV formatting and rules
├── requirements.txt                   # Ingestion requirements (Python Standard Library only)
├── submission_metadata.yaml           # Metadata mapping for challenge portal submission
├── README.md                          # Main overview, setup, and diagrams
├── ARCHITECTURE.md                    # Core architecture design and components
├── API.md                             # CLI arguments and input/output schema definitions
├── PROJECT_STRUCTURE.md               # Folder tree and files definitions
├── DEVELOPMENT.md                     # Local setup guidelines and development rules
├── DEPLOYMENT.md                      # Docker setups and sandboxed execution details
├── SECURITY.md                        # Threat analysis, input sanitization, and honeypots
├── CHANGELOG.md                       # History of edits and evolutionary timeline
├── ROADMAP.md                         # Future updates and system roadmaps
├── CONTRIBUTING.md                    # Code styles, branches, and submission workflows
├── SUPPORT.md                         # Technical support contacts and issue channels
├── CODE_OF_CONDUCT.md                 # Contributor behavior constraints and values
├── RELEASE.md                         # Roster releases details and submission checklists
└── docs/                              # Auxiliary documentation assets
    ├── ARCHITECTURE.md                # System design and core architectural choices
    ├── DATASET.md                     # Schema structures and honeypot analysis guide
    ├── RANKING_METHODOLOGY.md         # Additive-multiplicative weights and decays
    ├── TESTING.md                     # Development workflows and testing metrics
    ├── DEPLOYMENT.md                  # Performance benchmarks and docker specs
    ├── LIMITATIONS.md                 # Heuristics trade-offs and future updates
    └── CHANGELOG.md                   # Chronological engineering edits log
```

---

## 2. Ingestion Files & Runtimes

* **`rank.py`**: The central execution entry point. Houses the parser, the programmatic honeypot checkers, the additive-multiplicative scoring pipeline, the tie-breaking sorter, and the custom justification dictionary mapping.
* **`run_tests.py`**: The test runner. Contains 12 automated unit, integration, and performance benchmarks to verify honeypot logic, scoring formulas, and execution latency.
* **`validate_submission.py`**: A parsing validator. Ensures that the final submission CSV contains exactly 100 entries, ranks are from 1 to 100, scores are non-increasing, and tie-breaking ranks are sorted ascending by candidate ID.

---

## 3. Configuration & Metadata

* **`submission_metadata.yaml`**: Standard configuration file describing submission metadata:
  ```yaml
  # Submission configuration mapping
  participant_id: "team_redrob"
  methodology_description: "Additive-multiplicative quality scorer with stream parsing and deterministic tie-breaking."
  runtime_seconds: 24
  memory_peak_mb: 156
  ```
