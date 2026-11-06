---
name: grilling
description: "Stress-tests a feature, technical design or development plan with probing questions until it is clear enough to become an issue or a task. Use when the user asks for grilling, probing questions or a design discussion."
---

# Grilling

Help the user reach a decision that can become an issue or an implementation task.

- Check facts in the code, docs and existing decisions before asking.
- Ask a few questions at a time, the ones the rest depends on first, and hold the others until those are answered: one decision per question, with your recommended answer and its tradeoff. Ask only about choices that change the result; state minor ones as assumptions the user can correct, and don't reopen settled ones.
- Stop when goal, scope, acceptance and material tradeoffs are clear. Summarize decisions, assumptions and open questions.
- Discussion alone ends with that summary. If the user already asked for issues or code, continue without asking again: read and follow [to-tickets](../to-tickets/SKILL.md) (only the user can invoke it as a skill) or use [implement](../implement/SKILL.md).
