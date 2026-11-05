---
name: preview
description: "Publishes standalone HTML and Markdown pages through this machine's preview server, checks them and returns their links; also restarts the service. Use when the user wants a page, report or preview to view in a browser, or asks about existing /preview pages. Not for tracked repository documentation, which stays where it is."
---

# Preview

Publish a page the user wants to view: write it under the preview root, check it
through the service, and return its link. [references/service.md](references/service.md)
has this machine's root, browser base URL and token, and how to restart the service;
[server/README.md](server/README.md) describes the server's features, deployment and tests.

- Write a new artifact with a descriptive name, or a task subdirectory when it has assets; don't overwrite an existing file unless it is the update target. Markdown is rendered by the server, so don't make an HTML copy; HTML uses relative asset paths.
- Tracked repository docs stay where they are; to preview one, copy it in and call it a snapshot.
- Publish only content meant for the user: no credentials, environment dumps or unrelated private files.
- The link is the browser base URL plus the URL-encoded path below the root (no `/preview` prefix). Check it with `curl` and the access token as service.md shows: the status, the content type and some of this page's text; Markdown must come back as `text/html`, never as Markdown source.
- When the layout matters (charts, wide tables, phone width, dark mode), screenshot the page with the headless browser service.md names and fix what you see before returning the link.
- If the service is down, restart it as service.md says and check again; if it still fails, report the file's path and the failed check.
