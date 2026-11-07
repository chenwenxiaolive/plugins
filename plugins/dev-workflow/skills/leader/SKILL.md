---
name: leader
description: "Coordinates native subagents in the project's checkout and independent workers through herdr-core, checks their work and verifies integration. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. You stay in the project's original checkout and own
understanding, planning, splitting, integration and the final review.

Use GPT-6-Astra (`gpt-6-astra`, `xhigh`) for the leader. Native subagents inherit
the current model and reasoning effort; Herdr implementation workers default to
Claude Opus 5.5 (`claude-opus-5-5`, `xhigh`). The user's explicit model choice
overrides these defaults. Instructions cannot change the current session's model:
if it differs from the selected leader model, report that before delegation and
have the leadership session switched; do not start a second leader in the same
checkout.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md), even across several files. For scoped work in the current checkout, including code changes, prefer native subagents (Codex's `spawn_agent`, Claude Code's Agent tool). Invoking this skill authorizes that delegation. For frontend work, have the worker polish layout, visuals and interactions.
- Use [herdr-core](../herdr-core/SKILL.md) for an independently watchable or steerable session, a task with its own branch/MR, or a requested model unavailable to native subagents, such as Opus from a Codex leader. Preserve an explicit model choice when selecting the worker mechanism.
- Herdr workers get a directory where no other Claude Code or Codex instance runs, your checkout included. A code worker gets a worktree slot such as `/volume/worktree/<repo>/dev-1`, reused under the [worktree rules](../implement/SKILL.md#start-or-resume); prefer a free slot whose remote counterpart already has its environment, since a first build is slow. A Herdr worker that changes no repository files, such as a deployment, also gets its own directory, such as a free slot, and its brief names the remote paths it needs instead of using them as its cwd. Invoking this skill authorizes creating worktrees, their branches and, when remote checks are needed, their remote counterparts; native subagents need no new worktree.
- Assign disjoint files to the leader and workers, naming new files too. Independent MRs must not touch the same files; a task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel. A Herdr worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- Give each worker its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two workers.
- Keep project-wide discovery, architecture decisions, task selection and integration with the leader. Give a worker one coherent deliverable, the verified facts it needs and concrete starting points in the code. Necessary dependencies still belong in its scope; do not split a correctness-critical change merely to shorten a prompt.

## Shared checkout

Native subagents may edit their assigned files in the leader's checkout. No other
agent, including the leader, edits those files until the assignment returns.
The leader alone stages, commits, switches branches, integrates, pushes and
manages the MR. Wait for all writers to finish before changing HEAD or integrating.
Commit the accepted changes before validation; keep the validation checkout clean
and idle at that SHA until checks finish. The leader may delegate checks on that
commit and remains responsible for the full implement delivery and review.

## Brief each worker

A worker reads its task, not this skill. Build its launch from
[worker-brief.md](worker-brief.md), choosing its shared-checkout or Herdr
instructions. A Herdr assignment names whether it owns an MR or returns commits
for the leader's existing delivery; herdr-core adds its report line. Send the
assignment and necessary evidence, not the leader's whole conversation or
unrelated project documents. Follow
repository instructions and the issue's execution record as usual. First reads
are entry points, not a restriction on evidence needed for correctness.

Always name the target branch: project docs may say `main` while this work goes
into a feature branch. Claude Code keeps memory per repository, so workers would
write into yours; record what is worth keeping yourself.

## Follow through

- Send feedback to the same worker so it keeps its context: use the native subagent tools, or [herdr-core's follow-up guidance](../herdr-core/SKILL.md#wait-read-follow-up) for Herdr workers.
- Check the actual model as well as the result. The owner's preference is to reduce avoidable safeguard interruptions while completing the task, not to stop on every intervention. Report a refusal or fallback, preserve the work and allow the client's automatic fallback to continue under herdr-core's guidance. Handle any remaining blocker in the leadership session or report it. Attribute work to the model that did it; do not repeatedly rephrase a blocked request. Focused briefs reduce unnecessary context, but cannot guarantee that safeguards never trigger.
- A worker with its own branch that needs the target's changes merges the target into its branch; rebasing a pushed branch would need a force-push.
- For page changes, report visual acceptance apart from functional checks: screenshot the page as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
- Merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge): on your own at a low risk score, otherwise when the user asks. Merge an MR yourself while its target hasn't moved since its review, so a worker can be closed once its MR is ready-for-merge and accepted. Each merge moves the target: recheck the next MR against it, and merge that MR through a worker in its worktree (the original, or a new one given the MR link) that runs the checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
