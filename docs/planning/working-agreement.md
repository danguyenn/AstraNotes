# Working Agreement (Week 2.1)

How AstraNotes is managed as a solo, AI-native project. This agreement and the
[Definition of Done](definition-of-done.md) are the repo's governance layer; the
README cites them as the project's operating rules.

## Planning and tracking
- A lightweight backlog (Backlog / In Progress / Review / Done). Each task is
  scoped to finish in one working session.
- Pick 2–3 backlog items per week that match the current course milestone. No new
  work is pulled until the current items clear the Definition of Done.

## How AI is used in the workflow
- AI (primarily Claude, with GitHub Copilot for scaffolding) is a **drafting and
  reasoning partner**, not a source of truth.
- Every AI output that touches source code, requirements, or documentation passes
  through human review before it is committed or submitted.

## Documenting prompts, decisions, and revisions
- Any decision that shapes a feature boundary, data-model change, or security
  choice is recorded as an [ADR](../decisions/). Minor code-generation prompts
  do not need a full log.
- The accept / refine / reject trail for AI output is kept in the
  [AI-usage log](../ai-usage/ai-usage-log.md).

## Deciding whether AI output is acceptable (three-question check)
1. Can I explain what this does **without** re-reading the prompt?
2. Does it fit the existing architecture (layer boundaries, class names, patterns)?
3. Does it introduce a dependency, scope change, or assumption I did not ask for?

If any answer is "no," the output is revised or rejected.

## Preventing drift, duplication, and low-quality output
- **One feature at a time.** Short-lived feature branches, merged only after the DoD passes.
- Run the test suite (and the architecture fitness test) before every commit.
- When AI repeatedly suggests patterns that conflict with the codebase, stop and
  fix the prompt context rather than patching the output after the fact.

> **Reflection (from the original artifact).** This agreement was written after a
> real incident: AI-generated code that used a slightly different import path than
> the rest of the codebase caused a build error. The three-question acceptance
> check exists to catch exactly that — architectural-fit drift — before it lands.
> The same instinct is now enforced mechanically by the layering fitness test
> (`tests/test_architecture.py`).
