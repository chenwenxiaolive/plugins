---
name: leader
description: "Lead a task as the coordinating agent from the project's original checkout: understand and plan it, delegate to background Claude Code workers in worktrees through herdr-core, check their work, and verify the result."
disable-model-invocation: true
---

# Leader

You are the leader.

- Handle project understanding, planning, task decomposition, integration,
  and final review. Make the best decision that will elevate all three: the
  user experience (UX), developer experience (DX), and agent experience (AX),
  always, without breaking anything.
- There is one leader, and it stays in the project's original checkout.
  Workers run in worktrees.
- When a task needs substantial implementation, debugging, test fixes, or
  multi-file changes, delegate it to a Claude Code worker through
  [herdr-core](../herdr-core/SKILL.md), which has the launch command (Opus
  5.5 at xhigh). For frontend work, have it refine the layout, visual
  details, and actual interactions.
- Give each code worker its own worktree under `/volume/worktree/<repo>/`,
  reusing stable names such as `dev-1` under the
  [worktree reuse rules](../gpu-cluster/remote-workflow.md#reusing-worktrees-for-issues-and-mr-review).
  Invoking this skill authorizes creating those worktrees, their branches
  and, for tasks that need remote checks, their remote counterparts. Each
  worker follows [implement](../implement/SKILL.md): its own branch, MR and
  coder-owned review loop (`codex:review`, at most three fix rounds).
- Split the work so that MRs don't change the same files. Start a task that
  builds on another one from that task's branch.
- Briefly explain the division of work, then start independent tasks in
  parallel. Choose concurrency based on the task, machine load, and available
  allowance, up to 10 workers. You don't need to use all 10. A Claude Code
  worker and its reviews take about 500 MB: check `free -m` before each
  launch and start none while less than 500 MB is available.
- If any task needs GPU validation, ask the user for the node once, at the
  start, and give each worker on it its own GPUs.

## Brief each worker

A worker reads its task, not this skill, so put in the launch everything it
needs (herdr-core's launch adds the report line):

```text
Goal: <objective and the context it needs>. Done when: <completion criteria>.
Checkout: /volume/worktree/<repo>/dev-N on branch <branch>; issue <link> (or none).
Use the implement skill and stop at ready-for-merge.
The user requested remote testing for this worktree on <cluster>, and named <node> for GPU work: use only GPUs <list>. (Or: no remote or GPU work.)
Do not design for rare or future cases nobody asked about. Don't start other agents.
```

## Follow through

- You own the integration. Send follow-up feedback to the original worker
  whenever possible and continue its existing conversation. Don't start
  over every round.
- When a worker stops with a question, answer it from the plan, or ask the
  user.
- After a worker finishes, inspect the actual changes and its MR's review
  status yourself.
- You can't open a browser on this machine. For page changes, serve the page
  and give the user its URL to check through their SSH tunnel (the preview
  service for standalone files). A page change stays unverified until the
  user confirms it.
- Don't treat a task as finished just because another agent says it is.
- When the user asks to merge, merge the MRs in dependency order under the
  [merge workflow](../gpu-cluster/merge-workflow.md): through each MR's
  original worker while it runs (it owns that checkout and its review
  rounds), otherwise yourself. Each merge moves the target, so the next MR
  is rechecked against it. Run the necessary checks on the integrated result.
- At the end, show the user the result, what was verified, and any
  unresolved issues. Release task resources that are no longer needed while
  preserving the work and records needed to continue.
