#!/usr/bin/env bash
set -euo pipefail
cat > train.py <<'EOF'
import torch

from model import Net


def train(loader, steps):
    net = Net().cuda()
    opt = torch.optim.AdamW(net.parameters())
    for step, (x, y) in zip(range(steps), loader):
        loss = torch.nn.functional.cross_entropy(net(x.cuda()), y.cuda())
        opt.zero_grad()
        loss.backward()
        opt.step()
        print(f"step {step} loss {loss.item():.4f}")
EOF
cat > model.py <<'EOF'
import torch


class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.body = torch.nn.Sequential(torch.nn.Linear(1024, 4096), torch.nn.GELU(), torch.nn.Linear(4096, 10))

    def forward(self, x):
        return self.body(x)
EOF
