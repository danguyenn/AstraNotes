# Optional production image. AstraNotes is local-first; this exists so the app
# can also run as a single-user service behind a TLS-terminating reverse proxy.
#
# Multi-stage: a builder installs the pinned dependency set into a venv, and a
# slim runtime stage copies only that venv and runs as a non-root user.

# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy only what the install needs first so the dependency layer caches across
# source edits. README.md is required because pyproject declares `readme`.
COPY pyproject.toml requirements.lock README.md ./
COPY src ./src
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.lock \
 && /opt/venv/bin/pip install --no-deps .

# ---- runtime ----
FROM python:3.12-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    ASTRANOTES_DB_PATH=/data/astranotes.db \
    ASTRANOTES_INSTANCE=/data
# The instance dir (key/secret fallback when env vars are unset) lives on the
# writable /data volume — WORKDIR /app is root-owned, so the non-root user cannot
# create dirs there. In production, supply the keys via -e and /data only holds the db.
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv

# Run as a non-root user that owns the data volume mount point.
RUN useradd --create-home --uid 10001 astra \
 && mkdir -p /data && chown -R astra:astra /data
USER astra

# The database lives on a mounted volume so data survives container restarts.
VOLUME ["/data"]
EXPOSE 5000

# Liveness: hit the index route (proven 200 by the test suite) using stdlib only.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/', timeout=2).status == 200 else 1)"

# Secrets are provided at runtime via -e, never baked into the image.
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "astranotes.wsgi:app"]
