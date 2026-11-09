---
name: siflow
description: "Inspects the SiFlow (Scitix) AI platform at console.siflow.cn through its AK/SK Python SDK, read-only unless the user asks for a change. Use for SiFlow console questions and AI platform training tasks, pods, logs, metrics, resource pools, quotas, images or volumes; not for Alibaba Cloud PAI or the GPU cluster's nodes."
---

# SiFlow AI platform

Answer SiFlow questions from live data through the `siflow` Python SDK. The vendor
documents the platform and SDK for agents in [skill.md](https://docs.siflow.cn/skill.md)
and the page index [llms.txt](https://docs.siflow.cn/llms.txt) (each page also as
`.md`), and the SDK's docstrings cover paging, retry sub-tasks and field meanings:
read those for calls and parameters. [references/current-environment.md](references/current-environment.md)
has the wheel URL, this account's clusters and pools, and what was checked.

## Running the SDK

- The SDK isn't on PyPI. Run each script without an environment:
  `uv run --no-project --with 'siflow @ <wheel URL>' python -I <script>`; the same
  invocation reads docstrings with `-c 'from siflow.resources import Tasks; help(Tasks.list)'`.
- Keep scripts in the session scratchpad or a new `/volume/tmp/siflow-<YYYYMMDD>-XXXXXX`, never in a repository.
- `SiFlow(region=..., cluster=...)` reads `SIFLOW_ACCESS_KEY_ID` and `SIFLOW_ACCESS_KEY_SECRET` from the environment; pass neither as an argument.
- Pass `region` and `cluster` to every client: the default `cn-beijing/auriga` is offline and returns 410. When the user names no cluster, use `cn-shanghai/changliu`; for a task that isn't there, list the other `siflow.cn` clusters in the reference and say which were searched.
- The SDK has no account call. `client.get("https://console.siflow.cn/api/v1/ram/user/userInfo", cast_to=dict[str, object])` returns `rows`; print only `name`, `orgName` and `teamName`.

## Output

- Print named fields, never a whole record or `model_dump()`: `userInfo` rows hold `password`, `idNo` and `phoneNumber`, and task records hold `task_env`, `cmd`, image settings and `oss.access_key`/`secret_key`.
- `tasks.list(count=N)` counts rows, and retry sub-tasks are rows of their own: group them by `root_task_name`, read a retry's own `status` (a failed parent can have a running retry), and raise `count`, use `fetch_all=True` or say the list is partial.
- `tasks.query_logs(uuid, limit=N, sort_order="desc")` returns the last N lines in time order. A failure's cause can sit far above the tail: `tasks.diagnose(uuid_or_name=...)` collects the status message, error and warning lines and Kubernetes events, and `keyword=` searches the whole log.

## Changes

Listing and reading tasks, pods, logs, metrics, pools, quotas, images, volumes and
services needs no confirmation. Submitting, stopping, deleting, resubmitting or
reprioritizing tasks, buying or scaling resources, and changing images, volumes or
services happen only when the user asks for that change; finding why a task failed
doesn't authorize resubmitting it.

`https://skyinfer-training.siflow.cn/` is a separate training platform with its own
SSO login; this skill doesn't cover it.
