---
name: leader
description: "Leads a task as the coordinating agent from the project's original checkout: plans it, delegates to background Claude Code workers in worktrees through herdr-core, checks their work and verifies the integrated result. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. You stay in the project's original checkout and own
understanding, planning, splitting, integration and the final review.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md), even across several files. Give substantial, investigative or parallel work to Claude Code workers through [herdr-core](../herdr-core/SKILL.md) (its launch command uses Opus 5.5 at xhigh). For frontend work, have the worker polish layout, visuals and interactions.
- Each code worker gets its own worktree slot such as `/volume/worktree/<repo>/dev-1`, reused under the [worktree rules](../implement/SKILL.md#start-or-resume). Prefer a free slot whose remote counterpart already has its environment, since a first build is slow. Invoking this skill authorizes creating worktrees, their branches and, when remote checks are needed, their remote counterparts.
- Split so that MRs don't touch the same files. A task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel, up to 10. This machine has 4 GiB: a worker grows to about 500 MB and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- GPU work reuses the user's active node allocation; ask only when it is missing or must change. Give each worker its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two workers.

## Brief each worker

A worker reads its task, not this skill, so the launch carries everything
(herdr-core adds the report line):

```text
Goal: <objective and the context it needs>. Done when: <completion criteria>.
Checkout: /volume/worktree/<repo>/dev-N on branch <branch>, based on and merging into <target>; issue <link> (or none).
Use the implement skill and stop at ready-for-merge.
The user requested remote testing for this worktree on <cluster>, and named <node> for GPU work: use only <GPUs, or the whole node>. (Or: no GPU work; CPU-only checks run on a reachable <cluster> node with CUDA_VISIBLE_DEVICES= empty.)
Start no other agents; the `codex review` that implement runs is part of the task.
```

Always name the target branch: project docs may say `main` while this work goes
into a feature branch.

## Follow through

- Send feedback to the same worker so it keeps its context; handle its questions and blocked states with [herdr-core's follow-up guidance](../herdr-core/SKILL.md#wait-read-follow-up).
- A worker's "done" is a claim: inspect its changes and its MR's review status yourself.
- For page changes, report visual acceptance apart from functional checks: screenshot the page as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
- When the user asks to merge, merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge-only-when-the-user-asks). Your own work merges from its checkout; a delegated MR merges through a worker in its worktree (the original, or a new one given the MR link and the merge request). Each merge moves the target, so recheck the next MR against it and run the checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
- At the end, report the result, what was verified and what is unresolved. Stop finished task processes, and keep the worktrees and the records needed to continue.
