# Test Plan

## Strategy
Tests follow the layered architecture and the principles from the Week 9 Test
Improvement Log: **run the real rule against a real (in-memory/temp) database, not
a mock; test both the success and failure paths; assert on output, not just status
codes; and tie every test to a requirement.** Over-mocking is avoided — the
storage and the rules under test stay real because they *are* the risk.

Each test gets an isolated SQLite file via the `tmp_path` fixture (NFR-3), so tests
never share state.

## Levels
- **Unit** — domain invariants, encryption round-trips, storage dict-isolation, repository round-trips, search, versions, audit.
- **Integration** — the full Flask stack via the test client (`test_web.py`): real routes, services, storage, templates.
- **Architecture (fitness)** — `test_architecture.py` parses the source and fails the build on any layer-boundary violation.

## Coverage by requirement
| Requirement | Test module(s) |
|-------------|----------------|
| FR-1 create | `test_domain`, `test_note_service`, `test_web` |
| FR-2 edit | `test_note_service`, `test_web` |
| FR-3 delete (+retention) | `test_repository`, `test_versions`, `test_web` |
| FR-4 search (+edge cases) | `test_search` |
| FR-5 encryption/privacy | `test_encryption`, `test_note_service`, `test_web` |
| FR-6 versions/restore | `test_versions` |
| FR-7 folders/tags | `test_repository`, `test_web` |
| FR-8 export | `test_web` |
| NFR-1 local-first/offline | (architectural — verified by inspection; no automated network-absence test) |
| NFR-2 graceful failure | `test_storage` (corrupt-db), `test_config` (fail-fast startup), `test_web` (validation) |
| NFR-3 testability/layering | `test_architecture` |
| SEC-1 encryption at rest | `test_note_service`, `test_encryption` |
| SEC-2 device trust boundary | (architectural — verified by inspection) |
| SEC-3 XSS | `test_web::test_xss_is_sanitized` |
| SEC-4 audit append-only | `test_audit` |

## Key adversarial / failure cases (not just happy path)
- Corrupt the SQLite file mid-run and assert the next read raises `StorageError`.
- Assert SecureNote content is **ciphertext at rest** and **absent from search**.
- Assert the `audit_log` rejects UPDATE and DELETE at the DB level.
- Assert a `<script>` in a note body does not survive rendering.
- Assert a wrong key cannot decrypt another key's ciphertext.

## How to run
```bash
pip install -e ".[dev]"
pytest --cov=astranotes --cov-report=term-missing
```

## Known limitation (honest coverage gap)
Coverage measures lines executed, not states proven. The same lesson the Week 9
log raised about enrollment transitions applies here: e.g. the test suite verifies
locking/unlocking but does not exhaustively fuzz every session-state transition.
Uncovered lines are mostly defensive route branches and the server entry point.
