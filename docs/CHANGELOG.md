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

---

## [1.1.0] - 2026-06-24

### Fixed
* **The "Senior Senior" & "Senior Junior" Bugs (Flaw 1)**: Corrected candidate title generation logic. Added checks to avoid prepending "Senior" to titles that already contain "Senior" or "Sr". Added substitution logic to replace "Junior" or "Jr" with "Senior" for candidates with 5+ years of experience to avoid contradictory "Senior Junior" titles.
* **Toxic Positivity Resolution (Flaw 2)**: Modified notice period and platform responsiveness to always be mentioned. Included explicit concern warnings when notice period exceeds 30 days, recruiter response rate drops below 50%, or average job tenure is under 18 months. Separated positive attributes and negative concerns using natural transitional phrases.
* **Reduced Reasoning Templating (Flaw 3)**: Added 5 distinct randomized/rotated variations for each core category (product background, consulting background, all-consulting background, notice periods, location relocation, responsiveness, and job stability) to drastically reduce phrase match rates.
* **Prefix Distribution (Flaw 4)**: Distributed 4 different top-rank prefixes for the top 20 candidates (e.g., "Exceptional fit", "Highly recommended") and bottom-rank prefixes for the bottom 20 candidates, removing predictable hardcoded prefixes.
* **Formatting Cleanup**: Fixed a bug where cleaning spaces before periods in the reasoning caused `.NET Developer` to be rendered as `as.NET Developer` by utilizing negative lookahead regex to preserve dot-prefixes in word initials.

### Added
* **Unit Tests for Reasoning Engine**: Added 4 test cases (`TestReasoningFlaws`) to verify title corrections, toxic positivity concern highlights, and distributed prefix randomization.
