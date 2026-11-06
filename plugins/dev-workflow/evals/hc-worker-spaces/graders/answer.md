---
type: llm
---

PASS if each of the two `hc run` launches gets its own new `herdr.space` id (for example a uuid generated inside each launch's label, or a separate variable per worker), so each worker opens in a Herdr space of its own.
FAIL if both launches use the same space id, such as one `$SPACE` variable set once and used by both, or if either launch has no `herdr.space` label.
