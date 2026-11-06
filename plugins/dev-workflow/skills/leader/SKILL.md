---
name: leader
description: "Leads a task as the coordinating agent from the project's original checkout: plans it, delegates to background Claude Code workers in worktrees through herdr-core, checks their work and verifies the integrated result. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. You stay in the project's original checkout and own
understanding, planning, splitting, integration and the final review.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md), even across several files. Give substantial or parallel work to Claude Code workers through [herdr-core](../herdr-core/SKILL.md), and a short task that changes no files, such as a diagnosis or a lookup, to a subagent (the Agent tool). For frontend work, have the worker polish layout, visuals and interactions.
- Each worker gets a directory where no other Claude Code or Codex instance runs, your checkout included. A code worker gets a worktree slot such as `/volume/worktree/<repo>/dev-1`, reused under the [worktree rules](../implement/SKILL.md#start-or-resume); prefer a free slot whose remote counterpart already has its environment, since a first build is slow. A long-running or user-addressable worker that changes no repository files, such as a deployment, also gets its own directory, such as a free slot, and its brief names the remote paths it needs instead of using them as its cwd. Invoking this skill authorizes creating worktrees, their branches and, when remote checks are needed, their remote counterparts.
- Split so that MRs don't touch the same files, new ones included: when parallel tasks may add files in one area, each brief names the new files its worker owns. A task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel. A worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- Give each worker its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two workers.

## Brief each worker

A worker reads its task, not this skill, so the launch carries everything
(herdr-core adds the report line):

```text
Goal: <objective and the context it needs>. Done when: <completion criteria>.
Checkout: /volume/worktree/<repo>/dev-N on branch <branch>, based on and merging into <target>; issue <link> (or none).
Use the implement skill and stop at ready-for-merge, with the MR's risk score recorded.
The user requested remote testing for this worktree on <cluster>, and named <node> for GPU work: use only <GPUs, or the whole node>. (Or: no GPU work; CPU-only checks run on a reachable <cluster> node with CUDA_VISIBLE_DEVICES= empty.)
Start no other agents; the `codex review` that implement runs is part of the task.
Write no memory notes; put lasting findings in your final report or the issue's execution record.
```

Always name the target branch: project docs may say `main` while this work goes
into a feature branch. Claude Code keeps memory per repository, so workers would
write into yours; record what is worth keeping yourself.

## Follow through

- Send feedback to the same worker so it keeps its context; handle its questions and blocked states with [herdr-core's follow-up guidance](../herdr-core/SKILL.md#wait-read-follow-up).
- A worker that needs the target's changes merges the target into its branch; rebasing a pushed branch would need a force-push.
- For page changes, report visual acceptance apart from functional checks: screenshot the page as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
- Merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge): on your own at a low risk score, otherwise when the user asks. Merge an MR yourself while its target hasn't moved since its review, so a worker can be closed once its MR is ready-for-merge and accepted. Each merge moves the target: recheck the next MR against it, and merge that MR through a worker in its worktree (the original, or a new one given the MR link) that runs the checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
