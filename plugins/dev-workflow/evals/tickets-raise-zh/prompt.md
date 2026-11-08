---
tags: [to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

刚才查清楚了：plugins 仓库（GitHub：chenwenxiaolive/plugins）的 `scripts/check_installation.py` 在 worktree 里运行时，会拿脚本所在的 checkout 路径去比对 lock 里记录的安装来源，而安装来源是主 checkout，所以每个 skill 都报 `lock entry is missing or has a different source`，即使文件内容、权限和链接完全一致。我们商定加一个 `--source <path>` 参数，默认仍是脚本所在的 checkout，文件比较逻辑不变。

给 plugins 提一个 issue
