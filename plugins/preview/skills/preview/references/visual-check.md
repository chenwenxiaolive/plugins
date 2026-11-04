# Visual check in headless Chromium

This machine has no browser or display. Render a page in headless Chromium on the
browser host instead, and look at the screenshots.

| Setting | Value |
| --- | --- |
| Browser host | `sh-gate` (the owner's choice; it shares the sh cluster's `/volume`) |
| Browser environment | `/volume/tmp/preview-browser-20261104-cGh9jv` on that `/volume` |

The environment lives in user space and contains:

- a Playwright venv;
- the Chromium headless shell;
- the shared libraries and fonts Chromium needs, unpacked from Ubuntu packages.

apt keeps its lists and cache inside the environment. Building it installs no system
package, writes no apt state, and leaves the gate's proxy and tunnel alone.

## Check a page

1. Create a run directory on the host with `mktemp -d /volume/tmp/preview-shot-$(date +%Y%m%d)-XXXXXX`.
2. Copy the page there. For a page with assets, copy its task subdirectory too, but never the whole preview root. The page is opened as a file, so the token-protected URL isn't needed.
3. Stream the screenshot script to the environment's Python. Widths default to 1280 and 400 pixels, schemes to light and dark:
   ```sh
   ssh sh-gate "<env>/python - <run>/<page>.html <run>/out" < scripts/screenshot.py
   ```
4. Copy back `out/report.json` and the slices (`out/*-[0-9]*.png`, cut from each full-page shot) to the session's scratch directory. Then view them.

## What to check

- `report.json`: `errors` (console and page errors) and `horizontal_overflow_px` at 400 pixels must be empty and 0.
- Charts and diagrams at phone width: text that becomes too small to read. Wrap such a chart in an `overflow-x: auto` box with a minimum width.
- Overlapping labels, panels running past the margin, and colors that disappear in dark mode.
- Captions that claim more than the chart shows.

Fix the page, render it again, and remove the run directory when you're done. Keep the environment.

## Rebuild the environment

If the environment is missing or a run fails to launch the browser, build a new one. The script
targets Ubuntu 24.04 package names:

```sh
env=$(ssh sh-gate 'mktemp -d /volume/tmp/preview-browser-$(date +%Y%m%d)-XXXXXX')
ssh sh-gate "bash -s -- $env" < scripts/browser-env.sh
```

It finishes by checking that Chromium resolves every shared library and finds fonts.
Record the new path in the table above.
