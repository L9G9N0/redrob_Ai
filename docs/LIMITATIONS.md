# Limitations & Future Upgrades

This document outlines the current limitations of our implementation under the challenge constraints and maps out future production-grade enhancements.

---

## 1. System Limitations

### A. Heuristic Weight-Scoring Manual Tuning
* **Limitation**: The scoring system uses hard-coded weights (e.g. $0.35$ weight on skills, $0.25$ weight on job titles) and step functions for years of experience.
* **Impact**: While these weights represent professional recruiter rules, they are not mathematically optimized via gradient descent. Without training labels (ground truth rankings), we cannot run supervised optimization to find the exact global maximum weights.

### B. Rigid Dictionary Skill Matching
* **Limitation**: The list of core AI and adjacent engineering skills is statically defined.
* **Impact**: The engine cannot dynamically learn that a new or unlisted skill (e.g. "Mamba architecture" or "Speculative Decoding") is a core AI skill unless it is explicitly added to the `CORE_AI_SKILLS` set. It is vulnerable to vocabulary drift as technology changes.

### C. Standard Template-Based Reasoning
* **Limitation**: Candidate justifications are constructed dynamically using templates.
* **Impact**: While this guarantees factual accuracy ($0\%$ hallucination) and satisfies the validator's variation checks, the reasoning sentences lack the rich stylistic variety and natural flow of a large LLM output.

---

## 2. Future Improvements (Roadmap)

If the compute, time, and network constraints are relaxed in future stages, the ranking engine will be upgraded in the following order:

### Phase 1: Offline Pre-Computation of Cross-Encoder Scores
* **Approach**: Pre-compute the semantic similarity score of candidate summary and career descriptions against the job description using a local cross-encoder model (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) on a GPU machine offline.
* **Benefit**: The computed semantic similarity floats can be cached inside a lightweight key-value database (e.g., SQLite or RocksDB) and shipped with the Docker container, yielding highly accurate neural matches at runtime in $O(1)$ database search time.

### Phase 2: Supervised Learning-to-Rank (LTR) Integration
* **Approach**: Once user-feedback loop labels (recruiters saving profiles, candidate application actions) become available, train a LightGBM LambdaMART LTR model.
* **Benefit**: Learns the exact non-linear feature interactions between candidate quality and behavioral signals, replacing manual heuristic tuning with data-driven loss optimization (maximizing NDCG directly).

### Phase 3: Fine-Tuning a Local Sentence Embedding Model
* **Approach**: Fine-tune a compact embedding model (such as `bge-small-en-v1.5`) on HR-specific datasets (resume-to-JD pairs) using Contrastive Loss.
* **Benefit**: Captures domain-specific synonym mappings (e.g., recognizing that "ML Infrastructure" maps to both "Kubernetes" and "PyTorch distributed training") without requiring manual keyword dictionaries.
