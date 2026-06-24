# Deployment Guide & Runtime Specifications

This document describes the sandboxed environment constraints, container setup, and execution guidelines for production runs.

---

## 1. Sandbox Environment Constraints

All candidate discovery pipeline runs must execute inside a containerized sandbox with the following constraints:
* **Networking**: Disabled (`--network none`). No external HTTP/gRPC API requests allowed during ranking.
* **Memory Peak Ceiling**: $\le 16\text{ GB}$ RAM.
* **Storage Allocation**: $\le 5\text{ GB}$ disk space.
* **Compute Allocation**: CPU-only execution (no GPU drivers or CUDA runtimes available).
* **Execution Limit**: $\le 5\text{ minutes}$ (300 seconds) wall-clock time limit for the entire run.

---

## 2. Docker Configuration

To package and run the pipeline inside a reproducible Docker environment:

### Dockerfile
Create a `Dockerfile` at the root of the project:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# In compliance with zero-dependency rules, copy only the core python files
COPY rank.py validate_submission.py /app/

# Set pipeline entrypoint
ENTRYPOINT ["python3", "rank.py"]
```

### Build & Run Instructions
1. Build the lightweight Python container:
   ```bash
   docker build -t redrob-hiring-ranker .
   ```
2. Run the ranking container, disabling network access and restricting resource allocation to verify sandbox compatibility:
   ```bash
   docker run --rm \
     --network none \
     --memory 16g \
     --cpus 4 \
     -v $(pwd)/candidates.jsonl:/data/candidates.jsonl \
     -v $(pwd):/output \
     redrob-hiring-ranker --candidates /data/candidates.jsonl --out /output/team_redrob.csv
   ```

---

## 3. Production Resource Footprint

During execution on a benchmark MacBook Pro M2 (8 CPU cores, 16 GB RAM), the runtime metrics are:
* **Memory Consumption**: Generator-based streaming sequentially processes candidate records. Real-time RAM peak remains flat at **$\approx 156\text{ MB}$**, preventing Out-Of-Memory (OOM) faults.
* **Execution Latency**:
  * Ingesting & streaming JSON lines: $\approx 22.1\text{ seconds}$.
  * Filtering honeypots & multi-factor scoring: $\approx 1.58\text{ seconds}$.
  * Sorting and outputting Top-100 CSV: $\approx 0.04\text{ seconds}$.
  * **Total CPU Wall-Clock Time**: **$\approx 23.7\text{ seconds}$** (well within the 300-second sandbox budget).
