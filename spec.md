# Spec — AstraNotes UI ("Cream & Sage" light theme)

## Goal
Replace the original "AI-generated"-looking dark theme — the ✦ sparkle brand, periwinkle
gradient buttons (`--accent: #6c8cff`), low-contrast muted text, and a flat, character-less
type treatment — with a **crafted "cream & sage"** light look: a warm paper-cream base, a
single confident **deep forest-green** accent, high-contrast green-ink text, a real
typographic hierarchy, flatter/quieter cards, and considered spacing and micro-interactions.
Scope is the **full treatment** (skin rewrite **plus** layout/component/hierarchy polish),
using a **polished system-font stack only** (no downloaded/bundled fonts). The redesign is
purely visual: every route, flow, and the 77 passing tests must behave exactly as before.

## Non-Goals
- **No behavior, route, schema, or data changes.** UI/markup/CSS only.
- **No external assets / no CDN.** Must stay fully offline and satisfy the existing CSP
  (`default-src 'self'`, `style-src 'self'`): all CSS lives in `static/style.css` (no inline
  `<style>` or `style=` attributes), no web-font fetches, no remote images. A brand mark, if
  graphical, is **inline `<svg>`** (markup, CSP-safe), not an external file.
- **No new fonts bundled** (per the typography choice) — system stack only.
- **No dark theme / theme toggle** this pass (could be added later via
  `prefers-color-scheme`; out of scope now). The shipped product is light-only.
- **No renaming of test-observable hooks** (see Contract) and no removal of the inline
  `onsubmit` delete confirm (it's the reason the CSP keeps `script-src 'unsafe-inline'`).
- Not touching auth/multi-user/etc. (still out of project scope).

## Contract (design tokens + invariants)
**Files changed:** `src/astranotes/web/static/style.css` (substantial rewrite),
`src/astranotes/web/templates/base.html` (brand mark + minor structure), and light polish
across the page templates: `index.html`, `editor.html`, `view.html`, `history.html`,
`search.html`, `settings.html`, `profile.html`, `unlock.html`, `error.html`. `preview.js`
unchanged (it only sets `innerHTML` of the preview pane).

**Design tokens (CSS `:root`):**
- Surfaces: `bg #f3eee0` · `bg-elev #fbf7ee` · `surface #fdfbf5` · `surface-2 #ece5d4` ·
  `border #e2dbc6` · `border-strong #cdc4a8` (warm paper cream; cards a shade lighter)
- Text: `text #232a20` (deep green-ink, ≈AA on bg) · `muted #5f6753` (soft olive-grey) ·
  `faint #787e6b`
- Accent: `accent #2f6e3c` (deep forest green) · `accent-hover #25592f` · `accent-ink #f4f7ee`
  (light ink on green for AA)
- Keep semantic flash colors (success/warn/danger) but retune for the light palette.
- Radius: `10px` cards / `7px` controls; a subtle elevation/border system instead of flat
  sameness. `color-scheme: light`.
- Type scale: system grotesk for UI, **`ui-monospace`** for meta/labels/code; deliberate
  sizes/weights/letter-spacing for h1/section-label/title/body/meta.

**Invariants that protect the tests** (`tests/test_web.py`):
- Preserve class names asserted or relied on: `flash-success` / `flash-warning` /
  `flash-danger`, and the structural classes used by flows. (Test asserts `b"flash-warning"`.)
- Preserve all visible copy the tests check: page renders for `/`, note titles (e.g.
  "Meeting Notes"), "No notes match", "Type a keyword", "already exists", export
  `Content-Type` (`text/markdown`, `application/zip`), and the XSS-sanitization behavior.
- Preserve the security headers test (don't alter `after_request`).

**Brand:** replace `✦ AstraNotes` with a crafted wordmark — a small inline-SVG notebook
monogram/mark in the forest-green accent + the name in a tuned weight/tracking. No emoji,
no sparkle.

## Edge Cases
- Long note titles and tag lists wrap cleanly in cards and the sidebar.
- Empty states (no notes / no search results / empty history) look intentional, not default.
- Locked-note card ("🔒 … Locked — unlock to view") stays legible and visually distinct.
- Rendered Markdown: headings, lists, inline code, fenced code blocks, tables, links, and
  blockquotes are all styled and readable in the preview and the note view.
- Focus-visible states for keyboard nav (accessibility / NFR-4) and AA-contrast text.
- Responsive `@media (max-width: 860px)`: sidebar + side-by-side editor collapse correctly.
- Flash messages legible against new surfaces.

## Milestones (each independently checkable)
1. **Tokens + foundation** — new `:root` palette, base typography, links, headings, spacing,
   focus styles in `style.css`. App still renders.
2. **Chrome** — top bar, search field, sidebar, nav, and the new inline-SVG brand mark.
3. **Notes surface** — note grid + cards + tag pills + page head + empty states.
4. **Editor & reading** — editor panes/inputs, rendered-Markdown styles, history, search,
   settings, profile, unlock, error pages.
5. **Polish + verify** — hover/focus micro-interactions, responsive pass; run
   `ruff`/`mypy`/`pytest` (expect 77 green), smoke-test the running app in a browser, and
   re-capture `demo/screenshots/*` via `demo/capture_screenshots.py` so demo assets match
   the light look.

## Open Questions
_(none — realized in the shipped build.)_
