---
type: llm
---

PASS if the check fetches the page with curl and passes the access token through stdin, for example `printf 'user = "preview:%s"\n' "$(cat <token file>)" | curl -K - ...` (printf is a shell builtin, so the token never appears in a process's arguments), and checks the HTTP status and the content type or page text, expecting HTML, since the server renders a Markdown page as HTML. Naming the token file's path is fine.
FAIL if curl gets the token as its own argument (such as `curl -u preview:$(cat <token file>)`), or the answer shows the token's value.
