---
tags: [leader, to-tickets]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader Pick up the plan you were drafting when I invoked this. I asked for an
RFC and the dependent implementation issues for moving
/volume/workspace/launcher from dict-based configs to a typed schema. The work
goes into a long-lived integration branch, integration/config-schema, which
merges into main only when the whole migration is done; umbrella issue #120
already tracks it. Your investigation so far found:

- launcher/config.py::load_config returns a plain dict; launcher/cli.py and
  launcher/runner.py index it with string keys, and runner.py fills in defaults
  for missing keys itself.
- tests/test_config.py covers loading only; nothing checks key names or types.
- README.md documents every key, and examples/*.yaml are the shipped configs.
- Decided: an unknown key is an error naming the key and its file, and there is
  no compatibility path for dict access.

Give me the RFC and the child issue drafts here for review; don't file anything
or launch workers yet. Then say which issue a worker could start first once
they are filed, and what the others wait for.
