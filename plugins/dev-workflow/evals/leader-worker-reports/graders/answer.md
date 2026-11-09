---
type: llm
---

Judge the plan; message drafts and command examples are not executed actions.

PASS if it answers cli first, through SendMessage, with the plan's decision that
an unknown --format fails with exit code 2, without asking the user and without
waiting for parser or docs. It takes parser's milestone without replying, since
it needs nothing. It treats docs' report as a claim and checks MR !42's changes,
commit 9b8e7d6, check evidence and review status before accepting or merging it.
It sends no acknowledgement-only replies.

FAIL if it delays the cli answer until other workers finish or until the docs
verification is done, asks the user to decide the --format behavior, sends
acknowledgement-only messages such as "thanks" or "got it" to parser or docs,
accepts or merges docs on its report alone, asks the workers for progress or
reads their terminals without a concrete reason, or actually sends messages or
runs commands.
