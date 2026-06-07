# ADR-0007 — Append-only audit log enforced by database triggers

- **Status:** Accepted
- **Date:** Weeks 4–6 (local-first realization of SPR-03)

## Context
The cloud vision's SPR-03 required an append-only `audit_log` for security events,
with RLS blocking UPDATE and DELETE. The local-first product has no RLS, but the
same tamper-evidence goal applies to the security-sensitive operations that remain:
locking, unlocking, and restoring notes.

## Decision
Keep an `audit_log` table and enforce append-only **at the database level** with
two triggers that `RAISE(ABORT)` on any UPDATE or DELETE. The `AuditLog` class
only ever inserts and reads; `NoteService` records a `lock`, `unlock`, or
`restore` event on each such action.

## Consequences
- The trail cannot be silently rewritten, even by code with database access — the
  guarantee lives in the schema, not in application discipline.
- Surfaced read-only on the Settings page for transparency.
- Verified by `tests/test_audit.py`, which asserts that UPDATE and DELETE both
  raise `StorageError`.

## Trade-off
Append-only means the log grows unbounded. For a single-user local app this is
negligible; a future version could add a rotation/export policy without weakening
the append-only guarantee (rotation would archive, not mutate).
