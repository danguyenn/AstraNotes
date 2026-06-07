# ADR-0006 — Primary write before secondary, no cascading rollback

- **Status:** Accepted
- **Date:** Weeks 4–6 (principle carried from [ADR-0001](ADR-0001-supabase-cloud-vision.md))

## Context
Saving a note touches several stores: the `notes` row (primary), plus a version
snapshot, the search index, and tags (secondary). The original Architecture
Decision Log established the principle that *version history is a secondary
concern and should not block the primary write path.* The local-first design
needs the same guarantee without a single ACID transaction spanning all of them.

## Decision
`NoteRepository.save` commits the **primary** write (the `notes` row) first, then
performs the secondary writes (snapshot → index → tags) in order. A failure in a
secondary concern is never allowed to roll back the committed note.

## Consequences
- The user never loses a saved note because, say, the search index hiccupped.
- Each store is written through `LocalStorage` with its own commit, which matches
  the principle rather than fighting it with cross-store transactions.
- Read paths tolerate slight secondary lag (e.g. an index entry written a moment
  after the note), which is acceptable for a single-user local app.

## Trade-off
This favors durability of the user's primary data over strict cross-store
atomicity. For a multi-user server this might warrant a real transaction; for
local-first single-user it is the right call and keeps `LocalStorage` simple.
