# ADR-0005 — Full-text search via SQLite FTS5

- **Status:** Accepted
- **Date:** Weeks 4–6

## Context
The cloud vision (FR-03) specified Postgres `tsvector`/`tsquery` for ranked
full-text search. The pivot to SQLite (ADR-0002) needed an equivalent that stays
local-first, with no external search service.

## Decision
Use SQLite's built-in **FTS5** virtual table (`notes_fts`) over title + body,
queried with `MATCH ... ORDER BY rank`. Raw user input is tokenized into a safe
prefix query before it reaches the parser, and locked notes are kept out of the
index entirely.

## Consequences
- Ranked search with snippets, fully on-device (NFR-1), no extra dependency.
- The Week 3.1 edge cases are handled by construction: an empty query yields no
  tokens (the dashboard shows all notes), and special characters (`&`, `'`) are
  stripped to tokens so they cannot break the FTS5 parser (FR-4).
- Encrypted content never appears in results because locked notes are excluded
  from the index (FR-5).

## Trade-off
FTS5 ranking is simpler than Postgres `tsvector` weighting, which is an acceptable
trade for a single-user local store. If the project ever returns to a server, the
`SearchIndex` interface is small enough to re-implement against Postgres without
touching the service layer.
