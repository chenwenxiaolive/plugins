# A project's verify skill

A project keeps how to run it for proof in `.agents/skills/verify-<project>/SKILL.md`,
linked from `.claude/skills/verify-<project>`, so that a session that has never
seen the project can launch it, drive a feature and capture the result. Acceptance
runs follow it and the [review](review.md)'s verifier gets its path.

It holds real commands from the project, no placeholders:

- Launch: the command that brings the real surface up from the node checkout and what shows it is ready. Which parts need a GPU, a model under `/volume/model` or another service, since those runs stay with the session that holds the allocation.
- Check: one read-only command that tells whether an instance is worth driving: started by this run, at the checkout's commit.
- Drive: for each feature a user reaches (a command, an endpoint, a training entry point, a file format), how to reach it and the observable end state that proves it, such as an exit code, an output or a stored value. Three to five features are enough to start.
- Evidence: what to capture, into the run directory.
- Cleanup: stop what the run started, by PID. The evidence stays.

It is a draft until a fresh session has followed it once end to end on a node:
launch, check, one feature, cleanup, evidence still there. Record the commit of
that run and what it did not cover.

Write or correct one through the project's own issue and MR, when the owner asks
or a review left a requirement without a run because nobody could launch or drive
the project.
