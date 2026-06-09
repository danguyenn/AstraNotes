# Rendered Diagram Gallery

Every diagram in the AstraNotes docs, rendered to standalone images. The **source
of truth is the Mermaid in the Markdown files** (GitHub renders those inline); these
PNG/SVG exports make the same diagrams viewable offline, in a PDF, or as a supporting
attachment.

Regenerate after editing any diagram:

```bash
python tools/render_diagrams.py     # needs Node + npx (uses @mermaid-js/mermaid-cli)
```

PNG is embedded below; a vector **`.svg`** of the same name sits beside each one.

---

## Architecture & UML — source: [`../uml.md`](../uml.md)

### Class diagram
![Class diagram](01-1-class-diagram.png)

### Use-case diagram
![Use-case diagram](02-2-use-case-diagram.png)

### Activity — Create note (FR-1, with the NFR-2 failure branch)
![Create-note activity diagram](03-3-activity-diagram-create-note-fr-1-with-nfr-2-failure-branch.png)

### Activity — Edit note (FR-2)
![Edit-note activity diagram](04-4-activity-diagram-edit-note-fr-2-resolves-week-5-2-gap.png)

### Activity — Delete note, retaining history (FR-3)
![Delete-note activity diagram](05-5-activity-diagram-delete-note-fr-3-resolves-week-5-2-gap.png)

### Activity — Search with edge cases (FR-4)
![Search activity diagram](06-6-activity-diagram-search-fr-4-with-edge-cases-resolves-week-5-2-gap.png)

### Deployment (local-first, single node)
![Deployment diagram](07-7-deployment-diagram-local-first.png)

### Sequence — Lock a note (FR-5)
![Lock-note sequence diagram](08-8-sequence-diagram-lock-a-note-fr-5.png)

## Architecture overview — source: [`../overview.md`](../overview.md)

### Layers & the dependency rule
![Layered architecture](09-layers-and-the-dependency-rule.png)

### Data model (entity-relationship)
![Data-model ER diagram](10-data-model.png)

## Security — source: [`../../security/threat-model.md`](../../security/threat-model.md)

### Trust boundary
![Trust-boundary diagram](11-trust-boundary.png)

## Planning — source: [`../../planning/waterfall-gantt.md`](../../planning/waterfall-gantt.md)

### Waterfall baseline schedule
![Waterfall Gantt chart](12-waterfall-baseline-schedule-lab-1-1.png)
