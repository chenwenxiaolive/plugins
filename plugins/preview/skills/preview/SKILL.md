---
name: preview
description: Create or update standalone HTML and Markdown artifacts in the local /preview service, verify them, and return links at its configured browser URL. Use for requested document previews, reports, existing /preview artifacts, or managing the bundled service. Keep tracked repository documentation in its established location.
---

# Preview

Publish a page the user wants to view: write it under the preview root, check it
through the service, and return its link. [references/service.md](references/service.md)
has this machine's root, browser URL and token, and how to restart the service.

- Write a new artifact with a descriptive name, or a task subdirectory when it has assets; don't overwrite an existing file unless it is the update target. Markdown is rendered by the server, so don't make an HTML copy. HTML needs a charset, title and viewport, and relative asset paths.
- Tracked repository docs stay where they are; to preview one, copy it in and call it a snapshot.
- Publish only content meant for the user: no credentials, environment dumps or unrelated private files.
- The link is the browser base URL plus the URL-encoded path below the root (no `/preview` prefix). Check it with `curl` and the access token as service.md shows: the status, the content type and some of this page's text; Markdown must come back as HTML.
- When the layout matters (charts, wide tables, phone width, dark mode), look at the page rendered: [references/visual-check.md](references/visual-check.md) screenshots it in headless Chromium. `curl` only shows that the server returns the page. Fix what the screenshots show before returning the link.
- If the service is down, restart it as service.md says and check again; never change its settings as a side effect. If it still fails, keep the file and report its path and the failed check.
