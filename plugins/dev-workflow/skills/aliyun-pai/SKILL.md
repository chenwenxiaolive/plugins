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
pai --region <region> dlc job list --workspace-id <id> --all-users --since 365d --with-metadata [--status Running] [--page N] -o json \
  | jq '{pagination, jobs: [.items[] | {job_id, display_name, status, username, request_gpu, resource_name}]}'
pai --region <region> dlc job get <job-id> -o json \
  | jq '{status, reason_message, data_sources, pods: [.pods[] | {pod_id, status, node_name}], specs: [.job_specs[] | {type, pod_count, ecs_spec, image}]}'
pai --region <region> dsw instance list --workspace-id <id> --page-size 100 [--page N] -o json | jq '[.[] | {instance_id, instance_name, status, ecs_spec}]'
aliyun nas DescribeFileSystems --profile <profile> --region <region> --cli-query 'FileSystems.FileSystem[]'
pai --region <region> dlc job exec <running-job-id> [--pod <pod>] -- "df -h /cpfs01; ls -la /cpfs01/<dir>"
pai --region <region> dsw instance exec <running-instance-id> -- "df -h /cpfs01"
```

- Always project PAI JSON onto named fields as above: jobs carry environment variables, user commands, image credentials and credential configs (`envs`, `custom_envs`, `role_system_envs`, `user_command`, `image_config`, `credential_config`).
- Run these with `set -o pipefail`: `pai` reports errors on stderr, and `jq` alone would hide a failed call.
- Lists are paged: follow a job list's `pagination.next_page` while `has_more`, and fetch the next DSW `--page` while a page is full, or say the result is partial.
- Directory entries and live capacity come only from a running DLC pod or DSW instance; the APIs list file systems and filesets, and an empty fileset list doesn't mean an empty file system. Run only read-only commands there, and never create, restart or stop a task to browse storage.
- CloudMonitor returns `403` for this profile; `df` through a running target gives live capacity instead.

## Report

Keep apart job status and requested resources, file-system inventory and
configured capacity, live capacity, and directory entries actually read. Name the
job or instance used, region, workspace and path, and say when a result covers
the whole account rather than one workspace.
