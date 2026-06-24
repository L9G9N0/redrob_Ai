# Changelog

This document tracks the iterative design, milestones, and updates to the Intelligent Candidate Discovery & Ranking Engine.

---

## [1.0.0] - 2026-06-24

### Added
* **Multi-Factor Scoring Script (`rank.py`)**: Core scoring algorithm combining additive technical scores (years of experience, title alignment, skills fit, company profile, and education tier) with multiplicative availability modifiers.
* **Programmatic Honeypot Filters**: Handled exactly three classes of impossible candidate profiles (expert skills with 0 months, startup tenure anomalies at Krutrim and Sarvam AI, and job tenures exceeding lifetime experience).
* **Test Suite (`run_tests.py`)**: Unit tests for scoring and honeypots, end-to-end integration tests using mock candidate data, and CPU scoring latency benchmarks.
* **Strict Formatting & Lexicographical Sorting**: Rounded scores to 4 decimal places before sorting to satisfy lexicographical candidate ID constraints on equal scores.
* **Comprehensive Documentation Guides**: Added Guides for Architecture, Dataset, Ranking Methodology, Testing, Deployment, and Limitations.

### Fixed
* **Floating-Point Tie-Break Validation Bug**: Resolved a validation error where float precision sorting in Python introduced ties in the CSV 4-decimal formatted output that violated the candidate ID ascending validation rule.

### Changed
* **Copied Metadata Template**: Filled out and verified `submission_metadata.yaml` with appropriate reproduction commands and platform details.
