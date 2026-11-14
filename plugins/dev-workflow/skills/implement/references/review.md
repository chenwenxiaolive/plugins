# Review

Use these rules for implementation review and requested standalone reviews. A
review is a verification: a session that did not write the change runs it, and a
finding counts only when a run shows it.

A run executes the committed change and records the exact command and its
output. Instruction text has no command: its run is a fresh session that gets
the committed files by path and a case, a concrete situation a session following
that text would be in, without the outcome the requirement calls for. What the
session does is the output.

1. Round 0: start the verifier, a fresh session in the clean checkout at the MR source commit, with the diff range `<target-sha>...<source-sha>`, the issue's requirements or the agreed task, the acceptance runs stated for them, and this brief:

   > Verify this change, then try to break it. For each requirement, repeat its stated run, add your own on the surface the change touches, and report each command, its output and whether the output meets the requirement. Report a finding only with its run and the output that the requirement, or a contract an existing caller relies on, calls for. You cannot run instruction text: for each requirement and each finding on it, give a case, a concrete situation that a session following the text would be in, and separately the outcome the requirement calls for. Run only on this machine, and name with its command a run that needs a node, a GPU or another service. The session that started you makes those runs. Leave out anything without a run or a case: that covers style, naming, structure and risks that need a future change to matter. No findings is a valid result. Keep scripts and output in `<run_dir>` and leave the checkout unchanged.

   - Claude Code: a `general-purpose` agent from the Agent tool; call no Codex.
   - Codex: from the checkout, `codex exec -s workspace-write --add-dir <run_dir> -o <run_dir>/verify-0.md - < <run_dir>/brief-0.md > <run_dir>/verify-0.log 2>&1` (minutes; run it in the background). A case session takes the same command with its case as the brief.
2. Make the runs the verifier left to you and repeat each finding's run. Keep a finding when the output shows the failure and the failure breaks a requirement or a contract; an error that propagates where no requirement asks for recovery breaks neither. Drop the rest and give their count in the MR, each with a one-line reason. Read the comments the diff adds yourself, since they need no run: when one narrates the code or states a constraint the code could enforce, turn it into a name, type, assertion or test, or delete it. A pass means every requirement has a run that meets it, no kept finding is left and the checks pass on the current commit.
3. Otherwise, with a kept finding, fix it in scope with the smallest change, push, rerun the affected checks and start the verifier again on the new commit, the kept findings' runs added to its acceptance runs: one corrective round. If that does not pass either, or a requirement has no run that you or the verifier can make, stop, set `needs-human` and report what remains. After that, follow the user's feedback; another round needs their explicit allowance. With the round spent, a change or merge recheck that needs a review goes back to the user as `needs-human`.
4. Record each round's commit, runs and outcome in a review-status section of the MR description, so that the count survives interruptions. A later merge recheck uses the corrective round if it is unspent and never resets it.

A standalone review the user requests uses a detached checkout at the MR's source
commit, the same verifier, and a verdict in chat; post it to the MR only when asked.
