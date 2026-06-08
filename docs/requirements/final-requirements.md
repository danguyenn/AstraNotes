# AstraNotes — Final Requirement Baseline (Local-First)

This is the **authoritative requirement set for the shipped product.** It
reconciles the quarter's two technical directions: the Week 1–2 cloud vision
(Next.js + Supabase) and the Week 4–6 realization (Python + Flask + SQLite,
local-first). The project pivoted to local-first; see
[ADR-0002](../decisions/ADR-0002-pivot-to-local-first.md). The original cloud
requirements are preserved verbatim in
[initial-vision-supabase.md](initial-vision-supabase.md) and mapped here through
the [traceability matrix](../traceability/traceability-matrix.md).

Requirement IDs use the local-first numbering established in the Week 5.2
traceability matrix and Week 6 realization.

## Functional Requirements

### FR-1 — Create a note with Markdown
The system shall let a user create a note with a title and a Markdown body and
persist it to local storage. The editor renders a live preview as the user
types.
- **AC1:** `## Hello **world**` renders as a styled heading with bold text in the preview.
- **AC2:** A note with an empty or whitespace-only title is **rejected** with a validation message.
- **AC3:** Saved content round-trips to SQLite and back without losing formatting.
- **Realized by:** `Note`, `NoteService.create_note`, `NoteRepository.save`, `static/preview.js`.

> **Reconciliation note.** The Week 3.1 refinement proposed defaulting an empty
> title to "Untitled Note - [timestamp]". The Week 6 realization instead
> **rejects** empty titles in the `Note` constructor, and the Week 5.2 activity
> diagram models a validation-error loop (not a default). The shipped product
> follows the realized behavior — an invalid `Note` cannot exist in the system —
> and this divergence is recorded here as a deliberate human decision.

### FR-2 — Edit a note
The system shall let a user edit a note's title and body and persist the update.
The editor warns before navigating away with unsaved changes.
- **AC1:** Opening a note loads its current content into the editor.
- **AC2:** Saving updates the content and bumps the modified timestamp.
- **AC3:** Leaving with unsaved edits triggers a browser confirmation.
- **Realized by:** `Note.update_content`, `NoteService.edit_note`. Behavior modeled by the **edit activity diagram** ([UML](../architecture/uml.md)) — resolves Week 5.2 gap.

### FR-3 — Delete a note, preserving version history
The system shall let a user delete a note (with confirmation) while retaining
its version snapshots for possible restoration.
- **AC1:** Deleting prompts for confirmation, then removes the note from lists and search.
- **AC2:** The note's version history survives the deletion.
- **Realized by:** `NoteRepository.delete` (version table has no FK), `SearchIndex.remove`. Behavior modeled by the **delete activity diagram** — resolves Week 5.2 gap.

### FR-4 — Full-text search
The system shall let a user search across note titles and bodies and show ranked
results with snippets, or a clear empty/no-results state.
- **AC1:** Searching a keyword returns matching notes with a highlighted snippet.
- **AC2:** An empty query is treated as "no search" (the dashboard shows all notes).
- **AC3:** A query with special characters (e.g. `&`, `'`) does not crash the parser.
- **Realized by:** `SearchIndex` (SQLite FTS5), `NoteService.search_notes`. Behavior modeled by the **search activity diagram** with edge cases — resolves Week 5.2 gap.

### FR-5 — Private notes with encryption at rest
The system shall let a user mark a note private. A private note's body is
encrypted at rest and excluded from search; it is revealed only after the
session is unlocked.
- **AC1:** Locking a note stores its body as ciphertext (verifiable in the `.db`).
- **AC2:** A locked note does not appear in search results.
- **AC3:** Viewing a locked note requires an unlocked session.
- **Realized by:** `SecureNote`, `EncryptionService` (Fernet/AES-128-CBC+HMAC), `UserSession`.

### FR-6 — Version history and restore
The system shall snapshot a note on every save, let the user browse and restore
past versions, and make restoring itself reversible.
- **AC1:** Three saves produce three history entries, newest first.
- **AC2:** Restoring an older version replaces the current content and adds a new entry.
- **Realized by:** `VersionHistory`, `NoteService.restore_version`.

