# Review

Use these rules for implementation review and requested standalone reviews. A
review is a verification: a session that did not write the change runs it, and a
finding counts only when a run shows it.

A run executes the committed change and records the exact command and its
output. For instruction text, a run is a fresh session that gets the committed
files and a case, not the expected outcome; what it does is the output.

1. Round 0: start the verifier, a fresh session in the clean checkout at the MR source commit, with the diff range `<target-sha>...<source-sha>`, the issue's requirements or the agreed task, and this brief:

   > Verify this change, then try to break it. For each requirement, run the surface the change touches and report the command, its output and whether the output meets the requirement. Report a finding only with its run and the output the requirement calls for. Instruction text is run by the author: for each requirement and each finding on it, give a case and the outcome the requirement calls for. Leave out anything without a run: that covers style, naming, structure and risks that need a future change to matter. No findings is a valid result. Keep scripts and output in `<run_dir>` and leave the checkout unchanged.

   - Claude Code: a `general-purpose` agent from the Agent tool; call no Codex.
   - Codex: from the checkout, `codex exec -s workspace-write --add-dir <run_dir> -o <run_dir>/verify-0.md - < <run_dir>/brief-0.md > <run_dir>/verify-0.log 2>&1` (minutes; run it in the background).
2. Run the cases the verifier gave for instruction text and repeat each finding's run yourself. Keep a finding when the output shows the failure and the failure breaks a requirement or a contract; an error that propagates where no requirement asks for recovery breaks neither. Drop the rest and give their count in the MR, each with a one-line reason. A comment the diff adds needs no run: when it narrates the code or states a constraint the code could enforce, turn it into a name, type, assertion or test, or delete it. A pass means every requirement has a run that meets it, no kept finding is left and the checks pass on the current commit; a requirement no run reached is a gap that keeps the review from passing.
3. Otherwise fix the kept findings in scope with the smallest change, push, and repeat the affected checks, the kept findings' runs and the requirement runs the fix touches, without a new search for findings: one corrective round. If a run still fails, stop, set `needs-human` and report what remains. After that, follow the user's feedback; another round needs their explicit allowance. With the round spent, a change or merge recheck that needs a review goes back to the user as `needs-human`.
4. Record each round's commit, runs and outcome in a review-status section of the MR description, so that the count survives interruptions. A later merge recheck uses the corrective round if it is unspent and never resets it.

A standalone review the user requests uses a detached checkout at the MR's source
commit, the same verifier, and a verdict in chat; post it to the MR only when asked.
