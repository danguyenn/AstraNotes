# AI-Usage Log — Accept / Refine / Reject Across the SDLC

AstraNotes was built AI-natively under human oversight. AI was a drafting and
reasoning partner; **every output that touched code, requirements, or docs passed
through human review before it was accepted** (the
[Working Agreement](../planning/working-agreement.md) three-question check). This
log is the accept/refine/reject trail across each SDLC stage, drawn from the
quarter's artifacts and the final build.

## Summary table

| Stage | AI did | Accepted | Refined | Rejected |
|-------|--------|----------|---------|----------|
| Requirements | Drafted FR/NFR/SEC; pressure-tested as a reviewer | Measurable, testable requirements | Vague ACs → demo-verifiable; security made explicit | E2E encryption, full offline-first, enterprise SSO (scope) |
| Architecture | Compared stacks; reasoned components/failure/privacy | Supabase decision + failure principle | — | Shallow single-table CRUD (weak prompt) |
| Design (UML) | Drafted matrix structure + first-pass mappings | Matrix layout, consistent wording | Status labels downgraded to be honest | "Fully Traced" labels that hid real gaps |
| Implementation | Scaffolded pyproject, schema, Flask factory, tests | Idiomatic boilerplate | Moved validation to the domain; isolated SQLite | `versions` attribute on `Note` (wrong aggregation) |
| Testing | Critiqued tests; suggested real-DB approach | Real-DB + deny-path testing | Added body assertions; kept tests requirement-tied | Parametrized cases for non-existent roles (test theater) |
| Final build | Generated the local-first app + docs from artifacts | Coherent layered implementation | Empty-title reconciliation; ADR renumbering | — |

## By stage

### 1. Requirements (Week 1.2, refined Week 3.1)
- **Accept:** AI drafted the initial 14 requirements from a role+context+constraint prompt; the measurable, testable ones were kept.
- **Refine:** First-pass ACs were vague ("the app should be fast", "works as expected"). They were rewritten with thresholds and made demo-verifiable. Using AI as a *reviewer* ("what does this not say? what would two engineers disagree on? what happens on failure?") surfaced the FR-06 concurrent-edit conflict, the FR-04 user-enumeration leak, and the missing HSTS in SEC-02.
- **Reject:** AI pushed end-to-end encryption, full offline-first architecture, and enterprise SSO — all reasonable but unrealistic for a solo 10-week project. Left out to keep scope honest.

### 2. Architecture (Lab 1.2 ADL)
- **Accept:** A strong, role-framed prompt produced the component split, the RLS trust boundary, and — most importantly — the **primary-vs-secondary write failure principle** that still governs `NoteRepository.save` ([ADR-0006](../decisions/ADR-0006-secondary-write-isolation.md)).
- **Reject:** A weak prompt ("design a simple storage system") produced a shallow single-table CRUD with no ownership, failure handling, or privacy. The contrast itself was the lesson: prompt quality determines design quality.

### 3. Design / Traceability (Week 4.2 UML, Week 5.2 matrix)
- **Accept:** AI drafted the matrix structure and normalized requirement wording.
- **Refine / Reject:** AI's first pass labeled FR-2/3/4 "Fully Traced" because a use case and structural support existed. These were **downgraded** by hand — the behavioral coverage was genuinely thin (no edit/delete/search activity diagrams). AI also missed the reverse-traceability finding that `VersionHistory` was design-led; that was caught by a human checking class→requirement. *"AI was faster at producing a credible-looking matrix; slower at producing an honest one."* The final repo **resolves** all of those gaps (see [traceability matrix](../traceability/traceability-matrix.md)).

### 4. Implementation (Week 6 realization)
- **Accept:** Copilot scaffolded the `pyproject` layout, the SQLite schema string, the Flask factory, and the first test file — pattern-heavy code where AI is genuinely faster.
- **Refine:** Two boundary fixes were made over AI's first pass — validation moved onto `Note.__post_init__` ([ADR-0004](../decisions/ADR-0004-domain-owned-invariants.md)), and SQLite was confined to `LocalStorage` returning dicts ([ADR-0003](../decisions/ADR-0003-isolate-sqlite-in-localstorage.md)).
- **Reject:** Copilot offered a `versions: list[Version]` attribute on `Note`. Rejected — the class diagram aggregates `VersionHistory` under `NoteRepository`, and versions must outlive their note. Accepting it would have silently changed a committed architectural decision.

### 5. Testing (Week 9 Test Improvement Log)
- **Accept:** AI flagged that patching the function under test (`can_view`) was test theater and suggested seeding a real database and testing the deny path.
- **Refine:** AI's version only checked status codes; a body assertion was added so the test proves content actually loads.
- **Reject:** AI suggested many parametrized cases for user roles AstraNotes doesn't have — tests with no requirement behind them. Kept small and requirement-tied. These principles (real temp-SQLite, allow+deny paths, assert on output, every test maps to a requirement) are exactly how the shipped suite is written.

### 6. Final realization (this submission)
- **Accept:** AI generated the local-first Flask/SQLite application and the SDLC document set **from the quarter's artifacts**, preserving the class names so the UML and traceability stay coherent.
- **Refine:** Two human reconciliations were applied and documented — the empty-title behavior follows the realized **reject** rule (not the Week 3.1 "Untitled" default), and the ADR numbering was corrected so code/doc cross-references resolve.
- **Verify:** Test claims are not inherited — `pytest` was run and the actual count (77 passed, 89% coverage) is cited in the [test report](../testing/test-report.md), per the no-unverified-claims rule.

## The throughline
The defensible story is not "AI wrote it." It is **the pivot and the overrides**:
the human decisions to descope from cloud to local-first, to move validation into
the domain, to keep version history out of `Note`, to downgrade dishonest
traceability labels, and to reject test theater. AI accelerated the drafting; human
oversight decided what shipped.
