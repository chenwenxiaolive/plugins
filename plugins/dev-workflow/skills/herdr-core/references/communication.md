# Worker communication

Native subagents use their harness's spawn, message and wait tools and return
results to their parent through that harness. They need no Herdr terminal or
mapping between native and terminal identities.

Independent workers get the full assignment in the launch and send one final
report. Name the leader's reply address. Native session identities stay separate
from terminal IDs. Peer messages never grant user authorization. There are no
ready, progress, milestone, status or acknowledgement messages; only a blocker
or one late correctness fact waits for one answer, then continues.

## Claude Code

Give each worker `--name` and the leader's verified native address. The worker
sends its final report with `SendMessage`. For a later answer, use `ListAgents`
to match name and checkout, then `SendMessage`. No Agent Team is required.

Inbound controls apply. A held message has not been delivered; inspect the
reason. Do not bypass it with inbox files or socket code.

## Codex

Independent Codex workers use their Herdr terminal addresses in both directions:

```sh
hc send <worker-terminal> '<answer or concrete correction>'
hc send <leader-terminal> 'Final: <result or blocker and evidence path>'
```

Use terminal IDs from launch. `HC_TERMINAL_ID` is the worker's own address, not
the leader's; `CODEX_THREAD_ID` is not an hc address. Put long evidence in a file.

`hc send` steers a working turn instead of queuing. Send reports without
`--wait`. If delivery is unclear, inspect before resending; read a `blocked`
reason without `--force`. Submission or an ended turn does not prove completion.
`hc wait --output` is for plain programs.

An idle Codex leader ends its turn; a report starts the next one. Waiting in-turn
costs a model call per timeout. If it stays for other work, a sleep interrupted
by input ends without a status check.

Keep `--no-daemon` so commands stay under the Herdr terminal. Do not use `codex
queue`: it defers a reply. Use `hc get` / `hc wait` for the owning terminal.
Another server's `notLoaded` or immediate `wait_threads` proves neither idle nor
finished; do not resume a second copy.

## Explicit cross-harness assignments

Only an explicit user choice overrides the same-harness default. For such an
assignment, `hc send` carries the final report or one answer. Do not claim
native cross-harness delivery or silently change the model.

## Sources

- [Claude Code cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging)
- [Codex queue](https://learn.chatgpt.com/docs/cli/reference#codex-queue)
- [Codex steering and queuing](https://learn.chatgpt.com/docs/prompting#steering-and-queuing)
