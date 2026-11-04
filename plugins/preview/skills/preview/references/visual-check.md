# Visual check in headless Chromium

This machine has no browser. Render the page on `sh-gate` (the owner's choice; it shares
the sh `/volume`) with `scripts/browser-shot.sh`. The script reuses the browser
environment `/volume/tmp/preview-browser-20261104-XrJSjB`; if that is gone, pass a new
`mktemp -d /volume/tmp/preview-browser-<date>-XXXXXX` and record it here. The first run
fills it in about 25 s without installing anything system-wide.

```sh
run=$(ssh sh-gate 'mktemp -d /volume/tmp/preview-shot-$(date +%Y%m%d)-XXXXXX')
scp scripts/browser-shot.sh <page>.html sh-gate:$run/   # a page with assets: also its task subdirectory
ssh sh-gate "bash $run/browser-shot.sh <env> $run/<page>.html $run/out"
scp "sh-gate:$run/out/*" <scratch>/
```

It shoots the page at 1280 and 400 px, light and dark, in slices of 1400 px. View the
slices and check:

- `report.json` shows no errors and `overflow_px` 0;
- chart text is still readable at 400 px (otherwise give the chart a minimum width
  inside an `overflow-x: auto` box);
- no labels overlap, nothing runs past the margin, and colors hold in dark mode.

Fix the page, shoot it again, then remove the run directory.
