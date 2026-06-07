# Test Report

> Measured run, recorded per the project rule against unverified test claims.
> Re-run `pytest` after any change and update these numbers from the actual output.

- **Command:** `pytest --cov=astranotes --cov-report=term-missing`
- **Environment:** Python 3.14.3, Windows (win32), pytest, coverage
- **Result:** **77 passed**, 0 failed
- **Total coverage:** **89%** (753 statements, 83 missed)

## Per-module coverage (from the measured run)

| Module | Cover |
|--------|------:|
| `domain/note.py` | 95% |
| `errors.py` | 100% |
| `timeutil.py` | 100% |
| `config.py` | 88% |
| `services/note_service.py` | 96% |
| `services/encryption_service.py` | 100% |
| `services/session.py` | 80% |
| `storage/local_storage.py` | 96% |
| `storage/note_repository.py` | 91% |
| `storage/search_index.py` | 100% |
| `storage/version_history.py` | 100% |
| `storage/audit_log.py` | 100% |
| `web/app.py` | 93% |
| `web/deps.py` | 100% |
| `web/markdown_render.py` | 91% |
| `web/routes/*` | 72–100% |
| `wsgi.py` | 0% (prod entry; imported, not exercised in tests) |
| **TOTAL** | **89%** |

## Verified properties
- A SecureNote's body is **ciphertext at rest** and is **not searchable while locked**.
- Deleting a note **retains** its version history; restoring a version is itself reversible.
- The `audit_log` rejects `UPDATE`/`DELETE` at the database level.
- Rendered note content cannot inject `<script>`.
- A corrupt database surfaces a `StorageError`, not a crash (NFR-2).
- Invalid configuration (an ill-formed encryption key, an uncreatable database
  directory) fails fast with a `ConfigError` at startup (NFR-2).
- Every response carries the defensive HTTP headers (CSP, `X-Frame-Options`,
  `X-Content-Type-Options`, `Referrer-Policy`).
- No module imports across a layer boundary (architecture fitness test).

## Uncovered lines
Mostly defensive route branches (e.g. `StorageError` on a write failure, some
locked-note redirect paths) and the `wsgi:app` server entry point — none of which
affect the verified behaviors above. (The `config.load_config` env-var branches are
now exercised by `tests/test_config.py`, raising that module 38% → 88%.)
