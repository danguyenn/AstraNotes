# ADR-0004 — Validation lives in the domain constructor, not the service

- **Status:** Accepted
- **Date:** Week 6

## Context
Copilot's first scaffolding put the empty-title check inside
`NoteService.create_note`. With validation in the service, a different caller
could construct an invalid `Note` directly and bypass the rule.

## Decision
Enforce the title invariant in `Note.__post_init__` (and re-check in
`update_content`). The service does **not** re-validate. An invalid `Note` cannot
exist in the system regardless of who builds it — which matches the
responsibility split the class diagram already implies.

## Consequences
- The rule is enforced once, at the only place a `Note` is created.
- `NoteService` stays focused on orchestration.
- Directly unit-testable at the domain layer (`tests/test_domain.py`) with no
  storage or web involved.

## Note on a reconciled requirement
Week 3.1 (cloud era) proposed defaulting empty titles to "Untitled Note". The
realized decision is to **reject** them instead, consistent with the Week 5.2
activity diagram's validation-error loop. The divergence is recorded in the
[final requirements](../requirements/final-requirements.md#fr-1--create-a-note-with-markdown).

## AI involvement
This is a documented **override** of an AI suggestion — the kind the Working
Agreement's three-question check is designed to catch (does it fit the
architecture?). See the [AI-usage log](../ai-usage/ai-usage-log.md).
