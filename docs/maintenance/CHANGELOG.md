# Changelog

All notable changes to AstraNotes. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions use semantic versioning.

## [1.0.0] — Final submission
The first coherent end-to-end release: the local-first product plus the full SDLC
artifact set.

### Added
- Markdown notes: create, edit, delete with live preview (FR-1, FR-2, FR-3).
- Full-text search over title + body via SQLite FTS5, with empty/no-result/special-character handling (FR-4).
- SecureNotes: encryption at rest (Fernet), session unlock gate, exclusion from search while locked (FR-5).
- Version history with reversible restore; snapshots retained after note deletion (FR-6).
- Folders and tags with sidebar filtering (FR-7).
- Export a single note as `.md` or a folder/all as `.zip` with sanitized filenames (FR-8).
- Append-only audit log for lock/unlock/restore, enforced by DB triggers (SEC-4).
- Server-side Markdown sanitization (bleach) + escape-first live preview (SEC-3).
- Strict layered architecture enforced by an automated fitness test (NFR-3).
- Test suite (77 tests, 89% coverage) and a CI workflow that gates on `ruff` lint, `ruff format`, `mypy`, and `pytest`.
- HTTP security headers on every response — CSP, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` (SEC-3).
- Fail-fast configuration validation: an ill-formed encryption key or an uncreatable database directory raises a clear `ConfigError` at startup (NFR-2).
- Secret-safe structured logging of app start and lock/unlock/restore/storage events.
- Reproducible dependency lockfile (`requirements.lock`), `ruff`/`mypy` tool config, and a `Makefile` task runner.
- Hardened multi-stage Docker image: non-root user, `HEALTHCHECK`, lockfile-based install.
- Complete SDLC documentation: requirements, planning, architecture + UML, ADRs, traceability, testing, security, deployment, maintenance, and AI-usage log.

### Changed (reconciliations from the quarter)
- **Pivoted** from the Next.js + Supabase cloud vision to local-first Flask + SQLite (ADR-0002).
- Empty-title behavior reconciled to **reject** (Week 6 realization) rather than default to "Untitled" (Week 3.1 proposal) — ADR-0004.
- Search engine swapped from Postgres `tsvector` to SQLite FTS5 (ADR-0005).
- `LocalStorage.query()` returns plain dicts, not `sqlite3.Row`, fixing the leaky storage boundary the Week 6 audit found (ADR-0003).

### Deferred (roadmap)
- Authentication (FR-04), sharing (FR-05), and real-time collaboration (FR-06) — `user_id` placeholder retained for their return.

### Security
- No secrets in the repository; keys sourced from env/keyfile and git-ignored.
- SecureNote bodies stored as ciphertext at rest; key isolated from note data.
