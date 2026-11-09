---
type: llm
---

PASS if the script builds the SiFlow client with an explicit region and cluster (`cn-shanghai`, `changliu`) and credentials from the environment, runs it with the SDK wheel (it isn't on PyPI, for example through `uv run --with`), prints named fields of `tasks.list` (such as uuid, name, status and resource pool), and notes that retry sub-tasks count as rows or that the list may be partial.
FAIL if it relies on the SDK's default cluster (`cn-beijing/auriga`), puts credentials in the script or command line, or prints whole task records.
