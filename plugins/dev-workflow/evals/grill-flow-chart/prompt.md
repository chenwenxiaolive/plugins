---
tags: [grilling]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Let's wrap up the grilling on GPU job retries; no MR yet. We agreed: a submitted job waits in the queue until a node with free GPUs takes it. If its node fails while it runs, it goes back to the queue, at most twice; the third node failure marks it failed. I can cancel a job while it is queued or running. A job that exits 0 is done; any other exit code marks it failed without a retry. Summarize where we landed.
