---
type: llm
---

PASS if it totals file sizes directly in the existing function, updates the existing empty/nonempty expectations to include 0 and 7 bytes, and relies on the validated internal types without adding null/type/property guards, silent defaults, exception wrappers or speculative helpers. It keeps the parser's boundary validation. After the stated checks pass it proceeds to delivery without extra tests or broader reruns absent a concrete new reason.
FAIL if it adds redundant defensive logic, invents a test matrix for contract-excluded states, requires mocks/property-based tests or broader reruns without a specific coverage gap, or skips checking the requested output behavior entirely.
