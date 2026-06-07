# Definition of Done (Week 2.1)

A task, feature, or artifact in AstraNotes is **done** only when every one of
these is true. This checklist is the project's stopping rule — a concrete bar
instead of a vague sense of "finished."

1. **Traceable to an objective.** It maps to a backlog item, a requirement, or a
   documented goal. If it can't be pointed at a specific objective, it isn't done.
2. **Explainable by me.** I can walk through the logic without re-reading the
   original AI prompt. If I need the prompt to explain it, I don't understand it
   well enough to ship it.
3. **Checked for quality and realism.** Code passes its checks and behaves as
   expected locally; docs are internally consistent with no hallucinated
   references or unfilled placeholders.
4. **Tested or validated.** Code changes have at least a passing test or a real
   smoke test of the affected behavior; non-code artifacts get a self-review for
   consistency with the current architecture.
5. **Security and privacy considered.** Anything touching user data is reviewed
   against the trust model; no keys, secrets, or PII are hardcoded or committed.
   If there's no security surface, that is confirmed consciously, not ignored.
6. **Ready to build on.** Organized, on the right branch, and documented well
   enough to pick up a week later without a lengthy re-explanation.
7. **Worth defending.** I'd present it in a review and explain why it deserves to
   move forward, without needing caveats or apologies.

## How this DoD is met in the shipped repo
- **Traceable:** every requirement maps to code and tests in the [traceability matrix](../traceability/traceability-matrix.md).
- **Tested:** `pytest` suite (see [test-report.md](../testing/test-report.md)) with a real, cited pass count.
- **Security:** keys are env/keyfile-sourced and `.gitignore`'d; SecureNotes are encrypted at rest; the audit log is append-only. See [security-notes.md](../security/security-notes.md).
- **Quality gate:** the architecture fitness test fails the build on any layer-boundary violation.
