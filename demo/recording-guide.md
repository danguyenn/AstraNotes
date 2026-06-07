# AstraNotes — Recording Guide (record in one take)

A directive companion to [`demo-script.md`](demo-script.md). That file is the *story*;
this file is the *run sheet* — exact clicks, exact words, and what must be visible on
screen so every claim is backed by the live app. Every label and path below was checked
against the running app (seeded with `seed_data.py --reset`).

**Target: ~5:00.** Narration is written to ~150 words/minute; each beat shows a word
budget so the whole thing fits. Read at a calm, even pace — if you're rushing to hit a
word count, slow down and cut a sentence instead.

---

## Pre-flight checklist (do all of this *before* you hit record)

```powershell
# from the repo root, with the venv active
pip install -e ".[dev]"
python demo/seed_data.py --reset      # → "Seeded 7 notes (1 locked) across 3 folders"
astranotes                            # serves http://127.0.0.1:5000
```

- [ ] Browser open at **http://127.0.0.1:5000**, full-screen, **1080p or higher**.
- [ ] Browser **zoom 125–150%** so text is legible in the recording.
- [ ] A **second tab open on a terminal** (you'll run `pytest -q` on camera at the 2:35 beat).
- [ ] **Notifications off** (Focus Assist / Do Not Disturb). Close Slack/email/etc.
- [ ] Mic check: record 5 seconds, play it back, confirm levels.
- [ ] Confirm the dashboard shows the 7 seeded notes, including **🔒 API Keys (private)**.
- [ ] Decide the note you'll lock live in Beat 3 — use **"Encryption design"** (a normal note).

**Recording mechanics**
- Tool: **OBS Studio** (free) or Windows **Game Bar** (`Win+G`) → screen capture + mic.
- Enable **cursor highlight / click visualization** if your tool supports it.
- **Two-take strategy:** do one full rehearsal take (don't keep it), then one clean take.
  Don't chase perfection — a confident single pass beats a stitched-together edit.
- Keep the mouse **still while you talk**; move it only when the script says `[DO]`.

---

## Run sheet

Legend — **[DO]** = on-screen action · **[SAY]** = verbatim narration · **[MUST SEE]** =
what has to be visible so the claim is honest.

### Beat 1 · 0:00–0:30 · Scope & the pivot  *(~70 words)*
- **[DO]** Start on the **dashboard** (the notes list with the sidebar of folders).
- **[SAY]** "This is AstraNotes — a secure, local-first Markdown notes app. It's a small
  Flask server over a single SQLite file: no cloud, no accounts, fully offline. It started
  the quarter as a Next.js-plus-Supabase cloud app and **pivoted** to local-first. That
  pivot — and the human decisions behind it — is the core of what I'll show you."
- **[MUST SEE]** Sidebar folders **Work / Personal / Research**; several notes listed.

### Beat 2 · 0:30–1:15 · Create + live Markdown preview (FR-1)  *(~105 words)*
- **[DO]** Click **"+ New note"** (top of the list). In the title field type
  `Demo Note`. In the **left pane** ("Write Markdown here…") type a few lines, e.g.
  `# Hello` then `- **local-first** notes` — watch the **right pane** render live.
- **[DO]** Click **Save**.
- **[SAY]** "Creating a note gives a live Markdown preview — left is the source, right
  renders as I type. That renderer is served from the app itself, no CDN, so the app stays
  fully offline. It also escapes input before rendering, which is the first half of the
  cross-site-scripting story. I hit Save and the note's persisted to local SQLite."
- **[MUST SEE]** The right pane updating **as you type**; the saved note then appears in the list.

### Beat 3 · 1:15–2:00 · Secure notes: encryption at rest (FR-5)  *(~110 words)*
- **[DO]** Open the **"Encryption design"** note → click **"Lock (encrypt)"**.
- **[DO]** Go back to the dashboard — the note now shows **🔒 … Locked — unlock to view.**
- **[DO]** Click it; you hit the **unlock gate**. Click **"Unlock secure notes"** to open
  the session, then open the note — content is now readable.
- **[SAY]** "Marking a note private encrypts its body at rest with Fernet — AES. In the
  database the body is ciphertext, it's excluded from search, and it only reveals after I
  unlock the session. Lock, unlock, and restore are all written to an append-only audit log
  the database itself enforces with triggers."
- **[MUST SEE]** The **🔒** state on the dashboard; the **unlock gate** before reveal; the
  note readable **after** unlocking.
- **[OPTIONAL power move]** In the terminal: `sqlite3 instance/astranotes.db "select substr(content,1,40) from notes where title='Encryption design';"` to show ciphertext. *Skip if `sqlite3` isn't installed — don't burn time.*

### Beat 4 · 2:00–2:35 · Search + version history / restore (FR-4, FR-6)  *(~85 words)*
- **[DO]** Click **Search**, type `encryption` → ranked results with **snippets**.
- **[DO]** Open a note (e.g. "Architecture Cheat Sheet"), edit one line, **Save**, then click
  **History** → click **Restore** on the older version.
- **[SAY]** "Search is SQLite FTS5 — empty queries and odd characters are handled, and
  locked notes never appear. Every save snapshots the note, so I can open History and
  restore any version — and the restore is itself a new version, so it's reversible.
  Snapshots even survive deleting the note."
- **[MUST SEE]** Search snippets; the **History** list with multiple versions; content
  reverting after **Restore**.

### Beat 5 · 2:35–3:30 · Architecture, at a high level  *(~130 words)*
- **[DO]** Open **`docs/architecture/uml.md`** (the class diagram + an activity diagram).
  Briefly show the note view (`03-note-view.png` is the reference shot).
- **[DO]** Switch to the **terminal tab** and run **`pytest -q`**.
- **[SAY]** "Four layers — web, services, storage, domain — and imports only ever point
  down. The only module that touches SQLite is LocalStorage; validation lives in the domain
  constructor, so an invalid note can't exist. And this isn't just a convention — a fitness
  test parses the source and fails the build on any layer violation. Here's the suite:
  seventy-seven tests, all passing, eighty-nine percent coverage — measured, not claimed."
- **[MUST SEE]** The terminal showing **`77 passed`**. *(Verified: `77 passed`, 89% coverage.)*

### Beat 6 · 3:30–4:30 · AI across the SDLC + human oversight  *(~150 words)*
- **[DO]** Open **`docs/ai-usage/ai-usage-log.md`**, then
  **`docs/traceability/traceability-matrix.md`**; point at the resolved-gap rows.
- **[SAY]** "AI was used at every stage — requirements, scaffolding, docs — but always under
  review. Three concrete overrides. One: I moved validation out of the service into the
  domain, so nothing can build an invalid note. Two: I **rejected** AI's suggestion to hang
  version history off the Note class, because the design says versions must outlive their
  note. Three: when AI labeled the traceability matrix 'fully traced,' I **downgraded** the
  dishonest labels — there were no edit, delete, or search activity diagrams. This repo
  **resolves** exactly those gaps, and the matrix shows it."
- **[MUST SEE]** The accept/refine/reject entries in the AI-usage log; the resolved rows in
  the matrix.

### Beat 7 · 4:30–5:00 · Coherence & close  *(~75 words)*
- **[DO]** Scroll the traceability matrix to the **forward + reverse** mapping.
- **[SAY]** "Every requirement traces to code and a test; every major class traces back to a
  requirement — including version history, which I promoted from design-led to a real
  requirement. The pivot from cloud to local-first wasn't a failure to ship the cloud app —
  it was the decision to ship something coherent and defensible. That's AstraNotes. Thanks
  for watching."
- **[MUST SEE]** Both directions of traceability on screen.

---

## If something breaks mid-take
- **Server hiccups / page won't load:** stop, restart `astranotes`, and re-record the beat.
  Don't narrate over a broken screen.
- **A live action misbehaves:** cut to the matching reference screenshot in
  [`screenshots/`](screenshots/) as B-roll and keep narrating, then fix and continue.
- **Running long:** the first beat to trim is the optional `sqlite3` power move, then tighten
  Beat 6 to two overrides instead of three.

## After you record
1. Upload the video (YouTube **unlisted** or Google Drive **link-sharing on**). Confirm the
   link opens in a private/incognito window before you rely on it.
2. Paste the link into the README — replace the placeholder on
   **[`README.md` line 8](../README.md#L8)**: `> **Demo video:** <your link>`.
3. Commit/push that change (see the git steps in the project finalization notes), then submit
   **the repo link + the video link**.

## One-line cheat (if you truly have one shot)
Dashboard → **+ New note** (live preview) → **Lock (encrypt)** a note → **Unlock** + open it →
**Search** "encryption" → **History → Restore** → terminal **`pytest -q`** (77 passed) →
**ai-usage-log** + **traceability-matrix** → close on the pivot.
