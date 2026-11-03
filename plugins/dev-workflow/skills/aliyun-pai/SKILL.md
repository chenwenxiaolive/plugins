---
name: aliyun-pai
description: Inspect Alibaba Cloud PAI jobs, resource usage, and mounted NAS, CPFS, or OSS storage. Use for PAI console links, DLC/DSW task checks, storage discovery, or read-only directory and capacity inspection through an existing running instance.
---

# Alibaba Cloud PAI

Answer PAI questions from live data, read-only unless the user asks for a change.
[references/current-environment.md](references/current-environment.md) has this
machine's region, workspace, profile and file system.

## Credentials

- A PAI console URL can carry a bearer `Token`. Take only `regionId`, `workspaceId` and the job ID from it; never repeat the URL.
- The `pai` and `aliyun` CLIs already authenticate here. Never print credentials or `pai config show`. If one fails to authenticate, ask the user to set it up interactively (`! pai config init`, `! aliyun configure --profile <profile>`).

## Commands

```bash
pai --region <region> dlc job list --workspace-id <id> --all-users [--status Running] -o json 2>/dev/null
pai --region <region> dlc job get <job-id> -o json | jq '{status, reason_message, job_specs, data_sources, pods}'   # never the envs or credential_config fields
pai --region <region> dsw instance list -o json
aliyun nas DescribeFileSystems --profile <profile> --region <region> --cli-query 'FileSystems.FileSystem[]'
pai --region <region> dlc job exec <running-job-id> [--pod <pod>] -- "df -h /cpfs01; ls -la /cpfs01/<dir>"
pai --region <region> dsw instance exec <running-instance-id> -- "df -h /cpfs01"
```

- Directory entries and live capacity come only from a running DLC pod or DSW instance; the APIs list file systems and filesets, and an empty fileset list doesn't mean an empty file system. Run only read-only commands there, and never create, restart or stop a task to browse storage.
- CloudMonitor returns `403` for this profile; `df` through a running target gives live capacity instead.

## Report

Keep apart job status and requested resources, file-system inventory and
configured capacity, live capacity, and directory entries actually read. Name the
job or instance used, region, workspace and path, and say when a result covers
the whole account rather than one workspace.
