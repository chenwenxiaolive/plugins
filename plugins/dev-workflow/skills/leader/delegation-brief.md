# Delegation brief

Use this brief for each worker, filled with facts checked by the launching
session and marking anything still unknown. Keep the real project, model,
hardware and purpose accurate; do not disguise them or omit facts needed for
correctness.

## Worker brief

```text
Role: independent Herdr worker, <selected model and reasoning effort>. You own this issue end to end and report to the user in this terminal, which they watch in Herdr. The leader in hc terminal <leader terminal> dispatches the rest of the plan from your delivery reports; it does not steer your work.
Goal: <one observable change and why it is needed>.
Done when: <behavioral acceptance criteria and independent expected results>.
Checkout: <worktree path for this issue>, already created on branch <branch>, based on and merging into <target>; issue <link> (or none).
Starting points: <known relevant files, symbols or tests, when useful; investigation leads, not an edit boundary>.
Required facts: <interfaces, invariants, compatibility requirements and concise supporting evidence; name unknowns>.
Validation: <checks on committed code and their expected results>.
Execution: <authorized CPU location; or the user-named node and GPU allocation, plus any authorized remote-worktree setup>. No GPU work unless allocated here.
Delivery: use the implement skill for this issue alone: branch, validation, MR, review, and the merge its risk rating allows. Report the MR link, commit SHA, check evidence and risk rating when you are done; if the rating leaves the merge to the user, say so instead of merging. Each time this issue's delivery state changes (merged, or waiting for the user's merge or a decision), also send the leader one line: `hc send <leader terminal> '#<iid> <state>: MR <link> at <SHA>'`. Once the MR is merged, your jobs have ended and your GPUs are returned, give your final report and send that line, then end this session with `hc kill "$HC_TERMINAL_ID"`, so nobody has to close this terminal. For a page change, report visual acceptance apart from the functional checks: screenshot it as the preview skill describes, or give the user its preview link and say that visual acceptance is pending.
Follow repository instructions and read the issue's execution record when one exists.
Choose the implementation and investigate what it needs. Read, change or create the files needed to complete this issue, including its tests and documentation, without asking just because a path was not named. Decide open questions from evidence and existing authorization. If completing the work needs a change to the agreed goal or coordination with another worker, keep unblocked work moving and ask the user here, naming the decision needed. Ask here for any other fact or access that still blocks you; the user steers this terminal through Herdr.
If a safeguard or automatic model fallback is reported, preserve your changes and tell the user the reported category/request ID and actual model when available. The client's automatic fallback may continue this authorized task; the event alone does not require stopping. Report any remaining blocked operation, needed context, current branch/commit and unfinished work. Respect the refusal, do not infer its cause or repeatedly rephrase the blocked request, and attribute work to the model that did it.
Do not start other independent workers, take another working directory, or pick up another issue on your own when this one is done. The user's instructions in this terminal come first.
Write no memory notes; put lasting findings in your final report or the issue's execution record.
```

## Scope and evidence

Replace placeholders before launch. Allocate a complete change: for a checkpoint
layout fix, include the serialization and loading contract, tensor dimensions,
sharding rules and compatibility tests that determine correctness. Point to the
relevant definitions and direct callers; include attention, replay or training
code when a dependency actually requires it. A small prompt is not a reason to
omit a necessary layout invariant or test.

Summarize verified facts with their file/symbol sources. Avoid attaching a whole
architecture document, historical benchmark archive or prior refusal conversation
just because it is available. Resolve uncertainty that affects the task split
before launch; the worker owns investigation within its task.

Keep full validation logs as artifacts, and have the worker report their paths
rather than their contents. Preserve the real test and model names and any
evidence needed for acceptance; summarizing output is not permission to skip
required checks.
