# Current SiFlow environment

Checked 2026-11-09 on the control machine; confirm these values live before relying on them.

| Setting | Value |
| --- | --- |
| Account | The user's own account in org `skyinfer` |
| Credentials | `SIFLOW_ACCESS_KEY_ID` and `SIFLOW_ACCESS_KEY_SECRET`, exported from `~/.bashrc` |
| SDK | `siflow` 0.3.27: `https://oss-cn-shanghai.siflow.cn/ai-infra-download/siflow-public/siflow-0.3.27-py3-none-any.whl`; newer wheels are in the [changelog](https://docs.siflow.cn/ai-platform/developer-access/python-sdk-changelog.md) |
| API base URL | `https://console.siflow.cn/sfapi` for every `siflow.cn` cluster; region and cluster travel as `X-Region` and `X-Cluster` headers |
| Training tasks | `cn-shanghai/changliu`, resource pools `posttrain-cpt` and `math` |

- The SDK's other `siflow.cn` clusters returned no tasks for this account: `cn-shanghai/hercules`, `cn-shanghai/shmaas`, `longmen/longmen`, `zhuoguang/zhuoguang`, `cn-wulanchabu/draco`, `taihua/taihua` and `kunlun/hydra`. `cn-beijing/auriga`, the SDK default, returns `410 cluster "auriga" has been offline since 2026-10-11`.
- The SDK's `ap-southeast`, `us-east`, `us-west` and `kunlun/crux` clusters use `scitix.ai` consoles and weren't checked.
- Constructing a client already calls `userInfo` and a domain-policy endpoint to choose between `console.siflow.cn` and `console-inner.siflow.cn`; this account gets the public URL.
- Vendor docs are also served as an MCP server at `https://docs.siflow.cn/mcp`; it isn't configured here.
