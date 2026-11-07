---
name: leader
description: "Coordinates work from the project's original checkout with GPT-6-Astra leading and Opus 5.5 workers: scopes tasks, delegates through herdr-core, checks their work and verifies integration. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. You stay in the project's original checkout and own
understanding, planning, splitting, integration and the final review.

Use GPT-6-Astra (`gpt-6-astra`, `xhigh`) for the leader and Claude Opus 5.5
(`claude-opus-5-5`, `xhigh`) for implementation workers, unless the user chooses
otherwise. Instructions cannot change the current session's model: if it differs,
report that before delegation and have the leadership session switched to Astra;
do not start a second leader in the same checkout.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md), even across several files. Give substantial or parallel work to Claude Code workers through [herdr-core](../herdr-core/SKILL.md), and a short task that changes no files, such as a diagnosis or a lookup, to a subagent (the Agent tool). For frontend work, have the worker polish layout, visuals and interactions.
- Each worker gets a directory where no other Claude Code or Codex instance runs, your checkout included. A code worker gets a worktree slot such as `/volume/worktree/<repo>/dev-1`, reused under the [worktree rules](../implement/SKILL.md#start-or-resume); prefer a free slot whose remote counterpart already has its environment, since a first build is slow. A long-running or user-addressable worker that changes no repository files, such as a deployment, also gets its own directory, such as a free slot, and its brief names the remote paths it needs instead of using them as its cwd. Invoking this skill authorizes creating worktrees, their branches and, when remote checks are needed, their remote counterparts.
- Split so that MRs don't touch the same files, new ones included: when parallel tasks may add files in one area, each brief names the new files its worker owns. A task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel. A worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- Give each worker its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two workers.
- Keep project-wide discovery, architecture decisions, task selection and integration with the leader. Give a worker one coherent deliverable, the verified facts it needs and concrete starting points in the code. Necessary dependencies still belong in its scope; do not split a correctness-critical change merely to shorten a prompt.

## Brief each worker

A worker reads its task, not this skill. Build its launch from
[worker-brief.md](worker-brief.md), including the required instructions there;
herdr-core adds the report line. Send the assignment and necessary evidence,
not the leader's whole conversation or unrelated project documents. Follow
repository instructions and the issue's execution record as usual. First reads
are entry points, not a restriction on evidence needed for correctness.

Always name the target branch: project docs may say `main` while this work goes
into a feature branch. Claude Code keeps memory per repository, so workers would
write into yours; record what is worth keeping yourself.

## Follow through

- Send feedback to the same worker so it keeps its context; handle its questions and blocked states with [herdr-core's follow-up guidance](../herdr-core/SKILL.md#wait-read-follow-up).
- Check the actual model as well as the result. The owner's preference is to reduce avoidable safeguard interruptions while completing the task, not to stop on every intervention. Report a refusal or fallback, preserve the work and allow the client's automatic fallback to continue under herdr-core's guidance. Handle any remaining blocker in the leadership session or report it. Attribute work to the model that did it; do not repeatedly rephrase a blocked request. Focused briefs reduce unnecessary context, but cannot guarantee that safeguards never trigger.
- A worker that needs the target's changes merges the target into its branch; rebasing a pushed branch would need a force-push.
- For page changes, report visual acceptance apart from functional checks: screenshot the page as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
- Merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge): on your own at a low risk score, otherwise when the user asks. Merge an MR yourself while its target hasn't moved since its review, so a worker can be closed once its MR is ready-for-merge and accepted. Each merge moves the target: recheck the next MR against it, and merge that MR through a worker in its worktree (the original, or a new one given the MR link) that runs the checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
