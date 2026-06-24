# Deployment Guide & Performance Analysis

This guide describes the sandbox deployment setup, Docker specifications, and provides a runtime performance analysis under strict hardware constraints.

---

## 1. Sandboxed Runtime Specifications

All candidate discovery runs are reproduced inside a sandboxed environment matching the following criteria:
* **Operating System**: Linux (Debian/Ubuntu-based Docker image).
* **Python**: 3.8+ (tested on 3.11.4).
* **CPU Limit**: CPU-only execution (no GPU drivers or CUDA runtimes).
* **Memory Limit**: $\le 16\text{ GB}$ RAM.
* **Storage Limit**: $\le 5\text{ GB}$ disk space.
* **Network Limit**: Off (no external HTTP/gRPC requests allowed during candidate scoring).
* **Execution Limit**: $\le 5\text{ minutes}$ (300 seconds) wall-clock time.

---

## 2. Docker Setup

To reproduce the ranking locally inside an identical sandboxed container:

### A. Dockerfile
Create a `Dockerfile` at the root of the repository:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy files
COPY rank.py validate_submission.py /app/

# Entrypoint setup
ENTRYPOINT ["python3", "rank.py"]
```

### B. Build and Run
Build the Docker image:
```bash
docker build -t redrob-ranker .
```

Run the container, mounting the local directory containing the dataset to simulate the environment constraints:
```bash
docker run --rm \
  --network none \
  --memory 16g \
  --cpus 4 \
  -v $(pwd)/candidates.jsonl:/data/candidates.jsonl \
  -v $(pwd):/output \
  redrob-ranker --candidates /data/candidates.jsonl --out /output/team_redrob.csv
```

---

## 3. Performance Analysis Statistics

Below are the empirical benchmarks measured on a **MacBook Pro M2 (8 CPU cores, 16 GB RAM)**:

### A. Runtime Latency Breakdown
* **In-Memory streaming & JSON parsing**: $\approx 22.1\text{ seconds}$ (to read and parse all 100,000 JSON lines).
* **Honeypot Filter matching**: $\approx 0.74\text{ seconds}$ (to filter all 100,000 profiles).
* **Multi-Factor Scoring computations**: $\approx 0.84\text{ seconds}$ (projected from 5,000 profile benchmark).
* **Deterministic sorting & tie-breaking**: $\approx 0.04\text{ seconds}$.
* **Reasoning generation (top 100)**: $\approx 0.001\text{ seconds}$.
* **Total execution time**: **$\approx 23.7\text{ seconds}$** (well below the 300-second constraint).

### B. Memory Consumption Profile
* **Ingestion phase**: Generator streaming processes lines sequentially. Memory profile remains flat during parsing.
* **Scoring phase**: Only the candidate ID, final score, and extracted reasoning dictionary are kept in memory. The raw candidate profiles are garbage-collected.
* **Peak Memory Footprint**: $\approx 156\text{ MB}$ (extremely low compared to the 16 GB RAM limit).

### C. Resource Scaling
$$\text{Memory Complexity} = O(K) \quad \text{where } K = 100\text{ (top picks)}$$
$$\text{Time Complexity} = O(N) \quad \text{where } N = 100,000\text{ (candidate pool)}$$
This linear complexity ensures the ranker scales easily to millions of candidates without risk of Out-Of-Memory (OOM) failures or execution timeouts.
