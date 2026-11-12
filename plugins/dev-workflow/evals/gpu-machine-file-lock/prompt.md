---
tags: [gpu-cluster]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm Herdr worker t8 on the control machine. In the shared allocation directory,
there is a `.lock` file and a `sh-1` file containing `t7`. Nobody currently holds
the flock. There is no `sh-2` file. Which machine is registered to a worker, and
what must I do before using sh-2? When returning a machine, should I delete the
`.lock` file too? Explain the commands without executing them.
