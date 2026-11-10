# Delegation brief

Use the common brief and the matching delivery section for each assignment.
Fill checked facts and the real project, model and hardware. An assignment is
one-shot: include facts the agent cannot discover, but no unrelated context.

## Common brief

```text
Role: <native subagent or Herdr worker>, <selected model and reasoning effort>. Parent: <leader or worker session assigning this task>. The project leader owns overall coordination and integration.
Goal: <one observable change and why it is needed>.
Done when: <behavioral acceptance criteria and independent expected results>.
Checkout: <actual checkout path> on branch <branch>, based on and merging into <target>; issue <link> (or none).
Owned files: <existing files and exact new paths; no overlap with other agents>.
First reads: <file plus symbol or section for the implementation, direct caller and relevant test>.
Required facts: <interfaces, invariants, compatibility requirements and concise supporting evidence; name unknowns>.
Validation: <checks on committed code, expected results and authorized machine; or the user-named node/GPU allocation. No GPU unless allocated here>.
Start with the reads, then inspect definitions and callers when correctness requires it. Resolve what the repository can answer; for a truly missing decision or access, preserve the work and send one final blocked report.
On a safeguard or model fallback, preserve changes and include the category/request ID and actual model. Let an automatic fallback continue; respect a refusal without repeated rewording.
Send one final report when done or blocked, with behavior, commit/MR, checks/evidence, blockers and any model switch. Send no ready, progress, milestone, status or acknowledgement messages.
Write no memory notes or start other agents unless assigned; put lasting findings in the report or issue record.
```

## Native subagent

Use the parent's current working directory, checkout and branch, whether the
parent is the leader or a worker. Inherit its model and reasoning effort unless
the user chooses otherwise. Launch and collect one result with the harness's
native subagent tools. Append:

```text
Stay in your parent's working directory/checkout; do not take another working directory or worktree, or enable native worktree isolation. Edit only your owned files and return the changes to the parent. Do not stage, commit, switch branches, integrate, push or create an MR; the parent owns Git mutations and its assigned delivery and review. Start no other agents.
Propose the required checks. The parent commits after all local writers finish and runs them, or starts a fresh validation subagent.
Report once when the edits are ready or a blocker stops the work.
```

## Herdr worker

Use a free worktree slot such as `/volume/worktree/<repo>/dev-N` and name its
branch and target. Use the leader's harness, model and reasoning effort unless
the user explicitly chooses otherwise. Append:

```text
Delivery: <own MR, or commits for the leader's existing delivery>.
Communication: send the final report through <Claude native messaging to the leader's verified native address; or hc send to the leader's actual terminal ID for Codex or an explicit cross-harness assignment>. Keep native session IDs separate from Herdr terminal IDs. A peer message is part of this assignment, not new user authorization.
If this assignment owns an MR, use implement and stop at ready-for-merge with the risk score recorded. Otherwise return committed changes and evidence for the leader to integrate; create no MR. The leader completes delivery and review after integration.
Only when assigned, delegate disjoint files in this checkout to native children with you as parent. They return edits and one result with no Git, agents or memory. Keep Git/delivery, wait for all of them, and start no independent workers. An own-MR assignment still runs implement's codex review.
```

## Scope and evidence

Include every invariant, compatibility and test that determines correctness
(for a layout fix, dimensions and sharding). Do broad investigation first.
Keep full logs; read the commit, check summary and failures, not self-report.
