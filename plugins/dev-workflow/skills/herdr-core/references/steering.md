# Steering a worker

A worker reports in its own terminal and the user steers it there, in its Herdr
space. No session coordinates workers: there is no reply address in a launch, no
leader terminal to report to, and neither Claude's native cross-session messages
nor `hc send` is part of the normal workflow. Native subagents are separate: they
use their harness's spawn, message and wait tools and return results to their
parent, with no Herdr terminal or identity mapping.

Put the whole task in the launch. A message to a booting agent can be lost, and a
worker that has to ask for its scope is already waiting on someone.

When the user asks for text to be sent to a worker instead of typing it in Herdr:

```sh
hc send <worker-terminal> '<text from the user>'
```

`hc send` pastes text and presses Enter, steering a working session instead of
queuing a new turn, so processing can wait for the next model/tool boundary. Send
without `--wait`. For Codex, keep `--no-daemon` so commands execute under the
Herdr terminal, and do not use `codex queue`, which defers the message to the
next turn. A worker's `HC_TERMINAL_ID` is its own address; `CODEX_THREAD_ID` is a
native session UUID, not an hc address. Successful submission and an ended turn
prove neither receipt nor completion. If a send fails or delivery is unclear,
inspect that terminal before resending; for `blocked`, read the reason rather
than using `--force` to bypass a decision.

Another server's thread tools can read saved history while reporting `notLoaded`;
that status, or an immediate `wait_threads` return, establishes neither that a
worker is idle nor that it finished. Never resume a second copy of a live worker
to fix those statuses. `hc wait --output` is for plain programs, not agent
reports.

## Sources

- [Claude Code cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging)
- [Codex queue](https://learn.chatgpt.com/docs/cli/reference#codex-queue)
- [Codex steering and queuing](https://learn.chatgpt.com/docs/prompting#steering-and-queuing)
