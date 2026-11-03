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
- Decide whether to delegate by the amount of work, task independence and
  benefit from parallel execution. Handle small, straightforward changes
  directly in the selected checkout under [implement](../implement/SKILL.md),
  even when they touch several files. Delegate substantial implementation,
  investigation or independent parallel tasks to a Claude Code worker through
  [herdr-core](../herdr-core/SKILL.md), which has the launch command (Opus
  5.5 at xhigh). For frontend work, have it refine the layout, visual
  details, and actual interactions.
- Give each code worker its own worktree under `/volume/worktree/<repo>/`.
  Reuse fixed slots such as `dev-1` under the
  [worktree reuse rules](../gpu-cluster/remote-workflow.md#reusing-worktrees-for-issues-and-mr-review),
  preferring a free one whose remote counterpart already has its
  environment: a new counterpart's first environment build can be slow.
  Invoking this skill authorizes creating those worktrees, their branches
  and, for tasks that need remote checks, their remote counterparts. Each
  worker follows [implement](../implement/SKILL.md) through its own branch,
  MR and coder-owned review.
- Split the work so that MRs don't change the same files. Start a task that
  builds on another one from that task's branch.
- Briefly explain the division of work, then start independent tasks in
  parallel. Choose concurrency based on the task, machine load, and available
  allowance, up to 10 workers. You don't need to use all 10. A Claude Code
  worker and its reviews grow to about 500 MB, and one just started doesn't
  show in `free -m` yet: size each batch before starting it, at most
  (available MB − 500) / 500 workers, and check `free -m` again before the
  next batch.
- If any task needs GPU validation, reuse the user's active session allocation.
  Ask only if the required allocation is missing or needs to change. Give each
  worker its own GPUs, or a whole node when the project's
  validation needs one (mini-vllm's validation profile does). Never give two
  workers the same GPUs.

## Brief each worker

A worker reads its task, not this skill, so put in the launch everything it
needs (herdr-core's launch adds the report line):

```text
Goal: <objective and the context it needs>. Done when: <completion criteria>.
Checkout: /volume/worktree/<repo>/dev-N on branch <branch>, based on and merging into <target>; issue <link> (or none).
Use the implement skill and stop at ready-for-merge.
The user requested remote testing for this worktree on <cluster>, and named <node> for GPU work: use only <GPUs, or the whole node>. (Or: no remote or GPU work.)
Do not design for rare or future cases nobody asked about. Start no other agents beyond the codex:review that implement requires.
```

Name the target even when it is the default branch: project docs may say
`main` while this work goes into a feature branch.

## Follow through

- You own the integration. Send follow-up feedback to the original worker
  whenever possible and continue its existing conversation. Don't start
  over every round.
- Handle worker questions and blocked states using
  [herdr-core's follow-up guidance](../herdr-core/SKILL.md#wait-read-follow-up).
- After a worker finishes, inspect the actual changes and its MR's review
  status yourself.
- For page changes, report functional checks and visual acceptance separately,
  with the evidence and remaining gaps for each. Use available browser tooling
  when appropriate; when user inspection is needed, serve the page and give
  its URL through their SSH tunnel (the preview service for standalone files).
  Without visual evidence, report "functional checks passed; visual acceptance
  pending" only if those checks actually passed. Do not present functional
  checks as visual acceptance. A pending visual check does not invalidate
  completed functional checks; required acceptance criteria still apply.
- Don't treat a task as finished just because another agent says it is.
- When the user asks to merge, merge the MRs in dependency order under the
  [merge workflow](../gpu-cluster/merge-workflow.md). For work you implemented
  directly, use its selected checkout and reviewed branch. For delegated work,
  merge through a worker in that MR's worktree: its original worker, or, if
  that one was closed, a new worker told the MR link and that the user asked
  to merge it. Don't review a delegated MR from your own branch. Each merge
  moves the target, so the next MR is rechecked
  against it. Run the necessary checks on the integrated result. Work merged
  into a feature branch is not on the default branch yet: open that
  branch's MR into it, and merge it when the user asks.
- At the end, show the user the result, what was verified, and any
  unresolved issues. Clean up unneeded task processes while preserving the
  work and records needed to continue. Retain local and remote worktrees;
  remove them only when the user explicitly asks, under the
  [worktree retention rules](../gpu-cluster/remote-workflow.md#reusing-worktrees-for-issues-and-mr-review).
