# ADR-0002 — Pivot from Supabase cloud to local-first Flask + SQLite

- **Status:** Accepted (the central architectural decision of the project)
- **Date:** Weeks 4–6
- **Supersedes:** [ADR-0001](ADR-0001-supabase-cloud-vision.md)

## Context
By the design phase (Week 4.2 UML) and realization phase (Week 6 code), the
project's recent artifacts had all converged on a different stack than the Week 1–2
cloud vision. The UML class diagram, the traceability matrix, and the first
running code were Python + Flask + SQLite, single-user, local-first. The Supabase
vision's most ambitious requirements — multi-user auth, sharing, and real-time
collaboration — are each large efforts on their own and were not realistic to
build and defend end-to-end in a solo 10-week project.

## Decision
Ship the **local-first Flask + SQLite** application as the final product:
single-user, on-device, offline-capable, with SecureNote encryption at rest, a
strict layered architecture, and a real test suite. Preserve the Supabase vision
as the documented future roadmap rather than deleting it.

## Consequences
- **Realized:** Markdown CRUD, folders/tags, full-text search (Postgres `tsvector`
  → SQLite FTS5), version history + restore, encryption at rest, export.
- **Deferred to roadmap:** authentication (FR-04), sharing (FR-05), real-time
  collaboration (FR-06). A `user_id` placeholder column is kept in every table so
  multi-user can return without a schema rewrite.
- **Reframed:** the trust boundary moved from Supabase RLS to "data never leaves
  the device"; the append-only audit log (SPR-03) survives intact
  ([ADR-0007](ADR-0007-append-only-audit-log.md)).
- The pivot resolves the Week 5.2 traceability finding that `VersionHistory` was
  design-led, by **promoting** it to a real requirement (FR-6).

## Why this is the defensible choice
It is the most coherent with the most recent work (UML + running code), it demos
reliably offline, and the deferral of auth/sharing/realtime is an honest, stated
trade — exactly the kind of human-oversight decision a defense should show, rather
than a half-built cloud app.
