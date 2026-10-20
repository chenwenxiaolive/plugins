---
name: preview
description: Create or update standalone HTML and Markdown artifacts in the local /preview service and return verified browser links. Use for requested document previews, reports, or existing /preview artifacts. Keep tracked repository documentation in its established location.
---

# Preview

Publish the requested artifact through the existing preview service.

## Resolve the destination

Read [the service reference](references/service.md) before the first publication
in a task. Apply an explicit destination from the user, then environment overrides,
then the documented machine defaults. The directory and browser base URL must
refer to the same service.

Confirm that the preview directory exists. If the service mapping is unknown,
inspect the relevant local configuration or ask for the missing address. A
listener on port 8000 alone does not establish a browser URL.

## Write the artifact

- Honor the requested format. Markdown can be served directly; do not generate
  an HTML copy just to make it viewable.
- Put a new standalone artifact in the preview directory. Use a descriptive
  filename, or a task subdirectory when it has companion assets. Check for a
  collision before writing. Update an existing artifact only when the task
  identifies it as the update target.
- Keep tracked repository documentation in its existing location. If a browser
  preview of that documentation is requested, copy the requested document and
  needed assets into the preview directory and identify the copy as a snapshot.
- Write UTF-8. For HTML, set the charset, title, and viewport; use readable,
  responsive styling. Use relative paths for companion assets. Escape embedded
  data when generating HTML.
- Resolve destination paths and symlinks before writing; keep the artifact and
  copied assets inside the preview root. Copy only task-relevant files.
- Publish only content intended for the user to view. Keep credentials, environment
  dumps, and unrelated private files out of artifacts.

## Verify and link

Construct the URL from the configured base URL and the path relative to the
preview root. URL-encode path components, including spaces, Unicode, `#`, and `?`;
preserve directory separators. Do not include the filesystem's `/preview` prefix
unless it is part of the configured URL base.

Fetch the actual artifact URL with a bounded request, for example
`curl --fail --silent --show-error --max-time 10 <url>`. Check the response status,
content type, and an expected part of this artifact. For Markdown, confirm that
the response contains rendered HTML. A directory listing or a successful file
write alone is insufficient.

Check required local assets too. If a browser tool is available, inspect HTML
layout or interactions when the artifact depends on them; otherwise state any
material verification limit.

Return a descriptive Markdown link to the artifact's browser URL. Include source
or download links when useful, using the service's documented query parameters.

If the service is unavailable, retain the artifact, report its local path and the
failed access check, and distinguish an expected URL from a verified one. Do not
start a replacement server, open ports, or change shared service configuration
unless the user requested that operations work.
