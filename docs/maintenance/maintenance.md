# Maintenance Notes

## Routine maintenance
- **Dependencies:** abstract ranges (with upper bounds) in `pyproject.toml`; the exact transitive set is pinned in `requirements.lock`. Regenerate the lock with `pip-compile --extra prod -o requirements.lock pyproject.toml` after a bump, and re-run `pytest`.
- **Quality gates:** `ruff check`, `ruff format --check`, and `mypy src` run in CI and via `make check`. Fix findings rather than broadening the `pyproject` ignore lists; `mypy` holds `domain/*` and `markdown_render` to a strict bar.
- **Tests are the gate:** never claim a change is safe without running `pytest` and citing the result (see [test-report.md](../testing/test-report.md)). Update that report's numbers from the actual output, not from memory.
- **Architecture fitness:** `tests/test_architecture.py` fails the build if a new module imports across a layer boundary — keep the layering intact rather than suppressing it.
- **Diagrams:** the Mermaid in the docs is the source of truth (GitHub renders it inline). Re-render the PNG/SVG exports in `docs/architecture/diagrams/` with `make diagrams` (or `python tools/render_diagrams.py`, which needs Node + npx) after editing any diagram.

## Logging & observability
- The app configures logging in the factory (level via `ASTRANOTES_LOG_LEVEL`, default `INFO`) and logs app start plus lock/unlock/restore and storage/encryption failures under the `astranotes.*` loggers.
- Log lines carry **note ids and event names only** — never keys, the session secret, the passphrase hash, or note content. Preserve that rule when adding log points.

## Database
- Schema lives in `src/astranotes/storage/schema.sql` and is applied idempotently (`CREATE ... IF NOT EXISTS`) at startup.
- There is no migration framework yet (single-user local scope). For a backward-incompatible schema change, add a small, explicit migration step before broad rollout, and bump the version.
- The `audit_log` is append-only and grows unbounded; a future rotation policy should **archive**, never mutate, to preserve the SEC-4 guarantee.

## Keys & secrets
- Rotating `ASTRANOTES_ENCRYPTION_KEY` requires decrypting locked notes with the old key and re-encrypting with the new one — do this with a maintenance script before swapping the key, or notes locked under the old key become unreadable.
- Never commit real keys; `.gitignore` already covers `*.key`, `instance/`, and `.env`.

## Extending the app (common changes)
- **New feature:** add the use case to `NoteService`, persistence to `NoteRepository`/`schema.sql`, a thin route, a template, and tests — in that order, keeping the layer rule.
- **Re-introducing multi-user (deferred FR-04/05/06):** the `user_id` placeholder columns exist; add an auth layer and per-user filters, and restore an authorization boundary (the SPR-01 RLS equivalent).
- **Swapping the database:** only `LocalStorage` imports the driver; re-implement it (and `SearchIndex`) against the new engine without touching services or web (ADR-0003/0005).

## Known limitations / future work
- No automated migrations; no key-rotation script; FTS5 ranking is simpler than Postgres `tsvector` weighting.
- Accessibility (NFR-04) is partial (semantic HTML + labels) — a full WCAG audit is future work.
- Deferred roadmap: authentication, sharing, real-time collaboration.
