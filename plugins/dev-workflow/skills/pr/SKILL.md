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

Behavior, a view of it, evidence, risk and limitations, in that order.

- Behavior: what changes for someone using the code, in the owner's words, with the issue link. A closing reference only when the request completes the issue.
- A view, when a sentence cannot carry the change: the smallest one that makes the point. Behavior moving between states already owes its statechart, written under implement's [rule for `;` in labels](../implement/SKILL.md#deliver-and-review); reach gets a call or file tree, and a changed shape gets a short diff. A view that restates the prose earns nothing.
- Evidence: which checks ran, on which commit, and what they returned, with a path to the full logs instead of their contents. A page change adds its preview link or screenshot as the preview skill describes, and reports visual acceptance apart from the functional checks.
- Risk: the score and the reasons behind it from implement's [merge rules](../implement/references/merge.md), with whatever [risk.md](references/risk.md) finds that the score does not see.
- Limitations: what is unverified, out of scope or deferred. A reviewer should not have to find it in the diff.

## Judging a request

Read the diff against the description and the issue, not the description alone.
Score it, then work through [risk.md](references/risk.md). A one-way door, or a
diff that does more than its description, keeps the merge with the user even at
a score implement would otherwise let you merge yourself.

## Keep out

A description is not a record of the work: no plan, no history of attempts, no
apology, no narration of what was tried. Anything the reader cannot act on, or
that the execution record already holds, stays out.