> **Promotion note.** Week 5.2 found `VersionHistory` was "design-led" — present
> in the UML but unjustified by the baseline — and recommended either adding a
> version requirement or removing the class. The decision was to **promote**
> version history to FR-6, so the design earns its place.

### FR-7 — Folders and tags
The system shall let a user organize notes into folders (one per note) and apply
zero or more tags, and filter the sidebar by folder or tag.
- **AC1:** Folder names are unique; a duplicate is rejected with a message.
- **AC2:** Clicking a tag filters notes across all folders.
- **Realized by:** `folders`/`tags`/`note_tags` tables, `NoteRepository`, sidebar in `base.html`.

### FR-8 — Export as Markdown
The system shall let a user export a single note as a `.md` file and a folder (or
all notes) as a `.zip`. Filenames are sanitized; locked notes are skipped in bulk
export.
- **AC1:** A single note downloads as valid Markdown.
- **AC2:** A title like `Q3 / Budget & Forecast` produces a safe filename.
- **AC3:** An export with nothing to write reports it instead of producing an empty zip.
- **Realized by:** `web/routes/export.py`.

## Non-Functional Requirements

### NFR-1 — Local-first / offline
All data persists on the user's device in a single SQLite file. The app requires
no network connection; even the live-preview script is served locally (no CDN).
- **AC:** A static scan of the source finds zero outbound network calls or CDN references, and the app runs fully with networking disabled.
- **Realized by:** stdlib `sqlite3`, locally-served `preview.js`, no remote calls anywhere in the codebase.

### NFR-2 — Graceful failure
Invalid input and storage failures are reported as distinct, clear errors rather
than crashes. Input errors (`ValueError`) and write failures (`StorageError`)
render as two visually different flash styles.
- **AC:** An empty-title submit flashes a validation warning, and a corrupt or unwritable database surfaces a distinct `StorageError` message — neither path crashes the app.
- **Realized by:** `StorageError` wrapping in `LocalStorage`; the two-branch error handling in `web/routes/notes.py`; failure-path tests. Behavior extended beyond the create flow — resolves Week 5.2 gap.

### NFR-3 — Testability by design
The layers (domain, storage, services, web) are separated so each is unit-testable
in isolation, and the import direction is enforced automatically.
- **AC:** `tests/test_architecture.py` fails the build on any cross-layer (upward) import, and each test runs against an isolated `tmp_path` database.
- **Realized by:** strict layering, `tests/test_architecture.py` fitness test, per-test `tmp_path` isolation.

## Security & Privacy Requirements (Local-First)

- **SEC-1 — Encryption at rest.** SecureNote bodies are encrypted with Fernet; keys live outside the database (env var or git-ignored key file), never hardcoded.
  - **AC:** A locked note's body is stored as ciphertext in the `.db` (`test_note_service::test_make_private_encrypts_and_locks`, `test_encryption`).
- **SEC-2 — Data never leaves the device.** With no network surface, the device itself is the trust boundary — the local-first replacement for the original Supabase RLS boundary (SPR-01).
  - **AC:** A static inspection finds no remote/network surface; the device is the only trust boundary (verified by inspection — see NFR-1).
- **SEC-3 — XSS prevention.** Rendered Markdown is sanitized server-side with a bleach allow-list; the live preview escapes input before rendering.
  - **AC:** A `<script>` payload in a note body is escaped/stripped in both the live preview and the rendered view (`test_web::test_xss_is_sanitized`).
- **SEC-4 — Append-only audit log.** Lock, unlock, and restore are recorded in an `audit_log` whose UPDATE/DELETE are rejected by database triggers — the local-first realization of SPR-03.
  - **AC:** A direct `UPDATE` or `DELETE` against `audit_log` is rejected by a DB trigger (`test_audit`).

See [security-notes.md](../security/security-notes.md) and
[threat-model.md](../security/threat-model.md).

## Deferred (future roadmap)
Carried from the cloud vision and intentionally **out of scope** for the
local-first product: multi-user accounts/auth (FR-04), sharing with permissions
(FR-05), and real-time collaboration (FR-06). The schema keeps a `user_id`
placeholder column so these can return without restructuring the data.
