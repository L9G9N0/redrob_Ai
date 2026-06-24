# Candidate Ranking System Roadmap

This document outlines future engineering enhancements, model scale transitions, and feature roadmap phases for the ranking system.

---

## Phase 1: Semantic Embeddings & Offline Pre-Computation

### Objectives
* Transition from keyword dictionaries to semantic similarity checks of candidate summaries against the target job descriptions.
* Maintain execution latency under the 5-minute constraint.

### Implementation
1. **Model**: Fine-tune a compact embedding model (such as `bge-small-en-v1.5`) on HR-specific datasets (resume-to-JD pairs) using Contrastive Loss.
2. **Offline Extraction**: Pre-compute candidate summary embedding cosine similarities against the JD on a GPU environment offline.
3. **KV Cache Storage**: Store these similarity float values inside a lightweight key-value database (e.g. SQLite or RocksDB) packaged directly inside the Docker container.
4. **Runtime Ingestion**: Read the similarities in $O(1)$ database search time during ingestion.

---

## Phase 2: Supervised Learning-to-Rank (LTR) Ingestion

### Objectives
* Replace heuristically hand-tuned weights with machine learning optimization.

### Implementation
1. **Feedback Loop Ingestion**: Standardize logging of recruiter click/save data, message reply rates, and candidate interview progression.
2. **Model**: Train a LightGBM LambdaMART LTR model using candidate features, availability matrices, and user interaction labels.
3. **Loss Function**: Maximize Normalized Discounted Cumulative Gain (NDCG) directly on ranking results.

---

## Phase 3: Dynamic Interview Syllabus Generator

### Objectives
* Generate structured technical validation guides for screening calls.

### Implementation
1. **Concept Mapping**: Map candidate profile skill gaps relative to the JD requirements.
2. **Dynamic Generation**: Output 3 tailored technical questions focusing on identified skill gaps (e.g. asking about Qdrant index replication if the candidate lacks system design experience).
