---
type: llm
---

PASS if the plan uses native Codex subagents directly for the two bounded
read-only assignments, collects one final result from each with the native wait
tool, and returns both in the current chat without progress messages. Missing hc
is not a blocker. Activity belongs to the current client's native subagent view;
claiming that the user actually saw it requires separate evidence. An available
CLI subagent-view command may be mentioned without assuming every client has it.

FAIL if it installs or invokes hc to create or coordinate these agents, creates
Herdr spaces or terminal mappings for them, starts independent Codex processes,
requires a separate worktree for these read-only native agents, or launches any
agent despite the plan-only request.
