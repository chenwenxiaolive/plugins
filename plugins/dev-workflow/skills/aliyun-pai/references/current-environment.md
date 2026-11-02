# Current PAI environment

These values were observed on 2026-11-02. Confirm them live before relying on
them.

| Setting | Value |
| --- | --- |
| Region | `cn-hangzhou` |
| Workspace | `ai_lab`, ID `513442` |
| Alibaba Cloud CLI profile | `pai-readonly` |
| CPFS file system | `bmcpfs-0013ooqcih8196nqamf` |
| CPFS type | CPFS for Lingjun, `bm_advance_400_large` |
| CPFS mount in PAI jobs | `/cpfs01` |

The job observed during setup, `dlcg1o7wr4c98522`, completed successfully at
`2026-11-02T04:31:46Z`. It cannot be used for live mounted-filesystem access;
select a DLC pod or DSW instance whose current status is `Running`.

The control machine has the official `aliyun` CLI at `/usr/local/bin/aliyun`.
Install PAI CLI at `/usr/local/bin/pai` if it is absent. The `pai-readonly`
profile is only a local profile name; enforce read-only access through the RAM
policy and PAI workspace role.

The command below discovered the existing DLC job and then read its mounts and
filesystem statistics without altering the job:

```bash
python3 scripts/pai_inspect.py jobs --workspace-id 513442
python3 scripts/pai_inspect.py mounts <running-dlc-job-id>
python3 scripts/pai_inspect.py stat <running-dlc-job-id> /cpfs01
python3 scripts/pai_inspect.py ls <running-dlc-job-id> /cpfs01
```

CloudMonitor metric calls for this profile returned `403` even though NAS
inventory and task queries succeeded. Grant `AliyunCloudMonitorReadOnlyAccess`
or an equivalent custom policy that allows `cms:QueryMetricList` before relying
on monitoring APIs; use `statvfs` through a running target as an independent
capacity check.
