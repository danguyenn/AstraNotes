# Requirements ↔ Design ↔ Code ↔ Tests Traceability Matrix

This updates the Week 5.2 matrix to the shipped local-first product. It adds the
**code** and **tests** columns (the Week 5.2 version stopped at design), and it
**resolves the three behavioral gaps** that matrix flagged.

## 1. Forward traceability (requirement → realization)

| Req | UML element | Code | Tests | Status |
|-----|-------------|------|-------|--------|
| **FR-1** Create note | `Note`, Create-Note use case + activity | `domain/note.py`, `NoteService.create_note`, `NoteRepository.save` | `test_domain`, `test_note_service::test_create_and_get`, `test_web::test_create_and_view` | ✅ Fully traced & realized |
| **FR-2** Edit note | `Note.update_content`, Edit use case + **new activity** | `NoteService.edit_note` | `test_note_service::test_edit_note`, `test_web::test_edit_flow` | ✅ Gap resolved (edit activity diagram added) |
| **FR-3** Delete (keep versions) | Delete use case + **new activity**, `NoteRepository`↔`VersionHistory` aggregation | `NoteRepository.delete` | `test_repository::test_delete_*`, `test_versions::test_versions_retained_after_delete` | ✅ Gap resolved (delete activity + retention modeled) |
| **FR-4** Full-text search | `SearchIndex`, Search use case + **new activity w/ edge cases** | `storage/search_index.py`, `NoteService.search_notes` | `test_search` (hit/empty/no-result/special-chars/locked) | ✅ Gap resolved (edge cases modeled & tested) |
| **FR-5** Private + encryption | `SecureNote`, `EncryptionService`, `UserSession`; Mark-Private + Unlock use cases | `domain/note.py`, `services/encryption_service.py`, `services/session.py` | `test_encryption`, `test_note_service::test_make_private_*`, `test_web::test_lock_then_requires_unlock` | ✅ Fully traced |
| **FR-6** Version history + restore | `VersionHistory`, Restore use case | `storage/version_history.py`, `NoteService.restore_version` | `test_versions` (snapshot/restore/reversible/retained) | ✅ Promoted from design-led → realized |
| **FR-7** Folders + tags | folders/tags/note_tags | `NoteRepository` folder/tag methods | `test_repository::test_tags_*`, `::test_folder_*`, `test_web::test_create_folder_and_duplicate` | ✅ Realized |
| **FR-8** Export Markdown | (new in realization) | `web/routes/export.py` | `test_web::test_export_single_markdown`, `::test_export_bulk_zip` | ✅ Realized |
| **NFR-1** Local-first/offline | Deployment diagram (single node) | stdlib `sqlite3`, local `preview.js` | (architectural — verified by inspection; no automated network-absence test) | ✅ Traced by inspection |
| **NFR-2** Graceful failure | Activity validation + **new storage-failure branches** | `StorageError` in `LocalStorage`; two-branch error UI in routes | `test_storage::test_corrupt_db_raises_storage_error`, `test_web::test_empty_title_flashes_warning` | ✅ Gap resolved (extended beyond create) |
| **NFR-3** Testability by design | Layered class diagram | strict layering | `test_architecture` (fitness test) | ✅ Realized & enforced |
| **SEC-1** Encryption at rest | EncryptionService ↔ key store | Fernet; key from env/keyfile | `test_note_service::test_make_private_encrypts_and_locks` | ✅ |
| **SEC-2** Device trust boundary | Deployment (no network) | no remote surface | (architectural) | ✅ (reframed from RLS) |
| **SEC-3** XSS prevention | — | `web/markdown_render.py` (bleach), `preview.js` (escape-first) | `test_web::test_xss_is_sanitized` | ✅ |
| **SEC-4** Append-only audit log | — | `storage/audit_log.py` + triggers | `test_audit` (update/delete rejected) | ✅ |

## 2. The three Week 5.2 gaps — resolution

| Gap (Week 5.2 status) | Resolution |
|-----------------------|------------|
| FR-2 *Partially Traced* — no edit activity diagram | Edit activity diagram added ([UML §4](../architecture/uml.md)); `edit_note` realized + tested |
| FR-3 *Weakly Traced* — no delete activity, cascade/retention not visualized | Delete activity diagram added ([UML §5](../architecture/uml.md)) showing version retention + index removal; tested |
| FR-4 *Partially Traced* — no search activity, edge cases unmodeled | Search activity diagram with empty/no-result branches ([UML §6](../architecture/uml.md)); edge cases tested |
| NFR-2 *Weakly Traced* — only create validation modeled | Storage-failure branches modeled in create/edit activities; `StorageError` path tested (corrupt-db) |
| `VersionHistory` *design-led, no requirement* | Promoted to **FR-6** (per the matrix's own recommendation); now requirement-led |

## 3. Reverse traceability (class → requirement)
Every major class now has a requirement that justifies it — closing the one-way
gap Week 5.2 found:
`Note`/`SecureNote`→FR-1/FR-5 · `NoteService`→FR-1..FR-7 · `EncryptionService`→FR-5 ·
`UserSession`→FR-5 · `NoteRepository`/`LocalStorage`→FR-1/NFR-1 ·
`VersionHistory`→**FR-6** · `SearchIndex`→FR-4 · `AuditLog`→SEC-4.

## 4. Cloud-vision → local-first crosswalk
Reconciles the two requirement-numbering schemes (Supabase IDs from Week 1–3.1 vs.
local-first IDs above).

| Original (Supabase) | Final (local-first) | Disposition |
|---------------------|---------------------|-------------|
| FR-01 Markdown CRUD | FR-1 + FR-2 + FR-3 | Realized |
| FR-02 Folders + tags | FR-7 | Realized |
| FR-03 Search (`tsvector`) | FR-4 (FTS5) | Realized; engine swapped |
| FR-04 Auth | — | Deferred → roadmap (`user_id` placeholder) |
| FR-05 Sharing | — | Deferred → roadmap |
| FR-06 Real-time collab | — | Deferred → roadmap |
| FR-07 Version history | FR-6 | Realized (promoted) |
| FR-08 Export | FR-8 | Realized |
| NFR-01 Performance | NFR-1 (local-first) | Reframed |
| NFR-02 Responsiveness | responsive CSS | Partially realized |
| NFR-03 Testability | NFR-3 | Realized |
| NFR-04 Accessibility | (semantic HTML/labels) | Partially realized |
| SPR-01 RLS boundary | SEC-2 device boundary | Reframed |
| SPR-02 TLS + at-rest | SEC-1 (at-rest); TLS via proxy on deploy | Realized at-rest |
| SPR-03 Append-only audit | SEC-4 | Realized intact |
