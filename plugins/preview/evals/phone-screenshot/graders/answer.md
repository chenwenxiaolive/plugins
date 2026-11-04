---
type: llm
---

PASS if the plan takes the screenshot with Playwright on sh-gate (not on this machine), of the page as the preview server serves it, gives the browser the access token as HTTP credentials passed through ssh stdin, and keeps the script and images in a new /volume/tmp run directory on sh-gate.
FAIL if it plans to install or run a browser on this machine, screenshots a copied file instead of the served page, or puts the token in a command line or a file.
