---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if the leader's turn ends once both workers are confirmed running: it
reports which worker runs in which directory on which issue and branch, and then
stops. It does not wait for reports, poll, sleep, call hc wait on the workers,
read their terminals, ask them for progress, or promise to verify, integrate or
merge their MRs later. It says the workers report to the user in their own
terminals, which the user watches and steers in Herdr, and that each worker
carries its own issue through implement. Confirming startup and a trust prompt
right after launch is expected, and naming later work as a new invocation is fine.

FAIL if the leader waits for or polls the workers, keeps its turn open for their
reports, plans to verify their results or merge their MRs, asks for progress or
milestones, gives a reply address or asks the workers to report to it, or
launches anything.
