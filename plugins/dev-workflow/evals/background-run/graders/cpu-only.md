---
type: llm
---

PASS if the job's environment sets CUDA_VISIBLE_DEVICES to an empty value so the CPU-only job cannot touch a GPU.
FAIL otherwise.
