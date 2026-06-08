# Threat Model

A lightweight threat model for the **local-first, single-user** AstraNotes. The
trust boundary is the user's device; there is no network surface in the default
configuration.

## Assets
- Note content (especially SecureNote bodies).
- The encryption key.
- The integrity of the audit trail.

## Trust boundary
```
[ User's device ]  ── trusted ──  AstraNotes process + SQLite + key store
        |
        └── (no network surface by default)
```

## STRIDE summary

| Threat | Scenario | Mitigation | Residual risk |
|--------|----------|------------|---------------|
| **Spoofing** | Another local user opens the app | Optional passphrase gate for SecureNotes; OS account separation | Device owner is trusted by design |
| **Tampering** | Someone edits the DB to rewrite history | Audit log is append-only via DB triggers; primary writes are validated | A full DB replace is possible (it's the user's file) — out of scope for single-user |
| **Repudiation** | "I never locked that note" | `audit_log` records lock/unlock/restore with timestamps | Single-user, so attribution is to the one account |
| **Information disclosure** | DB file copied off the device | SecureNote bodies are ciphertext at rest; key stored separately | Non-secure notes are plaintext by design (user choice to lock) |
| **Denial of service** | Corrupt DB file | Errors are caught and surfaced as `StorageError`, not a crash (NFR-2) | User must restore from backup |
| **Elevation of privilege** | Web input escalates to code/markup execution | bleach allow-list on render; escape-first preview; parameterized SQL only | — |

## Key handling
- Key sources: env var → git-ignored key file → generated dev key. Never in the DB, never hardcoded.
- Losing the key makes locked notes unrecoverable; the key must be backed up separately from the `.db`.

## Injection surfaces
- **SQL:** every query uses parameter binding; no string interpolation of user input.
- **FTS5:** user queries are tokenized to a safe `MATCH` expression, so special characters can't break the parser or inject operators.
- **HTML/Markdown:** server-side bleach allow-list; client preview escapes before rendering.

## If the app is exposed to a network (non-default)
Running behind a reverse proxy reintroduces network threats. Mitigations: TLS +
HSTS at the proxy (cloud SPR-02 equivalent), and — before any real multi-user use —
restore an authentication + per-user authorization boundary (the deferred FR-04 /
SPR-01), for which the schema's `user_id` placeholder is reserved.
