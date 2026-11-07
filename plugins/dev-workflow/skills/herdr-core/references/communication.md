# Native worker communication

Use the client's native agent/session address for task messages. Record its
mapping to the Herdr terminal and checkout; a terminal ID, PID or display name
alone is not a verified native identity. The launch task includes the leader's
reply address. A ready reply identifies the worker and confirms the return route.
Messages carry the assignment, questions, blockers and final evidence within the
authorized scope. They never grant additional user authorization.

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

Native subagents use the available spawn, message and wait tools. For independent
Codex sessions launched through Herdr on this host, send in either direction with:

```sh
codex queue --thread <native-session-uuid> --message '<task message or worker report>'
```

Use the exact session UUID, available inside the session as `CODEX_THREAD_ID`.
Include the sender's UUID in worker reports and identify them as peer messages,
not user instructions. The command queues text using the recipient's current
model; successful queuing does not prove receipt or task completion.

Keep `--no-daemon` on the Herdr launch so commands execute under that terminal.
On 2026-11-07, Codex 0.167.0 exchanged messages in both directions and woke idle
sessions with this launch mode and plain `codex queue`; no `--resume` was needed.
Do not add `--resume` for a live Herdr worker: it asks another server to load the
session, and even a failed resume can return exit status zero.

Thread tools can read saved history from another server while reporting
`notLoaded`; this was observed with the same test. That status and an immediate
`wait_threads` return do not establish whether the owning Herdr terminal is idle
or finished. For sessions owned by the current app-server, use its native
send/read/wait tools. For a Herdr-owned session, await its queued native report
and use `hc get`/`hc wait` for the owning process's lifecycle when needed. Use
`hc read` for terminal diagnostics or transcript capture, not routine task relay.

## Explicit cross-harness assignments

Only an explicit user choice overrides the same-harness default. Claude and
Codex native addresses do not share a messaging protocol. For such an assignment,
name the Herdr bridge in the brief: `hc send` carries task messages and replies;
use the actual leader terminal ID, when one exists. Without a leader terminal,
collect the worker's report with `hc wait` and `hc read`. Do not claim native
delivery across harnesses or silently change the requested model.

## Sources

- [Claude Code cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging)
- [Codex queue](https://learn.chatgpt.com/docs/cli/reference#codex-queue)
