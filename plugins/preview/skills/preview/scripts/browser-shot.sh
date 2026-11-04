#!/usr/bin/env bash
# Screenshot a local HTML page in headless Chromium (references/visual-check.md).
# Usage, on the browser host: browser-shot.sh <env-dir> <page.html> <out-dir>
# The first run fills <env-dir>: Playwright's Chromium and the libraries and fonts it
# needs, unpacked from Ubuntu 24.04 packages. apt keeps its lists and cache there too,
# so nothing is installed system-wide.
set -euo pipefail
env_dir=$1 page=$2 out=$3
mkdir -p "$env_dir" "$out"
env_dir=$(cd "$env_dir" && pwd -P)
export PLAYWRIGHT_BROWSERS_PATH=$env_dir/browsers TMPDIR=$env_dir/tmp UV_CACHE_DIR=$env_dir/uv-cache
export LD_LIBRARY_PATH=$env_dir/root/usr/lib/x86_64-linux-gnu FONTCONFIG_FILE=$env_dir/fonts.conf

if [[ ! -e $env_dir/ready ]]; then
  mkdir -p "$TMPDIR" "$env_dir/debs" "$env_dir/apt/lists/partial" "$env_dir/apt/cache/archives/partial"
  [[ -x $env_dir/venv/bin/python ]] || uv venv -q "$env_dir/venv"
  uv pip install -q --python "$env_dir/venv/bin/python" playwright
  "$env_dir/venv/bin/python" -m playwright install --only-shell chromium
  printf 'deb http://archive.ubuntu.com/ubuntu %s main universe\n' noble noble-updates > "$env_dir/apt/sources.list"
  echo "deb http://security.ubuntu.com/ubuntu noble-security main universe" >> "$env_dir/apt/sources.list"
  apt=(apt-get -qq -o "Dir::State::Lists=$env_dir/apt/lists" -o "Dir::Cache=$env_dir/apt/cache"
    -o "Dir::Etc::sourcelist=$env_dir/apt/sources.list" -o Dir::Etc::sourceparts=-
    -o Debug::NoLocking=1 -o APT::Sandbox::User=root)
  "${apt[@]}" update
  (cd "$env_dir/debs" && "${apt[@]}" download libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxrender1 libxi6 libxcb1 libxau6 libxdmcp6 libxkbcommon0 libatk1.0-0t64 \
    libatk-bridge2.0-0t64 libatspi2.0-0t64 libgbm1 libwayland-server0 libdrm2 libnspr4 libnss3 \
    fonts-dejavu-core)
  for deb in "$env_dir"/debs/*.deb; do dpkg -x "$deb" "$env_dir/root"; done
  echo "<fontconfig><dir>$env_dir/root/usr/share/fonts</dir><alias><family>monospace</family><prefer><family>DejaVu Sans Mono</family></prefer></alias></fontconfig>" > "$FONTCONFIG_FILE"
  touch "$env_dir/ready"
fi

# 1280 and 400 px wide, light and dark: slices of 1400 px and report.json (errors, sideways overflow).
"$env_dir/venv/bin/python" - "$page" "$out" <<'EOF'
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

page_path, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
report = {}
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    for width in (1280, 400):
        for scheme in ("light", "dark"):
            page = browser.new_page(viewport={"width": width, "height": 900}, color_scheme=scheme)
            errors = []
            page.on("console", lambda message: message.type == "error" and errors.append(message.text))
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(page_path.as_uri())
            height = page.evaluate("document.documentElement.scrollHeight")
            for index, top in enumerate(range(0, height, 1400)):
                clip = {"x": 0, "y": top, "width": width, "height": min(1400, height - top)}
                page.screenshot(path=out / f"{width}-{scheme}-{index}.png", full_page=True, clip=clip)
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            report[f"{width}-{scheme}"] = {"errors": errors, "overflow_px": overflow}
            page.close()
(out / "report.json").write_text(json.dumps(report, indent=1))
print(json.dumps(report))
EOF
