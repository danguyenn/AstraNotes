# AstraNotes — Initial Vision (Next.js + Supabase)

This is the original cloud requirement baseline from **Week 1.2** (14 requirements),
refined in **Week 3.1** to 15 (NFR-04 accessibility was added). It is preserved here as the historical baseline
and as the documented future roadmap. The project later pivoted to a local-first
Flask/SQLite implementation — see
[ADR-0002](../decisions/ADR-0002-pivot-to-local-first.md) and the
[traceability matrix](../traceability/traceability-matrix.md) for how each item
was realized, reframed, or deferred.

**Original stack:** Next.js 14 (App Router) + TypeScript, Supabase
(Postgres + Auth + Realtime), Tailwind + shadcn/ui.

## Functional Requirements (Week 3.1, refined)
- **FR-01 — Create, edit, delete with Markdown.** Live preview; persists to Supabase Postgres; deletion confirmed; empty titles default to "Untitled Note - [timestamp]".
- **FR-02 — Folder organization with tagging.** One folder per note (default "Uncategorized"); zero+ tags; folder names unique per account; deleting a non-empty folder prompts move-or-delete.
- **FR-03 — Full-text search.** Postgres `tsvector`/`tsquery`, ranked, highlighted snippets; empty query shows all; special characters sanitized.
- **FR-04 — Email/password authentication.** Supabase Auth, HTTP-only cookies, generic login errors (no user enumeration), 8-char minimum.
- **FR-05 — Share a note (read / read-write).** Share by email; "Shared with me"; revocable; no self-share; clear "user not found".
- **FR-06 — Real-time collaborative editing.** Supabase Realtime; last-write-wins at field level; "Sync paused" banner on disconnect.
- **FR-07 — Version history with restore.** Snapshot per save; preview + restore (reversible); 50-version cap; owner-only visibility.
- **FR-08 — Export as Markdown.** Single `.md` and bulk `.zip`; sanitized filenames; empty-folder message.

## Non-Functional Requirements
- **NFR-01 — Page load performance.** FCP < 1.5s up to 1,000 notes; Lighthouse ≥ 90.
- **NFR-02 — Mobile responsiveness.** Usable to 375px; hamburger sidebar; 44px touch targets; editor/preview toggle on mobile.
- **NFR-03 — Testability by design.** Storage, access control, and sync separated and independently unit-testable.
- **NFR-04 — Accessibility baseline.** WCAG 2.1 AA on core flows (added in Week 3.1).

## Security, Privacy & Reliability
- **SPR-01 — Row-level security as the trust boundary.** RLS on all user tables; `owner_id` the single trust boundary; enforced at the DB, not the app.
- **SPR-02 — Encryption in transit (and at rest).** HTTPS/TLS everywhere, HSTS; Supabase AES-256 at rest.
- **SPR-03 — Graceful degradation / audit log.** Append-only `audit_log` for shared-note access; local-only editing on Realtime outage.

## What the pivot kept, reframed, and deferred
- **Kept & realized:** Markdown CRUD (FR-01 → FR-1/2/3), folders+tags (FR-02 → FR-7), search (FR-03 → FR-4, Postgres FTS → SQLite FTS5), version history (FR-07 → FR-6), export (FR-08 → FR-8).
- **Reframed:** the trust boundary moved from Supabase RLS (SPR-01) to "data never leaves the device"; encryption-at-rest is realized per-note via Fernet; the append-only audit log (SPR-03) survives intact.
- **Deferred to roadmap:** auth (FR-04), sharing (FR-05), real-time collaboration (FR-06) — they require a server and multiple users, which the local-first scope trades away on purpose. The `user_id` placeholder column keeps the door open.
