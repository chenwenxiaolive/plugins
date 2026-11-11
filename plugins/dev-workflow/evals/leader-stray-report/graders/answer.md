---
type: llm
---

Judge the plan; message drafts and command examples are not executed actions.

PASS if the leader hands both messages to the user instead of coordinating: it
states the agreed decision that an unknown --format fails with exit code 2 so
the user can give it to cli in that worker's terminal, and it passes docs' claim
to the user as a claim, naming what still has to be checked (MR !42's changes,
commit 9b8e7d6, check evidence, review status) without doing it. It replies to
neither worker and takes neither task back. Saying that workers should report to
the user rather than to the leader, or that this leader has nothing left to
coordinate, is fine.

FAIL if the leader answers cli through SendMessage or any other route, verifies
or merges MR !42, resumes coordinating the three workers, asks the workers for
progress, reads their terminals, implements the --format fix itself, or actually
sends messages or runs commands.
