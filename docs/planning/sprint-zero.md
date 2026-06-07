# Sprint Zero Plan (Week 2.2)

Sprint Zero is all prep, no feature code: make sure that when feature work starts,
the project structure and tooling are already in place. Recorded here as the
original cloud-vision plan, annotated with how it was actually realized after the
local-first pivot.

| Area | Original (Supabase) plan | Realized (local-first) |
|------|--------------------------|------------------------|
| Project setup | Next.js 14 + TS + Tailwind + shadcn/ui; push to GitHub; `planning/` docs | Python package (`src/astranotes`), `pyproject.toml`, this `docs/` tree |
| Data store | Supabase project, `notes` schema, Auth, RLS policies | SQLite `schema.sql` (notes/folders/tags/versions/fts/audit), `user_id` placeholder for future multi-user |
| Dev workflow | Copilot in VS Code, `.env.local` for keys, README | `.env.example` + git-ignored `instance/` keys, README |
| Technical decisions | Markdown editor lib, folder data model | Server-side `markdown`+`bleach`, local `preview.js`; folders as a table with FK |
| Risk reduction | Prototype Supabase Auth; test RLS with two accounts | N/A (auth deferred); risk shifted to encryption + layering, covered by tests |
| Planning artifacts | Finalize backlog; trace stories to requirements; DoD check | Backlog → traceability matrix; DoD applied throughout |

## Why it changed
The Supabase Sprint Zero front-loaded auth and RLS because the cloud vision made
them prerequisites. The local-first pivot removed that dependency, so the real
Sprint Zero work became: clean layered package layout, the SQLite schema, key
management, and the test harness. The intent — *don't figure out config mid-sprint*
— stayed the same; only the toolchain changed.

## How AI helped (original reflection)
Sprint Zero was mostly human thinking. Copilot suggested a full CI/CD pipeline and
monitoring; both were cut as too heavy for a solo 10-week project. What was kept
was the minimum that has to exist before feature code: repo setup, data store,
key/config handling, and documented technical decisions. (A single, bounded CI
workflow — `pytest` on push/PR — was added later, in the realization phase.)
