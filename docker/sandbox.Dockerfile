# Minimal, built once and reused across every task run (DockerSandbox
# checks for this image and only builds it if missing).
FROM python:3.11-slim

RUN pip install --no-cache-dir pytest

# Non-root, per the security review -- cheap to add, no downside here.
RUN useradd -m sandboxuser
USER sandboxuser

WORKDIR /repo

# No CMD/ENTRYPOINT that exits -- the container is started with
# `tail -f /dev/null` (see DockerSandbox.setup) so it stays alive between
# repeated `docker exec` calls, one container per task attempt.
