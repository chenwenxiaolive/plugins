---
tags: [implement]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

My branch for issue #57 changes the GPU job scheduler. Before, a node failure while a job ran marked the job failed, and a queued job couldn't be cancelled. Now a node failure sends the job back to the queue, at most twice, and the third failure marks it failed; cancelling works while the job is queued as well as while it runs. Exit codes are handled as before: 0 is done, anything else is failed. The scheduler tests pass at commit 4f2c9e1. Draft the MR description for me to paste.
