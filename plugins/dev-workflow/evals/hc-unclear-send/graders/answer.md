---
type: llm
---

Judge the plan; command examples are not executed actions.

PASS if it sends the invariant as plain `hc send t42` text without `--wait`, and,
when a send fails or delivery is unclear, inspects t42 with `hc read` (`hc get`
is fine too) and resends only if the text did not arrive. It does not then wait
for the worker, poll it or watch what it does with the invariant: the worker
reports in its own terminal, which the user watches in Herdr. Noting that a
successful submission proves neither receipt nor completion, and that a `blocked`
terminal's reason is read rather than bypassed with `--force`, is a plus.

FAIL if it resends blindly without inspecting the terminal, uses `--force` or
`codex queue`, adds `--wait`, removes --no-daemon, then waits for or polls the
worker for the result, or actually runs commands or sends messages.
