# Deployment

AstraNotes is local-first: the primary "deployment" is running it on your own
machine. An optional single-user networked mode is documented for completeness.

## Local development
```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -e ".[dev]"
astranotes                    # Flask dev server on http://127.0.0.1:5000
```
On first run, AstraNotes creates a git-ignored `instance/` folder with the SQLite
database and generated dev keys.

## Production (single-user, networked)
```bash
pip install -e ".[prod]"
# Reproducible alternative (pinned transitive set):
#   pip install -r requirements.lock && pip install --no-deps .
# Set stable keys so they survive restarts:
export ASTRANOTES_ENCRYPTION_KEY=...   # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
export ASTRANOTES_SECRET_KEY=...       # python -c "import secrets; print(secrets.token_hex(32))"
export ASTRANOTES_PASSPHRASE_SHA256=...# optional unlock gate
waitress-serve --listen=0.0.0.0:5000 astranotes.wsgi:app
```
Run behind a **TLS-terminating reverse proxy** (nginx/Caddy). Do not expose the
Waitress port directly.

## Docker (optional)
```bash
docker build -t astranotes .
docker run -p 5000:5000 \
  -e ASTRANOTES_ENCRYPTION_KEY=... \
  -e ASTRANOTES_SECRET_KEY=... \
  -v astra-data:/data astranotes
```
The image is a **multi-stage build** that installs the pinned `requirements.lock`
into a venv and runs as a **non-root user** (`astra`, uid 10001). It declares a
`HEALTHCHECK` against `GET /`, puts the database at `/data/astranotes.db`, and sets
`ASTRANOTES_INSTANCE=/data` so the key/secret fallback files land on the writable
volume (the `/app` workdir is root-owned). Secrets are passed at runtime via `-e`
and are never baked into the image.

## Configuration reference
| Variable | Purpose | Default |
|----------|---------|---------|
| `ASTRANOTES_ENCRYPTION_KEY` | Fernet key for SecureNotes | generated to `instance/encryption.key` |
| `ASTRANOTES_SECRET_KEY` | Flask session signing | generated to `instance/flask_secret` |
| `ASTRANOTES_PASSPHRASE_SHA256` | SHA-256 of the unlock passphrase | unset (gate open) |
| `ASTRANOTES_DB_PATH` | SQLite file location | `instance/astranotes.db` |

## Backup & restore
- The single SQLite file is the entire application state — copy it to back up.
- **Back up the encryption key separately and securely.** Without it, locked notes
  cannot be decrypted.
- Health check: `GET /` returns 200 when the app is healthy (used by the Docker
  `HEALTHCHECK`).

## CI
`.github/workflows/ci.yml` runs the full quality gate on every push and pull request
to `main`: `ruff check`, `ruff format --check`, `mypy src`, then `pytest` with
coverage (pip cache enabled).
