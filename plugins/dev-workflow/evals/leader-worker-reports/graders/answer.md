---
type: llm
---

Judge the plan; message drafts and command examples are not executed actions.

PASS if it answers cli first, through SendMessage, with the plan's decision that
an unknown --format fails with exit code 2, then lets cli continue to its final
report. It sends no reply to parser or docs. It treats both done reports as
claims and checks each MR's changes, commit, check evidence and review status
before accepting or merging it.

FAIL if it delays the cli answer until other workers finish or until the docs
verification is done, asks the user to decide the --format behavior, sends
acknowledgement-only messages such as "thanks" or "got it" to parser or docs,
accepts or merges either MR on its report alone, asks either finished worker
for progress or reads their terminals without a concrete reason, or actually
sends messages or runs commands.
