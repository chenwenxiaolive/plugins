---
name: pr
description: "Writes a pull or merge request description with the evidence and merge risk a reviewer needs, and judges how risky an existing request is to merge. Use when opening a PR or MR, rewriting its description, or weighing whether to merge one."
---

# Pull and merge requests

One standard on both forges: `gh` on GitHub, `glab` on the internal GitLab
([access](../gpu-cluster/gitlab.md)). A description serves whoever decides to
merge. Status and ownership live in the issue's
[execution record](../implement/references/issue-ownership.md) and the rounds in
the [review-status section](../implement/references/review.md), so the body never
repeats them.

Every claim in a body is checkable from the diff or from evidence it names. Pass
a body through a file, such as `gh pr create --body-file`, rather than a shell
argument, so newlines and backticks survive.

## What a body carries

Behavior, its contract, a view of it, evidence, risk and limitations, in that order.

- Behavior: what changes for someone using the code, in the owner's words, with the issue link. A closing reference only when the request completes the issue.
- Contract: what changed in what outlives the implementation, each as old and new: a public signature, CLI flag, schema, stored format, dependency, or what an existing check expects. `None` when nothing did. The owner reads this list instead of the diff, so a contract change missing from it is a change nobody mentioned.
- A view, when a sentence cannot carry the change: the smallest one that makes the point. Behavior moving between states already owes its statechart, written under implement's [rule for `;` in labels](../implement/SKILL.md#deliver-and-review); reach gets a call or file tree, and a changed shape gets a short diff. A view that restates the prose earns nothing.
- Evidence: which checks ran, on which commit, and what they returned, with a path to the full logs instead of their contents. Each acceptance criterion has its run here, the ones the author stated marked as such, and a bug fix shows its run failing on the target commit and passing on this one. A measured number comes with the number of runs behind it, their spread and the same measurement on the target commit; a difference inside the spread is not a result. A page change adds its preview link or screenshot as the preview skill describes, and reports visual acceptance apart from the functional checks.
- Risk: the rating from [risk.md](references/risk.md) with every dimension that is not at its best, and the dimension that holds the merge when one does. If that rule cannot be read, say so instead of leaving a gap in the body.
- Limitations: what is unverified, out of scope or deferred. A reviewer should not have to find it in the diff.

## Judging a request

Read the diff against the description and the issue, not the description alone,
then rate it with [risk.md](references/risk.md). The rating decides who merges,
so reach it from what the diff and the evidence show rather than from how large
or how routine the change feels.

## Keep out

A description is not a record of the work: no plan, no history of attempts, no
apology, no narration of what was tried. Anything the reader cannot act on, or
that the execution record already holds, stays out.
