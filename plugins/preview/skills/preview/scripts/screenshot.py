"""Full-page screenshots of a local HTML file in headless Chromium, sliced for viewing.

Run with the browser environment's Python (references/visual-check.md):
    <env>/python - PAGE OUT [--widths 1280,400] [--schemes light,dark] [--slice 1400]

For every width and color scheme it writes OUT/<width>-<scheme>.png, its slices
OUT/<width>-<scheme>-<n>.png of at most --slice pixels, and OUT/report.json with the
console and page errors, the horizontal overflow and the size of every SVG.
"""

import argparse
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("page", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--widths", default="1280,400")
    parser.add_argument("--schemes", default="light,dark")
    parser.add_argument("--slice", type=int, default=1400, help="slice height in pixels")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for width in map(int, args.widths.split(",")):
            for scheme in args.schemes.split(","):
                context = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
                page = context.new_page()
                errors = []
                page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
                page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
                page.goto(args.page.resolve().as_uri(), wait_until="load")
                page.wait_for_timeout(500)
                name = f"{width}-{scheme}"
                full = args.out / f"{name}.png"
                page.screenshot(path=str(full), full_page=True)
                report[name] = {
                    "errors": errors,
                    # A phone layout must not scroll sideways.
                    "horizontal_overflow_px": page.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"),
                    "svg_sizes": page.evaluate(
                        "[...document.querySelectorAll('svg')].map(s => {"
                        " const r = s.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })"),
                    "height": page.evaluate("document.documentElement.scrollHeight"),
                }
                context.close()
                with Image.open(full) as image:
                    for index, top in enumerate(range(0, image.height, args.slice)):
                        image.crop((0, top, image.width, min(image.height, top + args.slice))).save(
                            args.out / f"{name}-{index}.png")
        browser.close()
    (args.out / "report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({name: {k: v for k, v in entry.items() if k != "svg_sizes"} for name, entry in report.items()}))


if __name__ == "__main__":
    main()
