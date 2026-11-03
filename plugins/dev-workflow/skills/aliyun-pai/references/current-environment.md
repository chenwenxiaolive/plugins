# Current PAI environment

Observed on 2026-11-02 and 2026-11-03; confirm live before relying on them.

| Setting | Value |
| --- | --- |
| Region | `cn-hangzhou` |
| Workspace | `ai_lab`, ID `513442` |
| `aliyun` CLI profile | `pai-readonly` (read-only through its RAM policy and workspace role, not its name) |
| CPFS file system | `bmcpfs-0013ooqcih8196nqamf`, CPFS for Lingjun `bm_advance_400_large` |
| CPFS mount in PAI jobs | `/cpfs01` |

- `aliyun` is at `/usr/local/bin/aliyun` and `pai` at `/usr/local/bin/pai`; `pai` authenticates without a profile file.
- CloudMonitor metric calls return `403` for this profile while NAS inventory and job queries succeed; monitoring needs `cms:QueryMetricList` (for example `AliyunCloudMonitorReadOnlyAccess`).
