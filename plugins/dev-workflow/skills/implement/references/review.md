# Review

Use these rules for implementation review and requested standalone reviews.

1. Round 0: in the clean checkout at the MR source commit, run `codex review --base <target-sha> < /dev/null > <run_dir>/review-0.md 2> <run_dir>/review-0.log` (minutes; run it in the background). Separately check the change against the issue's requirements, which `codex review` does not see.
2. A pass means the requirements are met with evidence, no actionable finding is left and the checks pass on the current commit. An actionable defect needs a reachable condition, a violated requirement or contract, and a concrete consequence; missing defensive code or tests alone is not a defect. Fix defects in scope with the smallest change; reject style preferences and unsupported scenarios with a one-line reason in the MR.
3. Otherwise fix, push, rerun affected checks and review again: at most three corrective rounds. If round 3 still fails, stop, set `needs-human` and report what remains. After that, follow the user's feedback; further automatic rounds need their explicit allowance. With no round left, a change or merge recheck that needs a review goes back to the user as `needs-human`.
4. Record each round's commit, checks and outcome in a review-status section of the MR description, so that the count survives interruptions. A later merge recheck uses the remaining rounds and never resets them.

A standalone review the user requests uses a detached checkout at the MR's source
commit, the same command, and a verdict in chat; post it to the MR only when asked.
