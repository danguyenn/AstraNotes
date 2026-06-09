# AstraNotes

A **secure, local-first, modular Markdown note-taking application** — built solo
across a quarter as an exercise in AI-native software development with strong human
oversight (CSEN 296B). Everything runs on your own machine: a small Flask server, a
single SQLite file, no network, no accounts, no cloud.

> **Demo video:** _<paste your ~5-minute demo link here>_ &nbsp;|&nbsp; Recording guide: [`demo/demo-script.md`](demo/demo-script.md)

---

## What it does

| Feature | |
|---|---|
| ✍️ **Markdown notes** | Create, edit, delete with a live preview (FR-1/2/3) |
| 🔎 **Full-text search** | Ranked search over title + body via SQLite FTS5, with snippets (FR-4) |
| 🔒 **SecureNotes** | Mark a note private → encrypted at rest (Fernet/AES) and hidden from search until unlocked (FR-5) |
| 🕘 **Version history** | Every save snapshots; restore any version, and the restore is itself reversible (FR-6) |
| 🗂️ **Folders & tags** | Organize and filter from the sidebar (FR-7) |
| ⤓ **Export** | One note as `.md`, or a folder/all as `.zip` (FR-8) |
| 🧾 **Audit log** | Append-only record of lock/unlock/restore, enforced by DB triggers (SEC) |

## The story behind it (why this is defensible)

AstraNotes **pivoted** mid-quarter. It started as an ambitious **Next.js + Supabase**
cloud app (multi-user, sharing, real-time). By the design and realization phases the
work had converged on a pragmatic **Python + Flask + SQLite, local-first** build. The
project shipped the local-first version and **deferred** auth/sharing/realtime to a
documented roadmap. That pivot — and the human overrides along the way — is the heart
of the AI-native story: AI accelerated drafting; **human judgment decided what
shipped.** See [`docs/decisions/ADR-0002-pivot-to-local-first.md`](docs/decisions/ADR-0002-pivot-to-local-first.md)
and the [AI-usage log](docs/ai-usage/ai-usage-log.md).

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/activate         # Windows  (use: source .venv/bin/activate on macOS/Linux)
pip install -e ".[dev]"

# (optional) seed realistic demo notes, incl. a locked SecureNote
python demo/seed_data.py

# run the app → http://127.0.0.1:5000
astranotes
```

Run the tests:

```bash
pytest --cov=astranotes --cov-report=term-missing
# 77 passed, 89% coverage  (see docs/testing/test-report.md)
```

**Quality tooling.** CI gates on `ruff` (lint + format), `mypy` (strict on the
fully-typed `domain`/`markdown_render` modules), and `pytest` with coverage.
A `Makefile` wraps the common tasks — `make check` runs the whole gate locally,
`make run` / `make seed` / `make docker-build` cover the rest.

## Architecture at a glance

Strict layered design — **imports only ever point downward**, and a fitness test
fails the build if that's violated.

```
web        Flask routes · Jinja templates · static (CSS + local preview JS)
  ↓
services   NoteService · EncryptionService · UserSession
  ↓
storage    LocalStorage · NoteRepository · VersionHistory · SearchIndex · AuditLog
  ↓
domain     Note · SecureNote   (pure entities + invariants)
```

- The **only** module that imports `sqlite3` is `LocalStorage`; it returns plain dicts and wraps errors as `StorageError`.
- The title invariant lives in the **domain constructor**, so an invalid note cannot exist.
- SecureNote bodies are **ciphertext at rest**; the key is read from the environment or a git-ignored key file — never hardcoded, never in the database.

Full design + UML diagrams: [`docs/architecture/`](docs/architecture/).

## Project structure

```
src/astranotes/        application (domain · services · storage · web)
tests/                 pytest suite (unit · integration · architecture fitness)
docs/                  the full SDLC artifact set (see index below)
demo/                  seed_data.py · demo-script.md · recording-guide.md · capture_screenshots.py · screenshots/
tools/                 dev tooling (render_diagrams.py → docs/architecture/diagrams/)
.github/workflows/     CI (ruff + mypy + pytest on push/PR)
Makefile               developer task runner (make check / run / docker-build)
requirements.lock      pinned transitive deps for reproducible builds
```

## Documentation index

| Area | |
|------|---|
| Requirements | [final-requirements](docs/requirements/final-requirements.md) · [initial cloud vision](docs/requirements/initial-vision-supabase.md) |
| Planning | [backlog](docs/planning/backlog.md) · [sprint-zero](docs/planning/sprint-zero.md) · [working-agreement](docs/planning/working-agreement.md) · [definition-of-done](docs/planning/definition-of-done.md) · [waterfall-gantt](docs/planning/waterfall-gantt.md) |
| Architecture | [overview](docs/architecture/overview.md) · [UML (Mermaid)](docs/architecture/uml.md) · [rendered diagram gallery](docs/architecture/diagrams/) |
| Decisions | [ADR-0001…0007](docs/decisions/) |
| Traceability | [matrix (gaps resolved)](docs/traceability/traceability-matrix.md) |
| Testing | [test-plan](docs/testing/test-plan.md) · [test-report](docs/testing/test-report.md) |
| Security | [security-notes](docs/security/security-notes.md) · [threat-model](docs/security/threat-model.md) |
| Deployment & maintenance | [deployment](docs/deployment/deployment.md) · [maintenance](docs/maintenance/maintenance.md) · [CHANGELOG](docs/maintenance/CHANGELOG.md) |
| AI-native practice | [ai-usage-log](docs/ai-usage/ai-usage-log.md) |
| Original graded artifacts | [docs/artifacts-original/](docs/artifacts-original/) (the 11 source PDFs) |

## How AI was used (and overseen)

Built AI-natively under the [Working Agreement](docs/planning/working-agreement.md)
and [Definition of Done](docs/planning/definition-of-done.md). AI drafted
requirements, scaffolding, and docs; a human review gate decided what to **accept,
refine, or reject** at each stage — e.g. moving validation into the domain, keeping
version history out of `Note`, downgrading dishonest traceability labels, and
rejecting test theater. The full trail is in the
[AI-usage log](docs/ai-usage/ai-usage-log.md). Test claims here are measured, not
inherited: see [test-report](docs/testing/test-report.md).

## License

[MIT](LICENSE) © 2026 David Nguyen
