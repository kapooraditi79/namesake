# Base image for every task container. One throwaway container per task run.
# Target-repo-specific dependencies are installed at container-run time by
# sandbox/runner.py (each task can pin different deps), not baked in here.

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
