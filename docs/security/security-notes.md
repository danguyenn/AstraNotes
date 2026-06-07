# Security Notes

AstraNotes is local-first and single-user, so the **device is the trust boundary**.
This reframes the original cloud security model (Supabase RLS, TLS, audit logging)
for an on-device app. See the [threat model](threat-model.md) for the structured
analysis.

## Controls in the shipped product

| Control | Requirement | Implementation |
|---------|-------------|----------------|
| **Encryption at rest** | SEC-1 / FR-5 | SecureNote bodies are encrypted with **Fernet** (AES-128-CBC + HMAC) via `EncryptionService`. The DB stores ciphertext; plaintext exists only in memory after an unlocked-session decrypt. |
| **Key isolation** | SEC-1 | The key is read from `ASTRANOTES_ENCRYPTION_KEY` or a git-ignored `instance/encryption.key`. It is **never** stored in the database and **never** hardcoded. |
| **No secrets in the repo** | DoD | `.gitignore` excludes `*.db`, `*.key`, `encryption.key`, `flask_secret`, `instance/`, and `.env`. Only `.env.example` (placeholders) is tracked. |
| **XSS prevention** | SEC-3 | Markdown is rendered server-side and sanitized with a **bleach allow-list** (`markdown_render.py`); the live preview escapes input **before** rendering (`preview.js`). |
| **Tamper-evident audit log** | SEC-4 | `audit_log` records lock/unlock/restore; DB triggers `RAISE(ABORT)` on UPDATE/DELETE, so the trail is append-only even against direct DB writes. |
| **Passphrase gate (optional)** | FR-5 | `ASTRANOTES_PASSPHRASE_SHA256` gates session unlock; only the SHA-256 hash is stored, compared with `secrets.compare_digest`. |
| **Input validation** | NFR-2 | Domain invariants reject invalid notes; `StorageError`/`ValueError` produce distinct, non-crashing error UI. |
| **HTTP security headers** | SEC-3 | An `after_request` hook sets `Content-Security-Policy` (same-origin `default-src 'self'`, `object-src 'none'`, `frame-ancestors 'none'`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`. |
| **Fail-fast config validation** | NFR-2 | `load_config` rejects an ill-formed `ASTRANOTES_ENCRYPTION_KEY` or an uncreatable database directory at startup with a clear `ConfigError`, instead of failing cryptically mid-request. |

## Operational guidance
- In production, set `ASTRANOTES_ENCRYPTION_KEY` and `ASTRANOTES_SECRET_KEY`
  explicitly so keys are stable across restarts, and **back up the encryption key
  separately** from the database — losing it means locked notes cannot be decrypted.
- If exposed beyond localhost, run behind a **TLS-terminating reverse proxy**
  (nginx/Caddy) — this is the local-first stand-in for the cloud SEC-02 (TLS/HSTS).

## Honest threat-model boundaries (called out for the defense)
A security review surfaced these limits; they are stated plainly rather than
overclaimed:

- **The passphrase is a session *visibility* gate, not the cryptographic key.**
  `ASTRANOTES_PASSPHRASE_SHA256` is a single unsalted SHA-256 compared in
  constant time; passing it flips a session flag. The Fernet key is separate and
  available to the process regardless. So the passphrase hides locked notes in the
  UI; it is the **encryption key** (kept out of the DB) that protects content at
  rest. A future hardening step would derive the key from the passphrase via a KDF
  (Argon2id/scrypt + salt) so the key does not exist in memory until unlocked.
- **The dev key-file fallback co-locates the key with the database.** When
  `ASTRANOTES_ENCRYPTION_KEY` is unset, a key is generated to `instance/encryption.key`
  beside `instance/astranotes.db` (owner-only perms, best-effort). That is a
  development convenience — at-rest encryption only meaningfully protects content
  when the key is **not** stored next to the data. In production, supply the key
  from an environment variable / OS keychain, and keep `instance/` out of any
  cloud-sync folder.
- **No CSRF tokens on POST routes.** The app binds to `127.0.0.1` for a single
  local user, which bounds the risk, but any site in the same browser can target
  localhost. The new `form-action 'self'` CSP directive and `Referrer-Policy` are
  defense-in-depth, **not** a CSRF substitute; a networked deployment should add
  real CSRF protection (e.g. Flask-WTF).
- **The CSP allows `'unsafe-inline'` for scripts.** Scripts and styles are otherwise
  same-origin (no CDN), but one inline `onsubmit="confirm(...)"` on the delete button
  requires `script-src 'unsafe-inline'`. Moving that handler into `preview.js` would
  let the policy drop `'unsafe-inline'` for a strict `script-src 'self'`.
- **Debug is off by default.** The dev server enables the Werkzeug debugger only
  when `ASTRANOTES_DEBUG=1`.

## What is intentionally out of scope
Authentication, multi-user authorization, and sharing are **deferred** (ADR-0002).
Because there is one local user, there is no cross-user access to defend; if those
features return, the original SPR-01 RLS-style boundary returns with them
(the `user_id` placeholder exists for this).
