---
name: preview
description: Create or update standalone HTML and Markdown artifacts in the local /preview service, verify them, and return links at its configured browser URL. Use for requested document previews, reports, existing /preview artifacts, or managing the bundled service. Keep tracked repository documentation in its established location.
---

# Preview

Publish a page the user wants to view: write it under the preview root, check it
through the service, and return its link. [references/service.md](references/service.md)
has this machine's root and browser URL, and how to start or restart the service.

- Write a new artifact with a descriptive name, or a task subdirectory when it has assets; don't overwrite an existing file unless it is the update target. Markdown is rendered by the server, so don't make an HTML copy. HTML needs a charset, title and viewport, and relative asset paths.
- Tracked repository docs stay where they are; to preview one, copy it in and call it a snapshot.
- Publish only content meant for the user: no credentials, environment dumps or unrelated private files.
- The link is the browser base URL plus the URL-encoded path below the root (no `/preview` prefix). Check it with `curl --fail -sS --max-time 10 <url>`: the status, the content type and some of this page's text; Markdown must come back as HTML.
- If the service is down, start it with the saved settings (service.md) and check again; never change those settings as a side effect. If it still fails, keep the file and report its path and the failed check.
