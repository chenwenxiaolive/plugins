---
type: llm
---

PASS if it passes the token as a BuildKit secret (`RUN --mount=type=secret,...` with `--secret id=...,src=...`), removes the token from the clone's remote URL, and checks the image history for the token (for example `docker history --no-trunc ... | grep -c glpat-`) before pushing.
FAIL if it passes the token with --build-arg or ENV.
