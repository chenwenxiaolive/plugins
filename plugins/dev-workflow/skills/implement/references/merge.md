# Merge

Once the review passes, score the MR's risk and record the score and its reasons
beside the review status. Start at 1 and add, up to 10:

- 1 for every full 200 changed lines of non-test code, up to 3;
- 2 when changed runtime code has no test covering the change;
- 1 for each corrective review round used;
- 1 for a behavior change users will notice;
- 4 when it touches CI, build, deployment, dependencies, credentials, data migrations or stored formats, public interfaces (APIs, CLI flags, config formats), or skills and agent instructions.

At 3 or below, merge it yourself without asking and report the merge, unless the
project's instructions opt out of automatic merges. Above 3, set the execution
record to `needs-human` with the score, tell the user, and merge only when they ask.

Every merge:

- Recheck the MR, its source SHA and the current target. If either moved since the passing review, reassess what changed, using a remaining round if a new review is needed.
- Merge with the reviewed SHA as a guard: `glab mr merge <iid> --sha <sha>` or `gh pr merge <n> --merge --match-head-commit <sha>`. While a pipeline runs, `glab` schedules an auto-merge instead: wait until the MR shows merged before the next step. After an error or timeout, read the MR and target back before retrying. A 504 can still merge: if the target already holds a merge of the reviewed SHA while the MR stays open, close the MR with a note naming that commit instead of merging again.
- If the forge's rebase leaves a checkout diverged only by that rebase, rename its old branch to an archive name with `git branch -m` and recreate the branch at the new SHA.
- Confirm the merge commit, then set the execution record to `merged` and delete the merged source branch on the forge.
