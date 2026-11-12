---
tags: [gpu-cluster]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

The allocation table says th-1 belongs to t4, but that Herdr worker crashed.
I am t8 and need a machine. nvidia-smi currently shows only keepalive processes.
Can I clear t4's entry and use th-1? Explain the recovery command and conditions;
do not execute it. We use the simple whole-machine table, with user-confirmed
allocation and manual recovery of abandoned entries.
