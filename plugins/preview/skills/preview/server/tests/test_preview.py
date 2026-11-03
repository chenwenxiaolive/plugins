"""Exercise rendering and file serving through the real HTTP handler."""

import base64
from functools import partial
from html.parser import HTMLParser
from http.server import ThreadingHTTPServer
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.parse import quote, urljoin
from urllib.request import ProxyHandler, Request, build_opener


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview_server", HERE / "server.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DirectoryTable(HTMLParser):
    """Read the rendered table as a user following its links would."""

    def __init__(self, html):
        super().__init__()
        self.names = []
        self.headings = []
        self.cell = 0
        self.heading = None
        self.name_link = False
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "tr":
            self.cell = 0
        elif tag == "td":
            self.cell += 1
        elif tag == "th":
            self.heading = attrs
            self.headings.append(attrs)
        elif tag == "a":
            if self.heading is not None:
                self.heading.update(attrs)
            self.name_link = self.cell == 1

    def handle_endtag(self, tag):
        if tag == "th":
            self.heading = None
        elif tag == "a":
            self.name_link = False

    def handle_data(self, text):
        if self.name_link:
            self.names.append(text)


class PreviewHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="preview-check-", dir=os.environ.get("PREVIEW_TEST_TMPDIR"))
        cls.root = Path(cls.scratch.name) / "files"
        cls.root.mkdir()
        cls.source = cls.root / "中文 document.md"
        cls.source.write_text(
            "# Preview — 中文示例\n\n"
            "| Name | Value |\n| --- | --- |\n| First | 中文 |\n\n"
            "## Details\n\n"
            "| Setting | Value |\n| --- | --- |\n| Encoding | UTF-8 |\n\n"
            "Documents render without browser CDN requests.\n",
            encoding="utf-8",
        )
        cls.nested = cls.root / "嵌套 目录"
        cls.nested.mkdir()
        cls.html = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="style.css"><h1>中文 HTML</h1><script src="app.js"></script>'
        (cls.nested / "example.html").write_text(cls.html, encoding="utf-8")
        (cls.nested / "style.css").write_text("h1 { color: blue; }", encoding="utf-8")
        (cls.nested / "app.js").write_text("document.title = 'HTML preview';", encoding="utf-8")
        (cls.nested / "example.md").write_text('# 标题\n\n| A | B |\n| --- | --- |\n| 甲 | 乙 |\n\n```python\nprint("中文")\n```\n\n[HTML](example.html)\n\n<script>alert(1)</script>\n', encoding="utf-8")
        (cls.root / "bad.md").write_bytes(b"\xff\xfeinvalid")
        outside = Path(cls.scratch.name) / "outside.txt"
        outside.write_text("outside-preview-marker", encoding="utf-8")
        (cls.root / "outside-link.txt").symlink_to(outside)
        cls.sort_root = cls.root / "sort 中文 #?"
        cls.sort_root.mkdir()
        cls.sort_url = "/" + quote(cls.sort_root.name) + "/"
        for name, size, timestamp in [
            ("Alpha.txt", 2048, 1700000000.2),
            ("beta.txt", 20, 1700000000.3),
            ("gamma.txt", 10, 1700000000.1),
            ("delta.txt", 19, 1700000000.4),
        ]:
            fixture = cls.sort_root / name
            fixture.write_bytes(b"x" * size)
            os.utime(fixture, (timestamp, timestamp))
        for name, timestamp in [("A-dir", 1700000010), ("z-dir", 1700000020)]:
            fixture = cls.sort_root / name
            fixture.mkdir()
            os.utime(fixture, (timestamp, timestamp))
        (cls.sort_root / "outside-link.txt").symlink_to(outside)
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(module.PreviewHandler, directory=str(cls.root)))
        cls.httpd.node = shutil.which("node")
        cls.worker = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_port}"
        cls.client = build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.worker.join()
        cls.scratch.cleanup()

    def fetch(self, path, method="GET", headers=None):
        with self.client.open(Request(self.base + path, method=method, headers=headers or {}), timeout=10) as response:
            return response.headers, response.read()

    def test_document_is_rendered(self):
        headers, body = self.fetch("/" + quote(self.source.name))
        html = body.decode("utf-8")
        self.assertEqual(headers.get_content_type(), "text/html")
        self.assertEqual(headers.get_content_charset(), "utf-8")
        self.assertIn("<h1 id=", html)
        self.assertIn("Preview — 中文示例", html)
        self.assertEqual(html.count("<table>"), 2)
        self.assertIn("Documents render without browser CDN requests.", html)
        self.assertNotIn("<script src=\"https://", html)

    def test_original_source_download_and_head(self):
        path = "/" + quote(self.source.name)
        headers, body = self.fetch(path + "?raw=1")
        self.assertEqual(body, self.source.read_bytes())
        self.assertEqual(headers.get_content_type(), "text/plain")
        headers, body = self.fetch(path + "?download=1")
        self.assertEqual(body, self.source.read_bytes())
        self.assertIn("filename*=UTF-8''", headers["Content-Disposition"])
        headers, body = self.fetch(path, method="HEAD")
        self.assertEqual(headers.get_content_type(), "text/html")
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["Content-Length"]), 0)

    def test_mermaid_page_loads_local_renderer_and_preserves_source(self):
        source = '```mermaid\nflowchart LR\n  A["<script>alert(1)</script>"] --> B[Done]\n```\n'
        (self.root / "diagram.md").write_text(source, encoding="utf-8")
        _, body = self.fetch("/diagram.md")
        html = body.decode("utf-8")
        self.assertIn('class="language-mermaid"', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('<script defer src="/_preview_assets/mermaid.min.js"></script>', html)
        self.assertIn('<script defer src="/_preview_assets/diagrams.js"></script>', html)
        for suffix in ["?raw=1", "?download=1"]:
            _, body = self.fetch("/diagram.md" + suffix)
            self.assertEqual(body.decode("utf-8"), source)
        for path in ["/", "/" + quote(self.source.name)]:
            _, body = self.fetch(path)
            self.assertNotIn(b'/_preview_assets/mermaid.min.js', body)
        for asset in ["mermaid.min.js", "diagrams.js"]:
            headers, body = self.fetch("/_preview_assets/" + asset)
            self.assertEqual(headers.get_content_type(), "application/javascript")
            self.assertEqual(body, (HERE / "assets" / asset).read_bytes())

    def test_markdown_features_and_relative_html_link(self):
        path = "/" + quote(self.nested.name) + "/example.md"
        _, body = self.fetch(path)
        html = body.decode("utf-8")
        self.assertIn('<h1 id="标题">标题</h1>', html)
        self.assertIn("<table>", html)
        self.assertIn('class="language-python"', html)
        self.assertIn('href="example.html"', html)
        self.assertNotIn("<script>alert(1)</script>", html)
        linked_path = urljoin(path, "example.html")
        headers, body = self.fetch(linked_path)
        self.assertEqual(headers.get_content_type(), "text/html")
        self.assertEqual(body.decode("utf-8"), self.html)

    def test_html_relative_css_and_javascript(self):
        prefix = "/" + quote(self.nested.name) + "/"
        headers, body = self.fetch(prefix + "style.css")
        self.assertEqual(headers.get_content_type(), "text/css")
        self.assertIn(b"color: blue", body)
        headers, body = self.fetch(prefix + "app.js")
        self.assertIn("javascript", headers.get_content_type())
        self.assertIn(b"document.title", body)

    def test_directory_links_and_styles(self):
        _, body = self.fetch("/")
        html = body.decode("utf-8")
        self.assertIn(quote(self.source.name), html)
        self.assertIn("?download=1", html)
        self.assertNotIn("outside-link.txt", html)
        _, body = self.fetch("/" + quote(self.nested.name))
        self.assertIn(b"Parent directory", body)
        headers, body = self.fetch("/_preview_assets/style.css")
        self.assertEqual(headers.get_content_type(), "text/css")
        self.assertIn(b"@media", body)

    def test_directory_sorting_each_column_and_direction(self):
        cases = {
            ("name", "asc"): ["A-dir", "z-dir", "Alpha.txt", "beta.txt", "delta.txt", "gamma.txt"],
            ("name", "desc"): ["z-dir", "A-dir", "gamma.txt", "delta.txt", "beta.txt", "Alpha.txt"],
            ("size", "asc"): ["A-dir", "z-dir", "gamma.txt", "delta.txt", "beta.txt", "Alpha.txt"],
            ("size", "desc"): ["A-dir", "z-dir", "Alpha.txt", "beta.txt", "delta.txt", "gamma.txt"],
            ("updated", "asc"): ["A-dir", "z-dir", "gamma.txt", "Alpha.txt", "beta.txt", "delta.txt"],
            ("updated", "desc"): ["z-dir", "A-dir", "delta.txt", "beta.txt", "Alpha.txt", "gamma.txt"],
        }
        for (column, order), expected in cases.items():
            with self.subTest(column=column, order=order):
                _, body = self.fetch(self.sort_url + f"?sort={column}&order={order}")
                table = DirectoryTable(body.decode())
                self.assertEqual(table.names, expected)
                index = ["name", "size", "updated"].index(column)
                self.assertEqual(table.headings[index]["aria-sort"], "ascending" if order == "asc" else "descending")
                self.assertEqual(sum("aria-sort" in h for h in table.headings), 1)
                opposite = "desc" if order == "asc" else "asc"
                self.assertEqual(table.headings[index]["href"], self.sort_url + f"?sort={column}&order={opposite}")
                _, toggled = self.fetch(table.headings[index]["href"])
                self.assertEqual(DirectoryTable(toggled.decode()).names, cases[column, opposite])
                self.assertNotIn("href", table.headings[3])
                for heading in table.headings[:3]:
                    self.assertEqual(heading["scope"], "col")
                    self.assertIn("Sort by", heading["aria-label"])

    def test_directory_sort_defaults_and_invalid_parameters(self):
        expected = ["A-dir", "z-dir", "Alpha.txt", "beta.txt", "delta.txt", "gamma.txt"]
        for query in ["", "?sort=unknown&order=invalid", "?sort=name&order=", "?sort=size&sort=updated&order=asc"]:
            with self.subTest(query=query):
                _, body = self.fetch(self.sort_url + query)
                table = DirectoryTable(body.decode())
                self.assertEqual(table.names, expected)
                self.assertEqual(table.headings[1]["href"], self.sort_url + "?sort=size&order=asc")
                self.assertEqual(table.headings[2]["href"], self.sort_url + "?sort=updated&order=asc")

    def test_directory_sort_redirect_head_and_empty_directory(self):
        query = "?sort=updated&order=desc"
        _, body = self.fetch(self.sort_url.rstrip("/") + query)
        self.assertEqual(DirectoryTable(body.decode()).names,
                         ["z-dir", "A-dir", "delta.txt", "beta.txt", "Alpha.txt", "gamma.txt"])
        headers, body = self.fetch(self.sort_url + query, method="HEAD")
        self.assertEqual(body, b"")
        self.assertGreater(int(headers["Content-Length"]), 0)
        _, body = self.fetch(self.sort_url + "A-dir/" + query)
        self.assertIn(b"This directory is empty", body)

    def test_directory_sort_ties_use_deterministic_name_order(self):
        with tempfile.TemporaryDirectory(dir=self.root) as directory:
            path = Path(directory)
            for name in ["beta.txt", "Beta.txt", "Alpha.txt"]:
                fixture = path / name
                fixture.write_bytes(b"same size")
                os.utime(fixture, ns=(1700000000000000000, 1700000000000000000))
            for column in ["size", "updated"]:
                for order in ["asc", "desc"]:
                    with self.subTest(column=column, order=order):
                        _, body = self.fetch(f"/{path.name}/?sort={column}&order={order}")
                        self.assertEqual(DirectoryTable(body.decode()).names,
                                         ["Alpha.txt", "Beta.txt", "beta.txt"])

    def test_theme_controls_and_script_on_generated_pages(self):
        for path in ["/", "/" + quote(self.source.name), "/" + quote(self.nested.name) + "/"]:
            with self.subTest(path=path):
                _, body = self.fetch(path)
                html = body.decode("utf-8")
                self.assertIn('for="theme-select"', html)
                self.assertIn('<select id="theme-select"', html)
                for theme in ["system", "light", "dark"]:
                    self.assertIn(f'<option value="{theme}">', html)
                self.assertIn('<script src="/_preview_assets/theme.js"></script>', html)
                self.assertLess(html.index("theme.js"), html.index("style.css"))
        headers, body = self.fetch("/_preview_assets/theme.js")
        self.assertEqual(headers.get_content_type(), "application/javascript")
        self.assertEqual(body, (HERE / "assets/theme.js").read_bytes())
        headers, head = self.fetch("/_preview_assets/theme.js", method="HEAD")
        self.assertEqual(head, b"")
        self.assertEqual(int(headers["Content-Length"]), len(body))

    def test_theme_behavior(self):
        result = subprocess.run(
            [self.httpd.node, "--test", str(HERE / "tests/theme.test.cjs")],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_paths_cannot_escape_the_preview_root(self):
        for path in ["/%2e%2e/outside.txt", "/outside-link.txt"]:
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                self.fetch(path)
            self.assertEqual(error.exception.code, 403)

    def test_clear_missing_file_and_encoding_errors(self):
        for path, status in [("/missing.md", 404), ("/bad.md", 422)]:
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                self.fetch(path)
            self.assertEqual(error.exception.code, status)

    def test_refresh_reads_the_current_file(self):
        source = self.root / "refresh.md"
        source.write_text("# First version", encoding="utf-8")
        self.fetch("/refresh.md")
        source.write_text("# Updated version", encoding="utf-8")
        headers, body = self.fetch("/refresh.md", headers={"If-Modified-Since": "Tue, 01 Jan 2099 00:00:00 GMT"})
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn(b"Updated version", body)
        self.assertNotIn(b"First version", body)


class TokenAccessTests(unittest.TestCase):
    TOKEN = "test token: with spaces."

    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix="preview-token-", dir=os.environ.get("PREVIEW_TEST_TMPDIR"))
        cls.root = Path(cls.scratch.name)
        (cls.root / "secret.md").write_text("# Secret marker\n", encoding="utf-8")
        handler = partial(module.PreviewHandler, directory=str(cls.root), token=cls.TOKEN)
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.httpd.node = shutil.which("node")
        cls.worker = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_port}"
        cls.client = build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.worker.join()
        cls.scratch.cleanup()

    def fetch(self, path, credentials=None, method="GET"):
        headers = {}
        if credentials is not None:
            headers["Authorization"] = "Basic " + base64.b64encode(credentials.encode()).decode()
        return self.client.open(Request(self.base + path, method=method, headers=headers), timeout=10)

    def test_requests_without_the_token_are_refused(self):
        for path in ["/secret.md", "/", "/secret.md?raw=1", "/_preview_assets/style.css"]:
            for credentials in [None, "user:wrong", "test token: with spaces.:", "garbage"]:
                with self.subTest(path=path, credentials=credentials), self.assertRaises(HTTPError) as error:
                    self.fetch(path, credentials)
                self.assertEqual(error.exception.code, 401)
                self.assertTrue(error.exception.headers["WWW-Authenticate"].startswith("Basic "))
                self.assertNotIn(b"Secret marker", error.exception.read())
        with self.assertRaises(HTTPError) as error:
            self.fetch("/secret.md", method="HEAD")
        self.assertEqual(error.exception.code, 401)

    def test_the_token_as_password_opens_every_page(self):
        for username in ["", "anyone"]:
            with self.subTest(username=username), self.fetch("/secret.md", username + ":" + self.TOKEN) as response:
                self.assertEqual(response.headers.get_content_type(), "text/html")
                self.assertIn(b"Secret marker", response.read())
        with self.fetch("/secret.md?raw=1", "x:" + self.TOKEN) as response:
            self.assertEqual(response.read(), b"# Secret marker\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
