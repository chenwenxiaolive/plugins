# MR review

## Coder-owned review after opening an MR

The coder owns implementation, MR creation, review and fixes in the selected
development worktree, on the MR's existing development branch. Run this workflow
as part of the implementation task, without a separate reviewer role, review
worktree, notification or polling step.

1. Complete the implementation, commit and push it, run the required checks on the committed code, and open the MR. Read the issue/spec and project standards. Fetch and record the MR source SHA, target SHA and merge-base; verify that the clean local HEAD is the MR source commit. Review the entire MR diff against that baseline, even when the working tree is clean.
2. Run the initial review, recording it as round 0. For this pass and every re-review, assess requirement acceptance as described below and run the code review from either client with `codex review --base <target-sha> > <run_dir>/review-<round>.md 2> <run_dir>/review-<round>.log` in the clean checkout at the MR source commit. It starts a fresh Codex process with the configured model, reads the project instructions and diff, and prints its findings on stdout; the transcript goes to stderr. It takes minutes, so run it in the background or with a long timeout and wait for it to exit.
3. If changes are needed, perform at most **three corrective rounds, numbered 1, 2 and 3**. Each round is: address the findings → commit and push any fixes → synchronize and rerun the affected required checks under the validation rules → reassess requirement acceptance and re-review the full updated MR diff with the same command. Requirement gaps and code-review findings share this round budget. Refresh and record the source SHA and baseline for each review. The initial review is separate, so the maximum is four review passes in total.
4. A pass requires every in-scope acceptance criterion to be evidenced as met, a completed code review with no unresolved actionable findings, and the required checks passing on the current source SHA. Distinguish optional suggestions from defects and explain any rejected finding with evidence; unresolved disputed findings need human handling. Missing tools, an incomplete assessment/review or failed checks are not a pass. If review or validation cannot run, report the blocker and stop rather than silently substituting a different review route.
5. Stop early when a review passes. If the re-review after corrective round 3 still does not pass, stop automated edits and reviews and wait for human handling. Preserve the branch and MR; report the MR link, reviewed SHA, round count, unmet or unverified criteria, remaining findings and check failures. Do not start round 4, reset the counter on resume, or treat review success as permission to merge.

Keep the MR description's review-status section proportional to the change.
For each pass, record the round, source SHA, target SHA and merge-base, checks and
results, acceptance and review conclusions, and any findings or fixes. Use the
[acceptance guidance](#requirement-acceptance-within-each-review-pass) below to
choose a compact paragraph or a criterion table. The compact format still requires
the full review and the same corrective-round limit. Before a corrective round,
record its number and mark it in progress;
resume that round after interruption. Keep the MR status current; update the issue's
[execution record](worktrees.md#issue-execution-record) at the milestones defined there.
Use the run artifact directory for detailed logs.

An authorized merge follows [merge.md](merge.md). Any fresh full
review needed there consumes the next remaining corrective round, including when
the change came from a server rebase or the target branch. Do not reset the count
or add review passes beyond the existing limit.

### Requirement acceptance within each review pass

The coder reads the issue/spec and relevant discussions and checks the implemented
behavior against the agreed scope, including requirements outside formal
checkboxes. When there is no issue, use the agreed task. Distinguish this MR's
scope from a larger parent issue. On resume or a scope change, refresh the source
material and preserve the user's agreed requirements.

Assess every in-scope criterion on every pass. For a small, straightforward change,
summarize how the checks establish the requested outcome in the review paragraph;
no acceptance table is required. For changes with multiple behaviors, interfaces
or performance requirements, map each criterion to its implementation and evidence
for the reviewed source SHA:

| Criterion and source | Implementation | Validation evidence | Result |
|---|---|---|---|
| Agreed behavior and its issue/spec reference | Relevant file, symbol or change | Test, measurement or inspection result; command and artifact link where applicable | met / unmet / unverified |

Choose evidence appropriate to the criterion. A passing unrelated test, the
existence of code, or a review reporting no findings does not establish acceptance.
Missing behavior is `unmet`; behavior that has not been adequately checked is
`unverified`. Resolve material ambiguity with the user instead of inventing a
requirement or weakening one to obtain a pass.

Keep this assessment distinct from code review. `codex review` receives the Git
diff and project files, not the conversation or issue contents, so the coder owns
the requirement assessment. Reuse evidence only while it remains valid for the
current commit and scope, under the existing validation rules.

## Changes after the loop

When the user later asks for changes based on human feedback, read the latest discussions and source commit and continue on the MR's development branch. After the automatic round limit, follow their specific instructions; resume automatic rounds only with an explicit new allowance.

## Standalone review

When the user explicitly asks for a review of an MR rather than a change to it,
use the checkout rules in [worktrees.md](worktrees.md#reusing-worktrees-for-issues-and-mr-review),
run the review command from step 2 at the MR's exact source commit, and assess the
MR against its issue or description. Report the findings in chat with the
reviewed source and target SHAs and a verdict: approve, changes needed, or needs
discussion. Post them to the MR only when asked. A standalone review makes no
commits and has no corrective rounds.
