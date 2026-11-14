# Merge

Once the review passes, rate the request's risk by
[pr's rule](../../pr/references/risk.md) and record the rating, with the
dimensions behind it, beside the review status. A low rating merges on your own
authority; medium and high wait for the user, as that rule describes. A merge
request covers the source SHA it was made for; a later commit needs a new request.

Every merge:

- Recheck the MR, its source SHA and the current target. If either moved since the passing review, repeat the review's runs that the move touches, using the corrective round if it is unspent and a run now fails.
- Merge MRs in dependency order: the base MR first, then recheck the dependent one against the moved target and run its checks on the integrated result. Work merged into a feature branch reaches the default branch only through that branch's own MR.
- Merge with the reviewed SHA as a guard: `glab mr merge <iid> --sha <sha>` or `gh pr merge <n> --merge --match-head-commit <sha>`. While a pipeline runs, `glab` schedules an auto-merge instead: wait until the MR shows merged before the next step. After an error or timeout, read the MR and target back before retrying. A 504 can still merge: if the target already holds a merge of the reviewed SHA while the MR stays open, close the MR with a note naming that commit instead of merging again.
- If the forge's rebase leaves a checkout diverged only by that rebase, rename its old branch to an archive name with `git branch -m` and recreate the branch at the new SHA.
- Confirm the merge commit, then set the execution record to `merged` and delete the merged source branch on the forge.
