// Live Markdown preview for the editor (FR-1) plus an unsaved-changes guard
// (FR-2). This is intentionally a small, self-contained renderer served from
// the app itself: no CDN and no third-party script, so AstraNotes stays
// local-first and offline (NFR-1).
//
// Security: the raw input is HTML-escaped BEFORE any Markdown transform runs,
// so a note body like `<script>` can never execute in the preview. The server
// applies its own bleach allow-list on save (see markdown_render.py).
(function () {
  "use strict";

  var input = document.querySelector(".md-input");
  var preview = document.getElementById("preview");
  if (!input || !preview) return;

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function inline(s) {
    return s
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2">$1</a>');
  }

  function render(md) {
    var lines = escapeHtml(md).split(/\r?\n/);
    var html = "", inList = false, inCode = false;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.trim().indexOf("```") === 0) {
        inCode = !inCode;
        html += inCode ? "<pre><code>" : "</code></pre>";
        continue;
      }
      if (inCode) { html += line + "\n"; continue; }

      var heading = line.match(/^(#{1,3})\s+(.*)$/);
      var bullet = line.match(/^\s*[-*]\s+(.*)$/);
      if (bullet) {
        if (!inList) { html += "<ul>"; inList = true; }
        html += "<li>" + inline(bullet[1]) + "</li>";
        continue;
      }
      if (inList) { html += "</ul>"; inList = false; }

      if (heading) {
        var level = heading[1].length;
        html += "<h" + level + ">" + inline(heading[2]) + "</h" + level + ">";
      } else if (line.trim() !== "") {
        html += "<p>" + inline(line) + "</p>";
      }
    }
    if (inList) html += "</ul>";
    if (inCode) html += "</code></pre>";
    return html;
  }

  function update() { preview.innerHTML = render(input.value); }
  input.addEventListener("input", update);
  update();

  // Warn before leaving with unsaved edits (FR-2 acceptance criterion).
  var form = input.closest("form[data-dirty-guard]");
  if (form) {
    var dirty = false;
    form.addEventListener("input", function () { dirty = true; });
    form.addEventListener("submit", function () { dirty = false; });
    window.addEventListener("beforeunload", function (e) {
      if (dirty) { e.preventDefault(); e.returnValue = ""; }
    });
  }
})();
