# Backlog & User Stories (Week 2.2)

The original prioritized backlog from the cloud-vision phase. The eight user
stories trace to the Week 1.2 requirements. The **Realized as** column shows how
each landed in the shipped local-first product (see the
[traceability matrix](../traceability/traceability-matrix.md)).

## User stories

| ID | Story | Original priority | Realized as |
|----|-------|------------------|-------------|
| US-01 | Create and save a note (Markdown) | High | **FR-1** ✅ |
| US-02 | Edit an existing note | High | **FR-2** ✅ |
| US-03 | Delete a note | High | **FR-3** ✅ (version history retained) |
| US-04 | Organize notes into folders | Medium | **FR-7** ✅ (folders + tags) |
| US-05 | Search notes by keyword | Medium | **FR-4** ✅ (SQLite FTS5) |
| US-06 | Sign up and log in | High | Deferred → roadmap (single-user local) |
| US-07 | Notes private by default (RLS) | High | Reframed → **FR-5** (encryption at rest) + device trust boundary |
| US-08 | Responsive layout | Low | **NFR-2**-adjacent ✅ (responsive CSS to 375px) |

### Acceptance criteria (abridged, as originally written)
- **US-01:** single-click create; persists across reloads; empty note rejected/handled; Markdown renders in preview.
- **US-02:** click opens in editor with content; saves persist + bump timestamp; unsaved-changes prompt.
- **US-03:** delete from list or note view; confirmation dialog; gone from list and search after delete.
- **US-04:** create/rename/delete folders; one folder per note (default Uncategorized); move updates counts; deleting a non-empty folder prompts move-or-delete.
- **US-05:** keyword matches title/body; clear empty state; results within a reasonable time for a few hundred notes.
- **US-06–US-08:** auth, privacy-by-default, and responsive layout as detailed in the [initial vision](../requirements/initial-vision-supabase.md).

## Prioritization rationale (original)
Ordered by dependency and fastest path to a working vertical slice: auth and CRUD
first (everything depends on a logged-in user who can create notes), then folders
and search (day-to-day usefulness), with responsive layout last (polish, blocks
nothing).

> **Pivot note.** When the project moved to local-first single-user, the
> dependency that put auth (US-06) first disappeared. CRUD (US-01–03) became the
> true first vertical slice — which is exactly what the Week 6 realization built.

## How AI helped (original reflection)
Copilot Chat drafted ~12 stories from the Week 1.2 requirements; several were too
granular (separate stories for "bold" vs "italic") and were combined into US-01
and trimmed to 8. Early acceptance criteria were vague ("works as expected") and
were rewritten to be demo-verifiable; US-07's criteria had to be hand-fixed from
UI checks to database-level RLS enforcement. Sprint Zero stayed mostly human —
Copilot's suggestion of full CI/CD + monitoring was cut as too much for a solo
10-week project.
