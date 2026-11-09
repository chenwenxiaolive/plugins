---
name: leader
description: "Coordinates native subagents in the project's checkout and independent workers through herdr-core, checks their work and verifies integration. Runs only when the user invokes it."
disable-model-invocation: true
---

# Leader

You are the only leader. You stay in the project's original checkout and own
understanding, planning, splitting, integration and the final review. Before
starting Herdr workers, check that you run in your own hc terminal
(`HC_TERMINAL_ID` is set); if not, ask the user to restart the leader through
Herdr.

Here, a subagent is a child agent created and managed by the current harness's
native tools. A worker is an independent interactive CLI session launched
through Herdr. Agent is the common term for both. A worker using native
cross-session messages remains a worker.

Each working directory has one independent session: the leader or a worker.
That session may create multiple native subagents in its own directory. For code
work, this boundary is the checkout/worktree root; working in its subdirectories
stays within the boundary. Never assign a subagent to another working directory
or worktree, including through a native worktree-isolation option. Work in another
directory belongs to an independent worker there, which may create its own local
subagents.

Keep the current leader's harness, model and reasoning effort. Subagents and
workers inherit those settings unless the user explicitly chooses otherwise.
A Claude Code leader starts Claude Code workers; a Codex leader starts Codex
workers. Do not switch the leader or start another leadership session to satisfy
a fixed model pairing.

## Plan and delegate

- Make small changes yourself under [implement](../implement/SKILL.md), even across several files. For scoped work in the current checkout, including code changes, prefer native subagents (Codex's `spawn_agent`, Claude Code's Agent tool). Invoking this skill authorizes that delegation. Frontend assignments include layout, visuals and interactions.
- Use [herdr-core](../herdr-core/SKILL.md) for work in another directory/worktree, an independently watchable or steerable session, or a task with its own branch/MR. An explicit request for a model in another harness, such as Opus from a Codex leader, overrides the same-harness default. Preserve that choice and use the explicit cross-harness communication route.
- Herdr workers get a directory where no other independent Claude Code or Codex session runs, your checkout included. A code worker gets a worktree slot such as `/volume/worktree/<repo>/dev-1`, reused under the [worktree rules](../implement/SKILL.md#start-or-resume); prefer a free slot whose remote counterpart already has its environment, since a first build is slow. A Herdr worker that changes no repository files, such as a deployment, also gets its own directory, such as a free slot, and its brief names the remote paths it needs instead of using them as its cwd. Invoking this skill authorizes creating worktrees, their branches and, when remote checks are needed, their remote counterparts. Native subagents stay with their parent session.
- Assign disjoint files to the leader, subagents and workers, naming new files too. Independent MRs must not touch the same files; a task that builds on another starts from that task's branch.
- Explain the split briefly, then start independent tasks in parallel. A Herdr worker grows to about 500 MB (measured 2026-11-02) and a fresh one doesn't show in `free -m` yet, so start them in batches that keep about 500 MB available.
- Give each agent its own GPUs, or a whole node when the project's validation needs one; never the same GPUs to two agents.
- Keep project-wide discovery, architecture decisions, task selection and integration with the leader. Give each agent one coherent deliverable, the verified facts it needs and concrete starting points in the code. Necessary dependencies still belong in its scope; do not split a correctness-critical change merely to shorten a prompt.

## Shared checkout

Native subagents may edit their assigned files in their parent's checkout.
No other agent, including the parent, edits those files until the assignment
returns. The independent session in that checkout, whether leader or worker,
alone stages, commits, switches branches, integrates, pushes and manages its
assigned delivery. Wait for all local writers to finish before changing HEAD or
integrating. Commit the accepted changes before validation; keep the checkout
clean and idle at that SHA until checks finish. The parent may delegate checks
on that commit and remains responsible for its implement delivery and review.

## Brief each assignment

Each delegated agent reads its task, not this skill. Build its assignment from
[delegation-brief.md](delegation-brief.md), choosing the native subagent or Herdr
worker instructions. A worker's assignment names whether it owns an MR or returns
commits for the leader's existing delivery, and includes the reply route under
[worker communication](../herdr-core/references/communication.md).
Send the assignment and necessary evidence, not the leader's whole conversation
or unrelated project documents. Follow repository instructions and the issue's
execution record as usual. First reads are entry points, not a restriction on
evidence needed for correctness.

Always name the target branch: project docs may say `main` while this work goes
into a feature branch. Claude Code keeps memory per repository, so delegated
agents would write into yours; record what is worth keeping yourself.

## Follow through

- Send feedback to the same agent so it keeps its context. For subagents, use the harness's native subagent tools. For independent workers, use [worker communication](../herdr-core/references/communication.md): `hc send` for Codex, native messaging for Claude Code. Herdr owns workers' terminals and processes.
- While agents work, continue your own work or wait through their route: native wait/result tools for subagents, [herdr-core](../herdr-core/SKILL.md#communicate-with-workers) for workers, which covers ending the turn until the next report and when a terminal needs inspection. Elapsed time or a timed-out wait is no reason to ask for progress or read a transcript. Handle the reports already in hand together, answering questions and blockers first without waiting for other agents, and send no acknowledgement-only replies. An ended turn, idle notice or exit is lifecycle status: accept work only after checking its final report, source revision and required checks.
- Check the actual model as well as the result. The owner's preference is to reduce avoidable safeguard interruptions while completing the task, not to stop on every intervention. Report a refusal or fallback, preserve the work and allow the client's automatic fallback to continue the authorized task. Handle any remaining blocker in the leadership session or report it. Attribute work to the model that did it; do not repeatedly rephrase a blocked request. Focused briefs reduce unnecessary context, but cannot guarantee that safeguards never trigger.
- A worker with its own branch that needs the target's changes merges the target into its branch; rebasing a pushed branch would need a force-push.
- For page changes, report visual acceptance apart from functional checks: screenshot the page as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
- Merge in dependency order under implement's [merge rules](../implement/SKILL.md#merge): on your own at a low risk score, otherwise when the user asks. Merge an MR yourself while its target hasn't moved since its review, so a worker can be closed once its MR is ready-for-merge and accepted. Each merge moves the target: recheck the next MR against it, and merge that MR through a worker in its worktree (the original, or a new one given the MR link) that runs the checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
