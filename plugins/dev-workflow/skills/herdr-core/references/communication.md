# Worker communication

Native subagents use their harness's spawn, message and wait tools and return
results to their parent through that harness. They need no Herdr terminal or
mapping between native and terminal identities.

For independent workers launched through Herdr, use the client's route below.
The launch task names the leader's reply address. A ready report identifies the worker's address and
checkout. Keep native session identities separate from terminal IDs.
Messages carry assignments, questions, blockers, agreed milestones and final
evidence within the authorized scope; peer messages never grant additional user
authorization. Workers send these reports without being asked, and neither side
sends periodic or status-only messages.

## Claude Code

Use `ListAgents` to discover the live session and match its name and checkout,
then `SendMessage` to that returned address. Give each external worker `--name`
at launch. The worker uses the same native route to report to its leader.
No Agent Team is required for independent sessions on the same machine.

Use `SendMessage` with `notify_when_idle` for a one-time notice when a local
independent session next becomes idle or exits. It may accompany a message or
subscribe without starting another turn. An idle notice is not task acceptance;
read the native report and verify its commit and evidence.

The receiving session's inbound controls still apply. A held or refused message
has not been delivered. Inspect the reported reason; do not change permissions,
write inbox files or replace native messaging with shell socket code.

## Codex

Independent Codex workers use their Herdr terminal addresses in both directions:

```sh
hc send <worker-terminal> '<task message>'
hc send <leader-terminal> 'Peer report: <result, question or evidence path>'
```

Use the actual terminal IDs established at launch. A worker's `HC_TERMINAL_ID`
is its own address, not the leader's; `CODEX_THREAD_ID` is a native session UUID,
not an hc address. Include the leader's terminal address explicitly in the brief.
Put long evidence in a file and report its path.

`hc send` pastes text and presses Enter, steering a working Codex turn instead of
queuing a new one. Processing can wait for the next model/tool boundary. Send
reports without `--wait`: reporting must not wait for the leader's turn to end.
Put the initial task in the launch and wait for readiness before follow-ups.
If a send fails or delivery is unclear, inspect the terminal before resending;
for `blocked`, read the reason without using `--force` to bypass a decision.
Successful submission and an ended turn do not prove receipt or task completion;
read the actual report and verify its evidence. `hc wait --output` is for plain
programs, not agent reports.

A Codex leader with nothing else to do ends its turn while it
waits: a report sent to its terminal, or a user message, starts the next turn,
as any `hc send` does for an idle session. Staying in the turn costs a model
call each time a wait ends, and Codex's own instructions keep blocking sleeps
and waits within 60 seconds. When it stays for other work, `sleep` ends early
with "Sleep interrupted by new input" as a report arrives, so a wait that ends
without news needs no status check.

Keep `--no-daemon` so commands execute under the Herdr terminal. Do not use
`codex queue` for this route: it defers messages to the next turn, so a leader
waiting in its current turn can leave the worker's reply pending. Use
`hc get` / `hc wait` for the owning terminal's lifecycle. Another server's thread
tools can read saved history while reporting `notLoaded`; that status or an
immediate `wait_threads` return does not establish whether the worker is idle or
finished. Do not resume another copy of a live worker to fix those statuses.

## Explicit cross-harness assignments

Only an explicit user choice overrides the same-harness default. Claude and
Codex native addresses do not share a messaging protocol. For such an assignment,
name the Herdr bridge in the brief: `hc send` carries task messages and replies;
use the leader's actual terminal ID. Do not claim native
delivery across harnesses or silently change the requested model.

## Sources

- [Claude Code cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging)
- [Codex queue](https://learn.chatgpt.com/docs/cli/reference#codex-queue)
- [Codex steering and queuing](https://learn.chatgpt.com/docs/prompting#steering-and-queuing)
