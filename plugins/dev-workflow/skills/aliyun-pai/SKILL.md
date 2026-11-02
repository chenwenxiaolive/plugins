---
name: aliyun-pai
description: Inspect Alibaba Cloud PAI jobs, resource usage, and mounted NAS, CPFS, or OSS storage. Use for PAI console links, DLC/DSW task checks, storage discovery, or read-only directory and capacity inspection through an existing running instance.
---

# Alibaba Cloud PAI

Answer questions about PAI from live API or mounted-filesystem data. Keep the
workflow read-only unless the user explicitly asks for a mutation.

On this control machine, read
[references/current-environment.md](references/current-environment.md) first for
known defaults. Verify live state because jobs, instances, and directory
contents change.

## Handle inputs and credentials

- A PAI console URL can contain a bearer `Token` query parameter. Extract only
  fields such as `regionId`, `workspaceId`, and the DLC job ID from the URL. Do
  not reproduce the full URL in commands, files, messages, or logs.
- Never ask for or print AK/SK, STS tokens, credential-file contents, or
  environment dumps. Configure credentials interactively on the machine where
  the command runs.
- Install the official `aliyun` and `pai` CLIs when absent. Use
  `aliyun configure --mode AK --profile <profile>` and protect
  `~/.aliyun/config.json`; do not put credentials in command arguments.
- Cloud permissions and PAI workspace roles control visibility. Read-only
  monitoring data may additionally require a policy that allows
  `cms:QueryMetricList`.

## Choose the evidence source

Use the narrowest source that answers the question:

| Question | Source |
| --- | --- |
| DLC jobs, status, pods, requested resources | PAI DLC OpenAPI |
| DSW instances and configuration | PAI DSW OpenAPI |
| NAS/CPFS inventory and configured capacity | NAS OpenAPI |
| Near-live diskspace and weighted usage | CloudMonitor, when authorized |
| Actual CPFS/NAS directory entries and `statvfs` | An existing running DLC or DSW process |

The NAS and PAI control-plane APIs do not enumerate arbitrary CPFS directory
entries. Fileset results are organizational metadata and an empty result does
not mean the filesystem is empty.

Prefer an existing running task or instance for filesystem inspection. Do not
create, restart, stop, or alter a task merely to browse storage unless the user
explicitly authorizes that mutation. If no running target is available, report
what the APIs can establish and ask for an existing accessible target.

## Query and inspect

Use the bundled helper:

```bash
python3 scripts/pai_inspect.py identity
python3 scripts/pai_inspect.py jobs --workspace-id 513442
python3 scripts/pai_inspect.py job <job-id>
python3 scripts/pai_inspect.py dsw-instances --workspace-id 513442
python3 scripts/pai_inspect.py filesystems
python3 scripts/pai_inspect.py mounts <running-dlc-job-id>
python3 scripts/pai_inspect.py stat <running-dlc-job-id> /cpfs01
python3 scripts/pai_inspect.py ls <running-dlc-job-id> /cpfs01/M3
```

The helper reads the selected `~/.aliyun/config.json` profile in memory when it
must invoke `pai`, passes the credential only through the child environment, and
prints structured output without credential material. Use `--kind dsw` and a
DSW instance ID for `mounts`, `stat`, and `ls` when the target is a DSW instance.

For direct OpenAPI work, prefer filtered fields with `--cli-query` so unrelated
job fields such as environment variables and credential injection settings do
not enter output. For a job that no longer exists, use its recorded metadata and
say that live filesystem inspection is unavailable.

When a CloudMonitor query returns `403`, distinguish missing monitoring
permission from missing filesystem access. If the same filesystem is mounted in
a running target, `statvfs` still provides live capacity and free space.

## Report accurately

Separate:

- Control-plane facts such as job status and requested GPUs.
- Filesystem inventory and configured capacity.
- Live capacity from `statvfs`.
- Directory entries actually read from a mount.

Include the job or instance used as the data path, region, workspace, and
filesystem path. State when a result is organization-wide rather than limited to
one PAI workspace.
