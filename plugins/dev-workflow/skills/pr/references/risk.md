# Risk the score does not see

Implement's score counts changed size, missing coverage, review rounds used,
visible behavior and sensitive areas. These five dimensions catch what it
cannot. They produce no second score: state the ones that come out worse than
contained, each with the file, caller or command that shows it.

- Alignment: does the diff do what the description and the issue say, and nothing else? Name every unrelated change, then split it out or say why it stays.
- Blast radius: name what consumes the changed code, such as direct callers, another repository, a running deployment, a published image or a documented interface. "Internal only" is a claim that needs a caller search behind it.
- Reversibility: a two-way door comes back with a revert. One-way doors here include a stored format or checkpoint layout that leaves existing files unreadable by released code, an image already pushed to the registry, a deployment already serving, a deleted branch or tag, a published preview page, a write under `/volume/model` or shared configuration, and a merge another branch has already built on. Name the door and what undoing it would cost.
- Verification: does the evidence prove the new behavior on committed code, against expected results from a specification, a known example or an independent reference? An unchanged suite that still passes proves only that nothing else broke.
- Detection: if this breaks after the merge, what surfaces it, and to whom? A failing check or a job that stops is detection; a user noticing is not. Swallowed exceptions and silent fallbacks hide breakage and raise every dimension above.

A one-way door or a misaligned diff keeps the merge with the user. Raising the
numeric score to express that concern is the wrong move: report the score the
rules give, and the dimension that holds the merge, separately.
