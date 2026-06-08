# AstraNotes — Recording Guide

This is the run sheet for the script in [`demo-script.md`](demo-script.md): the exact
clicks, the words to say, and what needs to be on screen so every claim is backed by the
live app. I checked all the labels and paths against the running app after seeding it with
`seed_data.py --reset`.

Aim for about five minutes. Read at a calm, even pace. If you catch yourself rushing to
hit a time, slow down and cut a sentence instead.

---

## Before you hit record

From the repo root, with the venv active:

```powershell
pip install -e ".[dev]"
python demo/seed_data.py --reset      # → "Seeded 7 notes (1 locked) across 3 folders"
astranotes                            # serves http://127.0.0.1:5000
```

Then run through this:

- [ ] Browser open at **http://127.0.0.1:5000**, full-screen, 1080p or higher.
- [ ] Browser zoom 125–150% so the text reads on the recording.
- [ ] A second tab on a terminal — you'll run `pytest -q` on camera around the 2:35 mark.
- [ ] Notifications off (Focus Assist / Do Not Disturb). Close Slack, email, the rest.
- [ ] Mic check: record five seconds, play it back, confirm the levels.
- [ ] Confirm the dashboard shows all 7 seeded notes, including 🔒 API Keys (private).
- [ ] Pick the note you'll lock live in Beat 3. Use "Encryption design" — it's a normal note.

A few notes on the mechanics:

- Capture with OBS Studio (free) or the Windows Game Bar (`Win+G`) for screen plus mic.
- Turn on cursor highlight / click visualization if your tool has it.
- Do one full rehearsal take to warm up, throw it away, then record one clean take. A
  confident single pass beats a stitched-together edit, so don't chase perfection.
- Keep the mouse still while you talk. Only move it when you're doing the action.

---

## The run

For each beat: what to do, a line to say (paraphrase freely), and what has to be visible
so the claim stays honest.

### Beat 1 — Scope & the pivot (0:00–0:30)

Start on the dashboard, the notes list with the folder sidebar.

Say something like: "This is AstraNotes, a secure, local-first Markdown notes app. It's a
small Flask server over a single SQLite file: no cloud, no accounts, fully offline. It
started the quarter as a Next.js-plus-Supabase cloud app and pivoted to local-first. That
pivot, and the human decisions behind it, is the core of what I'll show you."

Make sure viewers see the Work / Personal / Research folders in the sidebar and several
notes listed.

### Beat 2 — Create + live Markdown preview (0:30–1:15, FR-1)

Click **+ New note** at the top of the list. Type `Demo Note` in the title field, then
type a few lines in the left pane ("Write Markdown here…"), like `# Hello` and
`- **local-first** notes`, and watch the right pane render as you go. Click **Save**.

Say something like: "Creating a note gives you a live Markdown preview. The left pane is
the source, the right renders as I type. That renderer is served from the app itself, no
CDN, so the app stays fully offline. It also escapes input before rendering, which is the
first half of the cross-site-scripting story. I hit Save and the note's persisted to local
SQLite."

Make sure viewers see the right pane updating as you type, then the saved note appearing in
the list.

### Beat 3 — Secure notes: encryption at rest (1:15–2:00, FR-5)

Open the **Encryption design** note and click **Lock (encrypt)**. Back on the dashboard it
now reads 🔒 "Locked — unlock to view." Click it and you'll hit the unlock gate; pick
**Unlock secure notes** to open the session, then open the note so the body is readable.

Say something like: "Marking a note private encrypts its body at rest with Fernet (AES).
In the database the body is ciphertext, it's left out of search, and it only reveals once I
unlock the session. Lock, unlock, and restore are all written to an append-only audit log
the database enforces with triggers."

Make sure viewers see the 🔒 on the dashboard, the unlock gate before anything reveals, and
the note readable after unlocking. (The append-only audit trail itself lives on the
**Settings** page — `07-settings-audit.png` is the reference shot if you want to flash it
while mentioning the audit log.)

