# AstraNotes — 5-Minute Demo Script

A shot-by-shot script for the recorded defense video. **Demo the running app, not
slides.** Reference screenshots are in [`screenshots/`](screenshots/).

## Before you record
```bash
pip install -e ".[dev]"
python demo/seed_data.py --reset     # 7 notes (1 locked) across 3 folders
astranotes                           # http://127.0.0.1:5000
```
Open `http://127.0.0.1:5000` full-screen. Have one editor tab and one terminal tab
ready (for the architecture + tests beat).

---

## 0:00–0:30 · Scope & the pivot (the "what" and the "why")
**Show:** the dashboard (`01-dashboard.png`).
**Say:** "This is AstraNotes — a secure, local-first Markdown notes app. It runs as
a small Flask server on a single SQLite file: no cloud, no accounts, fully offline.
It started the quarter as a Next.js + Supabase cloud app and **pivoted** to
local-first — and that pivot, with the human decisions behind it, is the core of the
story I'll show."

## 0:30–1:15 · Workflow 1 — Create with live Markdown preview (FR-1)
**Do:** Click **+ New note** → type a title → type Markdown in the left pane.
**Show:** the preview updating live (`02-editor-live-preview.png`). Save.
**Say:** "Create and edit render a live preview. The preview is a tiny renderer
served from the app itself — no CDN — so the app stays offline. It also escapes
input before rendering, which is the first half of the XSS story."

## 1:15–2:00 · Workflow 2 — Secure notes: encryption at rest (FR-5)
**Do:** Open a normal note → **Lock (encrypt)**. Go back to the dashboard; the note
now shows 🔒 "Locked — unlock to view." Try to open it → redirected to **Unlock**
(`06-unlock.png`). Unlock the session → open it.
**Say:** "Marking a note private encrypts its body at rest with Fernet. In the
database it's ciphertext, it's excluded from search, and it only reveals after I
unlock the session." *(Optional power move: in the terminal, `sqlite3` the
`notes` table to show the ciphertext.)*

## 2:00–2:35 · Workflow 3 — Search + version history/restore (FR-4, FR-6)
**Do:** Search "encryption" → ranked results with snippets (`05-search.png`). Open a
note, hit **History** (`04-history.png`), **Restore** an older version.
**Say:** "Search is SQLite FTS5 — empty and special-character queries are handled,
locked notes never appear. Every save snapshots; I can restore any version, and the
restore is itself reversible. Snapshots even survive deleting the note."

## 2:35–3:30 · Architecture, at a high level
**Show:** `docs/architecture/uml.md` (class + a couple activity diagrams), and the
note view (`03-note-view.png`).
**Say:** "Four layers — web → services → storage → domain — and imports only point
down. The only module that touches SQLite is `LocalStorage`; validation lives in the
domain constructor so an invalid note can't exist. This isn't just a convention — a
**fitness test** parses the source and fails the build on any layer violation."
**Do:** In the terminal, run `pytest -q` and show **77 passed**.

## 3:30–4:30 · AI across the SDLC + human oversight (accept / refine / reject)
**Show:** `docs/ai-usage/ai-usage-log.md` and `docs/traceability/traceability-matrix.md`.
**Say:** "AI was used at every stage — but under review. Three concrete overrides:
(1) I moved validation out of the service into the domain so nothing can build an
invalid note. (2) I **rejected** AI's suggestion to hang version history off `Note`,
because the design says versions outlive their note. (3) When AI labeled the
traceability matrix 'fully traced,' I **downgraded** the dishonest labels — there
were no edit/delete/search activity diagrams. This repo **resolves** those exact
gaps." Point at the resolved rows.

## 4:30–5:00 · Coherence & close
**Show:** the traceability matrix forward+reverse mapping and the test report.
**Say:** "Every requirement traces to code and a test; every major class traces back
to a requirement — including version history, which I promoted from 'design-led' to
a real requirement. The pivot from cloud to local-first wasn't a failure to deliver
the cloud app — it was the engineering decision to ship something coherent and
defensible. That's AstraNotes."

---

## Rubric coverage checklist
- [x] Chosen scope stated (local-first Markdown notes; cloud → local pivot)
- [x] Live demo of the actual app
- [x] ≥ 2–3 workflows (create+preview, secure/encrypt, search+restore, export)
- [x] Architecture/implementation direction at a high level (layers + fitness test)
- [x] How AI was used across the SDLC
- [x] What was accepted / refined / rejected under human oversight
- [x] Evidence: 77 passing tests, resolved traceability gaps
