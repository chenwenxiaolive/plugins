---
type: llm
---

PASS if it says to measure first (from the build host, PyPI's CDN measured faster than the mirrors) and, if a mirror is still wanted, to pass it only as a build argument declared in each downloading stage (`ARG PIP_INDEX_URL`, or `UV_DEFAULT_INDEX` for uv), never as ENV or pip.conf.
FAIL if it switches to the mirror with ENV or pip.conf, or without measuring.
