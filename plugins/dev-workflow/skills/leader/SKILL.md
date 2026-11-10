---
name: leader
description: "Launches self-contained native subagents and independent Herdr workers, reviews their final results and verifies integration. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. Stay in the original checkout and own understanding,
splitting, launch, integration and review. Before Herdr work, check for your own
hc terminal (`HC_TERMINAL_ID`); otherwise ask the user to restart through Herdr.

Delegation is one-shot. Give each agent a complete brief, launch it, then collect
one final report. Do not exchange readiness, progress, milestone or
acknowledgement messages. Only a blocked worker or one late correctness fact
gets a single message before it continues.

A subagent is a native child; a worker is an independent CLI session. One
session/checkout may have native children. Another directory needs a worker
there; never move a subagent, including through native worktree isolation.

Keep the current leader's harness, model and reasoning effort. Subagents and
workers inherit those settings unless the user explicitly chooses otherwise.
A Claude Code leader starts Claude Code workers; a Codex leader starts Codex
workers. Do not switch the leader or start another leadership session to satisfy
a fixed model pairing.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md). For scoped work in the current checkout, including code and frontend work, use a native subagent. Use [herdr-core](../herdr-core/SKILL.md) only for another directory/worktree, a task with its own branch/MR, or a watchable/steerable session. An explicit different-harness model overrides the default and uses the cross-harness route.
- A Herdr worker gets a directory with no other independent session, normally a free worktree slot under the [worktree rules](../implement/SKILL.md#start-or-resume) with its remote environment already prepared. A worker that changes no files gets such a directory too and is given the remote paths instead of using them as cwd. This skill authorizes worktrees, branches and needed remote counterparts.
- Assign disjoint files to the leader, subagents and workers, naming new files too. Independent MRs must not touch the same files; a task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel. A Herdr worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- Give each agent its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two agents.
- Keep project-wide discovery, architecture, task selection and integration. Give each agent one coherent deliverable, necessary facts and code entry points; dependencies stay in scope. Do not split a correctness-critical change just to shorten a prompt.

## Shared checkout

Native subagents may edit their assigned files in their parent's checkout.
No other agent edits those files until the assignment returns. The independent
session alone handles Git and delivery. Wait for all writers before changing
HEAD, then commit before validation and keep the SHA untouched while checks run.
The parent runs checks or starts a fresh validation subagent, and owns review.

## Brief each assignment

Each delegated agent reads its task, not this skill. Build its assignment from
[delegation-brief.md](delegation-brief.md), choosing the native subagent or Herdr
worker instructions. A worker's assignment names whether it owns an MR or returns
commits for the leader's existing delivery, and includes the reply route under
[worker communication](../herdr-core/references/communication.md).
Send the assignment and necessary evidence, not the whole conversation or
unrelated documents. Always name the target branch because docs may say `main`
while work goes elsewhere. First reads are entry points, not a context limit.
Claude Code memory is per repository, so delegated agents write into yours;
record what is worth keeping yourself.

## Collect and review

- After launching all independent work, continue your own work or end the turn. Collect native subagents with their result/wait tool and let an independent worker's report start the next turn. Do not poll progress or send receipts.
- On a final report, inspect the source, commit/MR and checks before accepting. A blocked report names what it needs; answer once from the plan and existing authorization, or ask the user. Then let it finish.
- A failed review gets one concrete correction to the same agent or a small fix by the leader. Do not narrate review.
- Check the actual model. Preserve work and let an automatic model fallback continue the task; attribute work to the model that did it, and do not repeatedly rephrase a refusal. Focused briefs reduce context but cannot prevent safeguards.
- A worker with its own branch that needs the target's changes merges the target into its branch; rebasing a pushed branch would need a force-push.
- For a page, report visual acceptance apart from functional checks: take the preview screenshot or give the user the preview link and say visual acceptance is pending.
- Merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge), on your own at low risk or when asked. Recheck each remaining MR after the target moves and run integrated checks in its worker before merging.