Optional, if `sqlite3` is installed: run
`sqlite3 instance/astranotes.db "select substr(content,1,40) from notes where title='Encryption design';"`
to show the raw ciphertext. Skip it if the tool isn't there — not worth the fumble.

### Beat 4 — Search + version history / restore (2:00–2:35, FR-4, FR-6)

Click **Search** and type `encryption` for ranked results with snippets. Then open a note
(say "Architecture Cheat Sheet"), edit one line, **Save**, click **History**, and
**Restore** the older version.

Say something like: "Search is SQLite FTS5. Empty queries and odd characters are handled,
and locked notes never show up. Every save snapshots the note, so I can open History and
restore any version, and the restore is itself a new version, so it's reversible. The
snapshots even survive deleting the note."

Make sure viewers see the search snippets, the History list with multiple versions, and the
content reverting after Restore.

### Beat 5 — Architecture, at a high level (2:35–3:30)

Open `docs/architecture/uml.md` (the class diagram plus an activity diagram), and briefly
show the note view — `03-note-view.png` is the reference shot. Then switch to the terminal
tab and run `pytest -q`.

Say something like: "Four layers — web, services, storage, domain — and imports only ever
point down. The only module that touches SQLite is LocalStorage, and validation lives in
the domain constructor, so an invalid note can't exist. This isn't just a convention: a
fitness test parses the source and fails the build on any layer violation. Here's the
suite: seventy-seven tests, all passing, eighty-nine percent coverage."

Make sure viewers see the terminal showing `77 passed`. (Verified: `77 passed`, 89% coverage.)

### Beat 6 — AI across the SDLC + human oversight (3:30–4:30)

Open `docs/ai-usage/ai-usage-log.md`, then `docs/traceability/traceability-matrix.md`, and
point at the resolved-gap rows.

Say something like: "AI was used at every stage — requirements, scaffolding, docs — but
always under review. Three concrete overrides. One: I moved validation out of the service
into the domain, so nothing can build an invalid note. Two: I rejected AI's suggestion to
hang version history off the Note class, because the design says versions must outlive their
note. Three: when AI labeled the traceability matrix 'fully traced,' I downgraded the
dishonest labels — there were no edit, delete, or search activity diagrams. This repo
resolves exactly those gaps, and the matrix shows it."

Make sure viewers see the accept / refine / reject entries in the AI-usage log and the
resolved rows in the matrix.

### Beat 7 — Coherence & close (4:30–5:00)

Scroll the traceability matrix to the forward + reverse mapping.

Say something like: "Every requirement traces to code and a test, and every major class
traces back to a requirement — including version history, which I promoted from design-led
to a real requirement. The pivot from cloud to local-first wasn't a failure to ship the
cloud app. It was the decision to ship something coherent and defensible. That's AstraNotes.
Thanks for watching."

Make sure viewers see both directions of traceability on screen.

---

## If something breaks mid-take

- Server hiccups or the page won't load: stop, restart `astranotes`, and re-record the
  beat. Don't narrate over a broken screen.
- A live action misbehaves: cut to the matching reference screenshot in
  [`screenshots/`](screenshots/) as B-roll, keep narrating, then fix it and continue.
- Running long: the first thing to trim is the optional `sqlite3` move in Beat 3, then
  tighten Beat 6 to two overrides instead of three.

## After you record

1. Upload the video (YouTube unlisted, or Google Drive with link-sharing on). Open the link
   in a private window first to confirm it works before you rely on it.
2. Paste the link into the README, replacing the placeholder on
   [`README.md` line 8](../README.md#L8): `> **Demo video:** <your link>`.
3. Commit and push that change (see the git steps in the project finalization notes), then
   submit the repo link and the video link.

## One-shot cheat (if you truly have one take)

Dashboard → **+ New note** (live preview) → **Lock (encrypt)** a note → **Unlock** and open
it → **Search** "encryption" → **History → Restore** → terminal `pytest -q` (77 passed) →
ai-usage-log + traceability-matrix → close on the pivot.
