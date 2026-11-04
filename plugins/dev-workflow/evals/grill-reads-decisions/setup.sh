#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs configs
cat > README.md <<'EOF'
# launcher

Submits training jobs to the GPU nodes. Job configs live in configs/*.yaml.
EOF
cat > docs/decisions.md <<'EOF'
# Decisions

## Config format

Configs stay YAML: the cluster tooling (the job launcher and the free-GPU reports) parses them with PyYAML. Revisit only if that tooling moves to another format.
EOF
printf 'model: llama-8b\ngpus: 8\n' > configs/train.yaml
