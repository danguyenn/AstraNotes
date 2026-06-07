"""Capture demo screenshots from the running app (headless Chromium).

Prereqs:  pip install playwright && playwright install chromium
Run the app first (`astranotes` or waitress), seed it (`python demo/seed_data.py`),
then:  python demo/capture_screenshots.py
"""

import pathlib

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
OUT = pathlib.Path(__file__).resolve().parent / "screenshots"
OUT.mkdir(exist_ok=True)


def shot(page, name):
    page.screenshot(path=str(OUT / name), full_page=True)
    print("saved", name)


with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    page.goto(BASE, wait_until="networkidle")
    shot(page, "01-dashboard.png")

    page.goto(BASE + "/notes/new", wait_until="networkidle")
    page.fill(".title-input", "Demo: live Markdown preview")
    page.fill(".md-input", "# Heading\n\n**bold**, *italic*, and `inline code`\n\n- first item\n- second item\n\n```\ncode block\n```")
    page.wait_for_timeout(400)
    shot(page, "02-editor-live-preview.png")

    page.goto(BASE, wait_until="networkidle")
    page.locator("a.note-title", has_text="Architecture").first.click()
    page.wait_for_load_state("networkidle")
    shot(page, "03-note-view.png")

    page.locator("a", has_text="History").first.click()
    page.wait_for_load_state("networkidle")
    shot(page, "04-history.png")

    page.goto(BASE + "/search?q=encryption", wait_until="networkidle")
    shot(page, "05-search.png")

    page.goto(BASE + "/unlock", wait_until="networkidle")
    shot(page, "06-unlock.png")

    page.goto(BASE + "/settings", wait_until="networkidle")
    shot(page, "07-settings-audit.png")

    browser.close()

print("done — screenshots in", OUT)
