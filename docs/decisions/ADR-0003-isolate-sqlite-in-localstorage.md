# ADR-0003 — Isolate SQLite inside LocalStorage (return dicts, not rows)

- **Status:** Accepted
- **Date:** Week 6 (quality audit)

## Context
The class diagram claims `LocalStorage` is the only component that knows about
SQLite. The Week 6 quality audit found this boundary was only partially real:
`LocalStorage.query()` returned `list[sqlite3.Row]`, so `NoteRepository` depended
on the driver's row interface. Swapping the database later would have silently
broken the repository — the boundary existed on paper, not in the code.

## Decision
`LocalStorage` is the **only** module that imports `sqlite3`. `query()` converts
every row to a plain `dict` before returning, and every `sqlite3.Error` is
re-raised as a domain-level `StorageError`. Callers depend on a shape (a dict-like
row), not on a driver type.

## Consequences
- The repository and everything above it are driver-agnostic.
- A single fitness test (`tests/test_architecture.py`) and a dict-return test
  (`tests/test_storage.py`) keep the boundary honest.
- Errors surface as `StorageError`, enabling the distinct failure UI (NFR-2).

## Lesson recorded
The audit's deeper finding: *a type that claims encapsulation but leaks a driver
type does not actually provide it.* Write the test that would fail before the code
exists, for any boundary you want to claim.
