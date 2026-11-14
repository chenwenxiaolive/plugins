# Review

Use these rules for implementation review and requested standalone reviews. A
review is a verification: a session that did not write the change runs it, and a
finding counts only when a run shows it.

A run executes the committed change and records the exact command and its
output. [Instruction text](../../pr/references/risk.md) has nothing to execute,
so it gets no verifier and a requirement on it needs no run. Its author runs each
command the changed text gives, as written, follows the changed workflow once
from the committed text where the task at hand allows, and states in the MR's
evidence what that covered and what only use will show. A diff of instruction
text alone passes with that and the project's checks on the current commit,
without the rounds below.

1. Round 0: start the verifier, a fresh session in the clean checkout at the MR source commit. Give it the diff range `<target-sha>...<source-sha>`, the issue itself, its text saved unedited in the run directory beside its link (the agreed task in the owner's words when there is none), the acceptance runs with the ones you stated marked as yours, the path of the project's [verify skill](project-verify.md) when it has one, and this brief. When the project's tests run on a node, first bring its checkout there to the source commit as [remote-workflow.md](../../gpu-cluster/remote-workflow.md) requires and make a run directory on the node; the brief names both.

   > Verify this change, then try to break it. Read the requirements from the issue or task text itself: a run the change's author stated is the author's reading, so check that it tests its requirement before you rely on it. For each requirement, repeat its stated run, add your own on the surface the change touches, and report each command, its output and whether the output meets the requirement. Run the target commit's version of each test the diff edits or deletes against the change, the old file kept in the run directory and no copy of the repository made; a failure that no requirement asks for is a finding. Report a finding only with its run and the output that the requirement, or a contract an existing caller relies on, calls for. Run on this machine and, when a node checkout is named here (`<alias>:<path>`, or none), in it without GPUs: start each command there with `cd -- <path> && export CUDA_VISIBLE_DEVICES= &&`, keep what a run needs on the node in `<node_run_dir>`, and report a checkout that is not clean at the source commit instead of changing it. Name with its command a run that needs a GPU or another service. The session that started you makes those runs. Leave out anything without a run: that covers instruction text, style, naming, structure and risks that need a future change to matter. No findings is a valid result. Keep scripts and output in `<run_dir>` and leave the checkout unchanged.

   - Claude Code: a `general-purpose` agent from the Agent tool; call no Codex.
   - Codex: from the checkout, `codex exec -s danger-full-access -o <run_dir>/verify-0.md - < <run_dir>/brief-0.md > <run_dir>/verify-0.log 2>&1` (minutes; run it in the background). Codex's sandbox is off by the owner's decision: inside it ssh has no network and its shared connection ends with each command.
2. Make the runs the verifier left to you and repeat each finding's run. Keep a finding when the output shows the failure and the failure breaks a requirement or a contract; an error that propagates where no requirement asks for recovery breaks neither. Drop the rest and give their count in the MR, each with a one-line reason. Read the comments the diff adds yourself, since they need no run: when one narrates the code or states a constraint the code could enforce, turn it into a name, type, assertion or test, or delete it. A pass means every requirement has a run that meets it, no kept finding is left and the checks pass on the current commit.
3. Otherwise, with a kept finding, fix it in scope with the smallest change, commit each kept finding's run as a test where the project's suite can hold it, push, rerun the affected checks and start the verifier again on the new commit (a named node checkout brought to it first), the kept findings' runs added to its acceptance runs: a corrective round. Rounds repeat without asking the user until one passes or a stop is reached. Stop, set `needs-human` and report what remains when:
   - a run that an earlier round fixed fails again;
   - a kept finding has no fix that meets every requirement, or its fix changes a contract the issue does not ask to change;
   - the third corrective round does not pass;
   - a requirement has no run that you or the verifier can make.

   After a stop, follow the user's feedback: another round needs their explicit allowance, and a change or merge recheck that needs a review goes back to the user as `needs-human`.
4. Record each round's commit, runs and outcome in a review-status section of the MR description, so that the count survives interruptions. A later merge recheck uses a corrective round if one is left and never resets the count.

A standalone review the user requests uses a detached checkout at the MR's source
commit, the same verifier, and a verdict in chat; post it to the MR only when asked.
