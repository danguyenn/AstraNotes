"""Server-side Markdown rendering with HTML sanitization (SEC / FR-1).

Note content is untrusted input, so rendered HTML is run through a bleach
allow-list before it reaches a template. This is what stops a note body like
`<script>steal()</script>` from executing — the client-side live preview applies
the same escape-first rule (see static/preview.js).
"""

import bleach
import markdown as md
from markupsafe import Markup

_ALLOWED_TAGS = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "br",
    "hr",
    "blockquote",
    "strong",
    "em",
    "del",
    "code",
    "pre",
    "ul",
    "ol",
    "li",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]
_ALLOWED_ATTRS = {"a": ["href", "title"]}


def render_markdown(text: str | None) -> Markup:
    if not text:
        return Markup("")
    html = md.markdown(text, extensions=["fenced_code", "tables", "sane_lists"])
    clean = bleach.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)
    return Markup(clean)
