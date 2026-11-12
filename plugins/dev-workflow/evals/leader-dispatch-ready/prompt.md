---
tags: [leader, herdr-core]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader This session is hc terminal t50 and is dispatching the agreed plan for
RFC #120 in /volume/workspace/launcher. Every issue targets the integration
branch integration/config-schema, and a dependent issue starts once its
prerequisites' MRs are merged into that branch. #121 and #124 are independent
and their Claude Code workers are running; #122 and #123 each depend only on
#121. CPU checks on sh-gate are authorized, no GPUs, and memory is enough for
two more workers. This just arrived:

<hc from="t51 issue-121">#121 merged: MR !130 into integration/config-schema at 4f2a9c1</hc>

What do you do now? You have no shell here, so describe each step and command
instead of running it.
