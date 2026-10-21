"""Preview a directory: render Markdown, serve HTML, and download originals."""

import argparse
from datetime import datetime
from functools import partial
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
from urllib.parse import parse_qs, quote, unquote, urlsplit


SERVICE_DIR = Path(__file__).resolve().parent
MARKDOWN_SUFFIXES = {".md", ".markdown"}


def page(title, content, location, actions=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · Preview</title>
<script src="/_preview_assets/theme.js"></script>
<link rel="stylesheet" href="/_preview_assets/style.css"></head>
<body><header class="topbar"><a class="brand" href="/">Directory Preview</a>
<div class="topbar-tools"><span class="tagline">Markdown &amp; HTML</span>
<label class="theme-control" for="theme-select">Theme
<select id="theme-select"><option value="system">System</option>
<option value="light">Light</option><option value="dark">Dark</option></select>
</label></div></header>
<main class="container"><div class="toolbar"><div class="location">{escape(location)}</div>
<nav class="actions">{actions}</nav></div><article class="paper markdown">{content}</article></main>
</body></html>""".encode("utf-8")


def button(label, url):
    return f'<a class="button" href="{escape(url, quote=True)}">{escape(label)}</a>'


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, **kwargs):
        self.root = Path(directory).resolve()
        super().__init__(*args, directory=str(self.root), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def guess_type(self, path):
        if Path(path).suffix.lower() in MARKDOWN_SUFFIXES:
            return "text/plain; charset=utf-8"
        content_type = super().guess_type(path)
        if content_type.startswith("text/") or content_type == "application/javascript":
            return content_type + "; charset=utf-8"
        return content_type

    def response_bytes(self, body, content_type="text/html; charset=utf-8", download=None):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if download:
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(download, safe=""))
        self.end_headers()
        return BytesIO(body)

    def send_head(self):
        request = urlsplit(self.path)
        if request.path == "/_preview_assets/style.css":
            return self.response_bytes((SERVICE_DIR / "assets/style.css").read_bytes(), "text/css; charset=utf-8")
        if request.path == "/_preview_assets/theme.js":
            return self.response_bytes((SERVICE_DIR / "assets/theme.js").read_bytes(), "application/javascript; charset=utf-8")
        try:
            decoded = unquote(request.path, errors="strict")
            if "\x00" in decoded:
                raise ValueError("Invalid path")
            path = (self.root / decoded.lstrip("/")).resolve()
            if not path.is_relative_to(self.root):
                self.send_error(403, "Path is outside the preview directory")
                return None
        except (ValueError, OSError, RuntimeError):
            self.send_error(400, "Invalid path")
            return None
        if not path.exists():
            self.send_error(404, "File not found")
            return None
        if path.is_dir():
            if not decoded.endswith("/"):
                self.send_response(301)
                location = quote(decoded + "/", safe="/")
                if request.query:
                    location += "?" + request.query
                self.send_header("Location", location)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            return self.directory_page(path, decoded)
        if not path.is_file():
            self.send_error(403, "Only regular files can be previewed")
            return None

        query = parse_qs(request.query)
        download = query.get("download") == ["1"]
        raw = query.get("raw") == ["1"]
        if path.suffix.lower() in MARKDOWN_SUFFIXES and not (raw or download):
            return self.markdown_page(path, decoded)

        # Force fresh responses so earlier cached encodings cannot survive a 304.
        if "If-Modified-Since" in self.headers:
            del self.headers["If-Modified-Since"]
        try:
            stream = path.open("rb")
            size = path.stat().st_size
        except OSError:
            self.send_error(404, "File could not be opened")
            return None
        content_type = "text/plain; charset=utf-8" if raw else self.guess_type(str(path))
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(size))
        if download:
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + quote(path.name, safe=""))
        self.end_headers()
        return stream

    def markdown_page(self, path, decoded):
        try:
            if path.stat().st_size > 8 * 1024 * 1024:
                self.send_error(413, "Markdown preview is limited to 8 MiB; use the raw or download link")
                return None
            source = path.read_text(encoding="utf-8-sig")
            result = subprocess.run(
                [self.server.node, str(SERVICE_DIR / "renderer.cjs")],
                input=source, text=True, encoding="utf-8", capture_output=True,
                timeout=10, check=True,
            )
        except UnicodeDecodeError:
            self.send_error(422, "Markdown must use UTF-8 encoding")
            return None
        except (OSError, subprocess.SubprocessError):
            self.send_error(500, "Markdown rendering failed")
            return None
        url = quote(decoded, safe="/")
        parent = quote(decoded.rsplit("/", 1)[0] + "/", safe="/")
        actions = button("Files", parent) + button("Source", url + "?raw=1") + button("Download", url + "?download=1")
        return self.response_bytes(page(path.name, result.stdout, decoded, actions))

    def directory_page(self, path, decoded):
        query = parse_qs(urlsplit(self.path).query)
        column = query.get("sort", ["name"])
        column = column[0] if len(column) == 1 and column[0] in {"name", "size", "updated"} else "name"
        descending = query.get("order") == ["desc"]
        entries = []
        try:
            children = list(path.iterdir())
        except OSError:
            self.send_error(403, "Directory could not be read")
            return None
        for child in children:
            try:
                if not child.resolve().is_relative_to(self.root):
                    continue
                is_directory = child.is_dir()
                if not (is_directory or child.is_file()):
                    continue
                stat = child.stat()
            except (OSError, RuntimeError):
                continue
            entries.append((child, is_directory, stat))

        # Stable sorts keep name ties deterministic and directories first in either direction.
        entries.sort(key=lambda entry: (entry[0].name.casefold(), entry[0].name))
        sort_keys = {
            "name": lambda entry: (entry[0].name.casefold(), entry[0].name),
            "size": lambda entry: 0 if entry[1] else entry[2].st_size,
            "updated": lambda entry: entry[2].st_mtime_ns,
        }
        entries.sort(key=sort_keys[column], reverse=descending)
        entries.sort(key=lambda entry: not entry[1])
        rows = []
        for child, is_directory, stat in entries:
            url = quote(decoded + child.name + ("/" if is_directory else ""), safe="/")
            kind = "DIR" if is_directory else child.suffix.lstrip(".").upper() or "FILE"
            size = "—" if is_directory else f"{stat.st_size / 1024:.1f} KB"
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            actions = "" if is_directory else f'<a href="{url}?raw=1">Source</a><a href="{url}?download=1">Download</a>'
            rows.append(f'<tr><td><span class="tag">{escape(kind)}</span><a href="{url}">{escape(child.name)}</a></td><td class="details">{size}</td><td class="details">{modified}</td><td class="file-actions">{actions}</td></tr>')
        title = "Files in /preview" if decoded == "/" else "Files in " + decoded
        content = f'<h1>{escape(title)}</h1><p class="hint">Open a Markdown or HTML file to preview it. Refresh after updating a file.</p>'
        if rows:
            headings = []
            for key, label in (("name", "Name"), ("size", "Size"), ("updated", "Updated")):
                active = column == key
                next_order = "desc" if active and not descending else "asc"
                direction = "descending" if descending else "ascending"
                aria = f' aria-sort="{direction}"' if active else ""
                indicator = ("▼" if descending else "▲") if active else "↕"
                url = quote(decoded, safe="/") + f"?sort={key}&order={next_order}"
                next_direction = "descending" if next_order == "desc" else "ascending"
                headings.append(f'<th scope="col"{aria}><a class="sort-heading" href="{escape(url, quote=True)}" aria-label="Sort by {label} {next_direction}">{label} <span aria-hidden="true">{indicator}</span></a></th>')
            content += '<table class="file-table"><thead><tr>' + "".join(headings) + '<th scope="col">Original</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
        else:
            content += '<p class="empty">This directory is empty.</p>'
        actions = button("Parent directory", quote(decoded.rstrip("/").rsplit("/", 1)[0] + "/", safe="/")) if decoded != "/" else ""
        return self.response_bytes(page(title, content, decoded, actions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", default="/preview")
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    node = shutil.which("node")
    if not node:
        parser.error("The existing Node executable is required for Markdown rendering")
    root = Path(args.directory).resolve()
    if not root.is_dir():
        parser.error("The preview directory does not exist")
    handler = partial(PreviewHandler, directory=str(root))
    with ThreadingHTTPServer((args.bind, args.port), handler) as server:
        server.node = node
        print(f"Serving Markdown and HTML from {root} on {args.bind}:{args.port}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
