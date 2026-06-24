# Redrob AI Hiring Challenge — Intelligent Candidate Discovery & Ranking Engine

Welcome to the Intelligent Candidate Discovery & Ranking Engine for the Redrob AI Hiring Challenge. This repository implements a production-grade, highly optimized candidate matching pipeline that scores, filters, and ranks a pool of 100,000 candidates for a **Senior AI Engineer — Founding Team** role.

The engine processes the entire 100,000-candidate pool in **under 25 seconds** on a single CPU core, enforces strict location/relocation, notice period, and salary boundaries, filters out keyword-stuffing profiles and honeypots, and produces a valid formatted CSV of the top 100 candidates with factual justifications.

---

## 🚀 Quick Start & Reproducibility

To reproduce our submission CSV from the candidates dataset, follow these instructions.

### 1. Prerequisites
Ensure you have Python 3.8+ installed (tested on `Python 3.11.4`). No external Python dependencies are required (runs entirely using the standard library to guarantee reproducibility and zero environment compilation overhead).

### 2. Setup
Clone the repository and verify the candidate pool dataset (`candidates.jsonl`) is present:
```bash
# Verify candidates pool is extracted (wc -l candidates.jsonl should return 100,001)
wc -l candidates.jsonl
```

### 3. Generate Submission CSV
Run the ranker command at the root of the repository:
```bash
python3 rank.py --candidates ./candidates.jsonl --out ./team_redrob.csv
```

### 4. Validate Results
Verify the formatting, sorting order, and tie-breaking requirements of the generated CSV:
```bash
python3 validate_submission.py team_redrob.csv
```

---

## 📂 Repository Layout

```text
├── candidates.jsonl                     # 100,000 candidate dataset (JSONL)
├── candidate_schema.json                # JSON Schema for candidate validation
├── rank.py                              # Core ingestion, scoring, and ranking engine
├── run_tests.py                         # Test suite (Unit, Integration, Performance)
├── validate_submission.py               # Official challenge validator script
├── submission_metadata.yaml             # Metadata config for portal submission
├── README.md                            # Main project overview and setup
└── docs/                                # Production Documentation
    ├── ARCHITECTURE.md                  # System Design & Core Engineering Decisions
    ├── DATASET.md                       # Data Schema & Honeypot Analysis Guide
    ├── RANKING_METHODOLOGY.md           # Multi-Factor Weight Scorer & Multipliers
    ├── TESTING.md                       # Test Execution & Developer Guide
    ├── DEPLOYMENT.md                    # Deployment Guide & Sandbox Specifications
    ├── LIMITATIONS.md                   # Platform Constraints & Future Enhancements
    └── CHANGELOG.md                     # History of Iterative Development
```

---

## 📚 Detailed Documentation Index

To explore the architecture, decisions, and logic behind our implementation, please refer to the following guides in the `docs/` directory:

1. **[Architecture & Design Decisions](docs/ARCHITECTURE.md)**: Conceptual pipeline, components interaction, offline operations, and systems constraints.
2. **[Dataset & Honeypot Guide](docs/DATASET.md)**: In-depth schema fields analysis and details on programmatic honeypot detection rules.
3. **[Ranking Methodology](docs/RANKING_METHODOLOGY.md)**: Formulas for Technical Quality, Availability, Notice Period decays, and tie-breaking algorithms.
4. **[Testing & Developer Guide](docs/TESTING.md)**: Execution instructions for the test suites, verification criteria, and developer workflows.
5. **[Deployment & Sandbox Guide](docs/DEPLOYMENT.md)**: Specifications for Docker containers, HuggingFace Spaces sandbox runtime, and CPU optimization.
6. **[Limitations & Future Upgrades](docs/LIMITATIONS.md)**: Analysis of trade-offs made under limits, model scale constraints, and production roadmap.
7. **[Changelog](docs/CHANGELOG.md)**: Development milestone trace.
