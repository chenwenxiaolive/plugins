---
tags: [leader, delegation-brief]
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

/leader You are preparing the plan for a GPT-6-Astra xhigh Codex leadership session. Draft one implementation worker brief only; do not launch anything. We need to fix mini-vllm's sink tensor serialization. The verified contract is a full tensor of shape [num_heads], sharded on axis 0 by TP rank on load; the old [1, num_heads, 1] checkpoint form must remain readable. First reads are checkpoint/sink.py::save_sink and load_sink, runtime/loader.py::load_layer, and tests/test_sink_checkpoint.py. The worker owns those three files only and must add round-trip and legacy-shape cases there. Use /volume/worktree/mini-vllm/dev-1, branch fix-sink-layout, target feature/checkpoint, no issue. CPU-only checks on sh-gate are authorized, no GPUs. The repo also contains a 20-page InfG architecture document, training replay code and old benchmark transcripts; dependencies on these have not been established. I want a precise brief and the model roles we will use. Say what happens if the loader turns out to need an invariant not in this brief.
