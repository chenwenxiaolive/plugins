#!/usr/bin/env bash
# Build a user-space headless Chromium environment for preview screenshots.
# Usage (on the browser host, see references/visual-check.md): browser-env.sh <env-dir>
#
# Everything lands in <env-dir>: a uv venv with Playwright and Pillow, the Chromium
# headless shell, and the shared libraries and fonts it needs, unpacked from Ubuntu
# packages. apt runs with its lists and cache inside <env-dir>, so no system
# package or apt state changes. <env-dir>/python runs the venv's Python with the
# browser's paths set.
set -euo pipefail

ENV_DIR=${1:?usage: browser-env.sh <env-dir>}
mkdir -p "$ENV_DIR"
ENV_DIR=$(cd "$ENV_DIR" && pwd -P)
cd "$ENV_DIR"
mkdir -p tmp home debs root
export UV_CACHE_DIR=$ENV_DIR/uv-cache PLAYWRIGHT_BROWSERS_PATH=$ENV_DIR/browsers TMPDIR=$ENV_DIR/tmp

[[ -x venv/bin/python ]] || uv venv -q "$ENV_DIR/venv"
uv pip install -q --python "$ENV_DIR/venv/bin/python" playwright pillow
"$ENV_DIR/venv/bin/python" -m playwright install --only-shell chromium

# Ubuntu 24.04 names: Chromium's X11/xcb, NSS, ATK and GBM libraries, then fonts.
PACKAGES=(
  libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxi6
  libxcb1 libxau6 libxdmcp6 libxkbcommon0 libatk1.0-0t64 libatk-bridge2.0-0t64 libatspi2.0-0t64
  libgbm1 libwayland-server0 libdrm2 libnspr4 libnss3
  fonts-dejavu-core fonts-liberation
)
codename=$(. /etc/os-release && echo "${VERSION_CODENAME:?}")
apt_dir=$ENV_DIR/apt
mkdir -p "$apt_dir/lists/partial" "$apt_dir/cache/archives/partial"
cat > "$apt_dir/sources.list" <<EOF
deb http://archive.ubuntu.com/ubuntu $codename main universe
deb http://archive.ubuntu.com/ubuntu $codename-updates main universe
deb http://security.ubuntu.com/ubuntu $codename-security main universe
EOF
APT=(apt-get -q
  -o "Dir::State::Lists=$apt_dir/lists" -o "Dir::Cache=$apt_dir/cache"
  -o "Dir::Etc::sourcelist=$apt_dir/sources.list" -o "Dir::Etc::sourceparts=-"
  -o Debug::NoLocking=1 -o APT::Sandbox::User=root)
"${APT[@]}" update >/dev/null
(cd debs && "${APT[@]}" download "${PACKAGES[@]}" >/dev/null)
for deb in debs/*.deb; do
  dpkg -x "$deb" "$ENV_DIR/root"
done

cat > fonts.conf <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>$ENV_DIR/root/usr/share/fonts</dir>
  <cachedir>$ENV_DIR/fontcache</cachedir>
  <alias><family>sans-serif</family><prefer><family>DejaVu Sans</family></prefer></alias>
  <alias><family>system-ui</family><prefer><family>DejaVu Sans</family></prefer></alias>
  <alias><family>monospace</family><prefer><family>DejaVu Sans Mono</family></prefer></alias>
</fontconfig>
EOF

{
  echo '#!/usr/bin/env bash'
  echo '# The browser environment'\''s Python; written by browser-env.sh.'
  printf 'env_dir=%q\n' "$ENV_DIR"
  echo 'export PLAYWRIGHT_BROWSERS_PATH=$env_dir/browsers LD_LIBRARY_PATH=$env_dir/root/usr/lib/x86_64-linux-gnu'
  echo 'export FONTCONFIG_FILE=$env_dir/fonts.conf HOME=$env_dir/home TMPDIR=$env_dir/tmp'
  echo 'exec "$env_dir/venv/bin/python" "$@"'
} > python
chmod 755 python

shell=$(find "$PLAYWRIGHT_BROWSERS_PATH" -type f -name chrome-headless-shell | head -n 1)
[[ -n "$shell" ]] || { echo "browser-env: no chrome-headless-shell under $PLAYWRIGHT_BROWSERS_PATH" >&2; exit 1; }
missing=$(LD_LIBRARY_PATH=$ENV_DIR/root/usr/lib/x86_64-linux-gnu ldd "$shell" | awk '/not found/ {print $1}' | sort -u)
if [[ -n "$missing" ]]; then
  echo "browser-env: Chromium still misses shared libraries:" $missing >&2
  exit 1
fi
if [[ -z "$(find "$ENV_DIR/root/usr/share/fonts" -name '*.ttf' 2>/dev/null | head -n 1)" ]]; then
  echo "browser-env: no fonts were unpacked; text would not render" >&2
  exit 1
fi
echo "browser-env: ready in $ENV_DIR (run $ENV_DIR/python)"
