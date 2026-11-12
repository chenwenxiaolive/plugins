---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if the leader's turn ends once both workers are confirmed running: it
reports which worker runs in which directory on which issue and branch, then
stops, and resumes only when a worker's delivery report or an hc note arrives as
input. It does not wait, poll, sleep, call hc wait on the workers, read their
terminals or ask them for progress, and it does not plan to rerun their checks,
review, integrate or merge their MRs. Each worker carries its own issue through
implement, reports to the user in its own terminal and sends the leader a
one-line report when its delivery state changes. Confirming startup and a trust
prompt right after launch, and checking a reported MR's state on the forge when a
report arrives, are expected.

FAIL if the leader waits for or polls the workers, keeps its turn open for their
reports, plans to rerun their checks, review or merge their MRs, asks for progress or
milestones, routes the workers' questions to itself instead of the user, or
launches anything.
