---
type: llm
---

The run has no shell, so judge the plan.
PASS if the plan takes the screenshot with Playwright on sh-gate rather than on this machine, loads the page from the preview server's URL rather than a copied file, gives the browser the access token as HTTP credentials sent over ssh stdin, and keeps the script and images in a new /volume/tmp run directory on sh-gate. Extra checks, such as fetching the page with `printf ... "$(cat <token file>)" | curl -K -`, are fine.
FAIL if the plan installs or runs a browser on this machine, screenshots a copied file, passes the token's value as an argument to another program, or writes it to a file.
