# Worker communication

Native subagents use their harness's spawn, message and wait tools and return
results to their parent through that harness. They need no Herdr terminal or
mapping between native and terminal identities.

For independent workers launched through Herdr, use the client's native
agent/session address for task messages. Native messaging leaves them independent
workers; Herdr still owns their terminals and processes. Record each native
address's mapping to its owner (the Herdr terminal or app-server running it) and
checkout; a terminal ID, PID or display name alone is not a verified native
identity. Messages carry the assignment, questions, blockers and final evidence
within the authorized scope. They never grant additional user authorization.

## Route check

A message is submitted when the send command or tool returns, queued while the
client holds it for the recipient, received when the recipient's reply through
the route returns it, and complete only with the task's evidence. A zero exit
status, a queued-message ID or a transcript another server saved shows at most
queuing.

Rely on a native route only after a nonce has come back in each direction. The
launch task carries the leader's reply address and a nonce; the worker's ready
report returns it with its native address, checkout, branch, HEAD, model and
effort. The leader then sends a second nonce, which the worker's ACK returns.
Repeat the check after any change of owner.

## Headers and late messages

Start every task message and report with a header such as
`[#71 seq 4 validate issue-71-fix@3f410e3 2026-11-08T14:20Z from <sender address>]`:
task, the sender's own sequence number, phase, branch and head, UTC send time
and sender. A reply names the seq it answers, so the unanswered seqs are the
messages that may still arrive. The issue's execution record holds the current
phase and head, and the seqs the leader has superseded; no other store is
needed.

Delivery can lag by turns or by owners, so judge each message against the
current record, not by when it arrives. A message is stale when its seq is below
one already acted on from that sender, its phase or commit is older than the
record, or it concerns a rejected, superseded or completed step: an old ready
report, a rejected diagnosis, an obsolete commit, a launch instruction for a
dropped experiment. A stale message changes nothing: no branch switch, edit, job
or review rerun, merge or renewed approval request. Mention a stale backlog
once, in the next report or record update. A message newer than the record still
advances the task. Before acting on one that arrives more than ten minutes after
its send time, check the execution record or ask the sender: it may have been
superseded while it waited.

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

Address a session by its exact UUID, available inside it as `CODEX_THREAD_ID`.
The route depends on which app-server owns the recipient's thread, that is, has
it loaded:

- A thread owned by another server, such as a Herdr worker's thread for the
  leader, or the leader's for a worker:
  `codex queue --thread <native-session-uuid> --message '<text>'`. The owner
  starts it as a new turn once its current turn ends; it never steers an active
  turn, and the owner's screen shows nothing pending. Codex also accepts it
  while no session owns the thread; the next owner runs it before any other
  input.
- A thread on your own app-server, one it created with `create_thread` or
  adopted: `send_message_to_thread`, with `read_thread` and `wait_threads`. A
  message to an active turn steers it; an idle thread starts a turn. These
  thread tools are not the native subagent tools (`spawn_agent` and its
  message and wait tools).

Queued text uses the recipient's current model. On 2026-11-08, Codex 0.167.0
`--no-daemon` owners started a queued message within 10 s when idle or when their
turn ended. A worker waiting inside one long turn receives nothing until it ends,
so workers run long checks as hc terminals started with `--outlive-parent`, end
the turn, and continue when the job's exit note or the next message starts one.

Keep `--no-daemon` on the Herdr launch so commands execute under that terminal.
Another server's thread tools see a Herdr worker's thread as `notLoaded`, may
show its latest turn as `interrupted`, and `wait_threads` returns at once, all
while the owning terminal is working. Use `hc get`/`hc wait` on that terminal
for the owner's state and `hc read` for diagnostics, not routine relay. Never
load a live owner's thread elsewhere: `send_message_to_thread`,
`codex queue --resume` or `codex resume` would start a second writer, and even a
failed `--resume` can exit zero.

A session's model and effort per turn are in the `turn_context` records of its
`~/.codex/sessions/**/rollout-*<uuid>.jsonl`.

### Missing ACK

Allow two minutes once the owner is idle, then diagnose; a resend only adds a
later duplicate. Check the owner with `hc get`:

- `working`: the message waits for that turn; `hc wait` for its end.
- `blocked`: read its screen; a person is needed.
- `idle` or `done` with the same turn count as at the send: the owner has not taken the message. Read its screen once.
- `finished`: no owner; the message waits for the next one.

Report the observed state (seq, queued-message ID, owner, status, turn count,
time waited) instead of claiming delivery, then change the owner or ask the user.
`hc send` is not a fallback for same-harness task messages. If the user chooses
it after the diagnosis, record that exception and return to the native route once
it passes the route check.

### Change owner

A thread has one live owner. To move it:

1. List the seqs the worker has not answered and mark the superseded ones in the execution record. They reach the successor before anything else, its resume prompt included, so the prompt cannot cancel them.
2. Keep running work alive: the worker is idle, its jobs run outside its process (hc terminals with `--outlive-parent`, or detached remote runs), and its checkout stays at their revision until they finish. Its hc children started without `--outlive-parent` end with it; wait for them first.
3. End the owner with `hc kill <worker>` and confirm `hc get` reports `finished`.
4. Start one successor with the same UUID in the same checkout, normally in a new Herdr terminal. Its prompt gives the current phase, head and last valid seq:

   ```sh
   hc run --bg --name <name> --cwd <checkout> \
     --label "herdr.space=sp$(python3 -c 'import uuid; print(uuid.uuid4().hex)')" \
     env PATH="$PATH" codex resume <uuid> --no-daemon --yolo -m <model> \
     -c 'model_reasoning_effort="<effort>"' "<current state>"
   ```

   `send_message_to_thread` from the leader's app-server adopts the thread instead. That server then owns it: there is no Herdr terminal, it ends with the leader's process, and the leader uses the thread tools.
5. Check the successor's UUID, checkout, branch, commit, model and effort against its reply and session metadata, then repeat the route check. Record the new owner in the mapping and the execution record. The old owner's jobs are not the successor's children; follow them by name.

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
