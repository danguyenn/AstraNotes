# ADR-0001 — Adopt the Next.js + Supabase cloud architecture

- **Status:** Superseded by [ADR-0002](ADR-0002-pivot-to-local-first.md)
- **Date:** Week 1.2

## Context
AstraNotes needed a technical path for a solo, 10-week project: a secure, modular
note-taking system. The decision was made with AI assistance using a strong,
role-framed prompt that forced step-by-step reasoning about components, data
model, failure handling, and privacy boundaries — and a comparison against an
Express + Firebase alternative.

## Decision
Adopt **Next.js 14 (App Router) + TypeScript** with **Supabase** (Postgres, Auth,
Realtime) and Tailwind + shadcn/ui. Supabase bundles auth, database, and realtime
into one managed service, minimizing wiring for a solo project, and its
Row-Level Security makes the privacy trust boundary verifiable in one place
(unlike scattering auth checks across Express middleware).

## Consequences
- Enabled an ambitious feature set: accounts, sharing, real-time collaboration, RLS.
- Established a durable **failure-handling principle** that outlived the stack:
  *a secondary write (e.g. version history) must never block or roll back the
  primary write.* This survives into the local-first design — see
  [ADR-0006](ADR-0006-secondary-write-isolation.md).
- Later proved heavier than a solo quarter could realize end-to-end, which led to
  the pivot in ADR-0002.

## AI involvement
A weak prompt ("design a simple storage system") produced a shallow single-table
CRUD answer with no ownership, failure handling, or privacy. The stronger
role+context+constraint prompt produced the component split, RLS trust boundary,
and the primary-vs-secondary write principle that was actually adopted. The
contrast itself was the lesson recorded in the original Architecture Decision Log.
