---
name: grilling
description: "Clarify or stress-test a feature, technical design or development plan when the user asks for grilling, probing questions or a design discussion."
---

# Grilling

Help the user reach a decision that can become an issue or an implementation task.

- Check facts in the code, docs and existing decisions before asking. Use [gpu-cluster](../gpu-cluster/SKILL.md) before GitLab or remote access; an experiment on a GPU still needs the user's node.
- Ask one to three questions at a time, each with a recommendation and its tradeoff. Ask only about choices that change the result; settle minor ones as stated assumptions, and don't reopen settled ones.
- Stop when goal, scope, acceptance and material tradeoffs are clear. Summarize decisions, assumptions and open questions.
- Discussion alone ends with that summary. If the user already asked for issues or code, continue with [to-tickets](../to-tickets/SKILL.md) or [implement](../implement/SKILL.md) without asking again.
