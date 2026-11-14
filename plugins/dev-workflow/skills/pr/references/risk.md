# Rating a request's risk

Rate these five from the diff and the evidence the body names. The verdicts are
the output: there is no number, and a good verdict never averages away a bad one.

| Dimension | Best | Middle | Worst |
|---|---|---|---|
| Alignment | the diff does what the description and the issue say, and nothing else | an unrelated change is there, named and justified in the body | the diff does more or less than its description, or carries a change nobody mentioned |
| Blast radius | the callers are named and live in this repository | users of the code see the change, it reaches a documented caller, or it changes instruction text other sessions load without widening their authority | it touches a published interface, another repository, CI, build, deployment, dependencies, credentials, a stored format, a running service, or the scripts and configuration other sessions load, or it widens sessions' authority |
| Reversibility | a revert restores the old behavior | a revert needs coordination, such as data the new code has already written | a one-way door |
| Verification | the new behavior has a check on committed code, against a specification, a known example or an independent reference, and the project's gates pass | checks cover part of the change, the evidence is indirect, the diff changes or drops what an existing check expects, or a corrective round changed behavior that has no check of its own | runtime behavior with no check, evidence only that the existing suite still passes, or checks run on uncommitted code |
| Detection | a gate, check or job fails if this regresses | only a later manual run would notice | the change hides its own failure through a swallowed exception or a silent fallback, or no check exercises the path at all |

One-way doors here: a stored format or checkpoint layout that existing files can
no longer be read against, an image already pushed to the registry, a deployment
already serving, a deleted branch or tag, a published preview page, a change to
the deployed `/volume/cluster-ops` or other shared configuration, and a merge
another branch has already built on.

A change widens authority when a session may then do what it had to ask the
owner for, or was forbidden, before (such as merge, delete, publish, deploy, use
GPUs, touch credentials or shared configuration), when it drops or weakens a
confirmation, a review or a check that gates a session's work, or when it
changes this rule or who may merge. Otherwise one that restricts sessions
further, clarifies or corrects a fact does not. When it is unclear what a change
lets a session do, it widens.

Instruction text is the Markdown of skills and project instructions and of the
files they reference, commands in it included, not their frontmatter, scripts,
code or configuration. For it, exercising the changed workflow by hand, even in
part, is verification at its middle and none exercised its worst, a regression
only a later run would show is detection at its middle, and a revert, with the
usual install where there is one, is reversibility at its best.

Size is not a dimension. It is what makes two of them impossible to claim: a
diff too large to judge against its description is not aligned, and behavior too
large to check is not verified.

## The rating and what it authorizes

- Low: alignment, reversibility, verification and detection are each at their best, and blast radius is best or middle. A diff of instruction text alone is also low with verification and detection at their middle, when the project's gates pass, alignment and reversibility are at their best and blast radius is best or middle. Merge it yourself and report the merge, unless the project's instructions opt out of automatic merges.
- High: any dimension is at its worst.
- Medium: anything else.

Medium and high wait for the user: record the rating with the dimensions behind
it, set the execution record to `needs-human`, and say which dimension holds the
merge.

Name the rating and every dimension that is not at its best, each with the file,
caller or command behind the verdict. Never move one verdict to express another
concern: a one-way door is reported as reversibility at its worst, not as weak
verification.

Give one rating. When a verdict needs something not in front of you, rate on the
facts you have and name the check that would change it; two possible ratings are
not a rating, and neither is a placeholder.
