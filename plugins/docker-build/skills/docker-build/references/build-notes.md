# Build notes from this host

Facts, measurements and incidents behind the rules in [SKILL.md](../SKILL.md). Since
2026-11-03, `docker-build` names this host (until then the `longmen-metal` alias);
incidents from the previous build host are marked as such.

## Host

Checked on 2026-11-03:

| item | value |
|---|---|
| Access | user `xqing` at 10.161.41.7 through `sh-gate`; passwordless `sudo` |
| Machine | Ubuntu 22.04 VM, x86_64, 192 CPUs, 2 TiB RAM; no NVIDIA GPU or driver |
| Disks | `/`: 1 TB, home directories and build contexts; `/data`: 7 TB, Docker's data root `/data/docker` |
| Docker | 29.5.2 with the containerd image store; `default` builder: docker driver, BuildKit v0.30.0 |
| Registry login | root's `/root/.docker/config.json` holds only the `registry-cn-shanghai.siflow.cn` entry, copied from the previous host |
| File descriptors | daemon 524288; `RUN` steps start at soft 1024, hard 524288 |

## Download and upload speeds

Measured from this host on 2026-11-03, on 64 MB ranges (whole files when smaller):

| source | speed |
|---|---|
| `files.pythonhosted.org` (PyPI) | 29 MiB/s |
| `https://pypi.tuna.tsinghua.edu.cn/simple` | 13 MiB/s |
| `https://mirrors.aliyun.com/pypi/simple` | 4.5 MiB/s |
| Docker Hub layers | about 39 MiB/s |
| GitHub release assets; Ubuntu and NVIDIA apt repositories | 7.6 MiB/s; 8.3 and 8.6 MiB/s |
| Push of a 6.5 GB image into a new `skyinfer` repository | 108 s, about 58 MiB/s |

- PyPI's CDN is the fastest index here, so builds use the default indexes. Routes drift: on 2026-10-17 the previous host reached PyPI at 20–64 KiB/s (a torch + CUDA-wheel layer took 23 min) and the Tsinghua mirror at 7.6–12.2 MiB/s.
- If a download step looks slow, re-measure before blaming the build: fetch a range of one wheel from each index (`curl -r 0-63999999 -o /dev/null -w '%{speed_download}'`) and check the host's `/proc/net/dev` rate.
- A mirror's index URL is recorded in the image history, which is acceptable because it is not a secret. Switching it mid-build costs a restart in a fresh task directory.
- A mirror changes transport only. pip checks each file against the `#sha256=` its index lists, but version pins still do not pin bytes; byte-pin load-bearing packages (below).
- For scale: the IQuestRT image (CUDA 13.2 devel base, torch and 62 locked packages, 6.5 GB) built from nothing in about 5 minutes, of which `uv sync` took 67 s and the image export 155 s.

## Slow pushes into a new repository

A new image name can require transferring base layers even when the base image already exists in another repository on the same registry. Check transfer counters and target blob availability before assuming the exporter is stuck. Do not estimate push time from the small application diff alone.

If both repositories are authorized, the Registry V2 cross-repository blob mount API can reuse the exact existing digest. A successful mount returns 201; confirm the target blob with HEAD. Keep registry credentials in memory and never print or persist tokens. This is troubleshooting, not a required build step. Only after every required blob is available, a cached retry can avoid an already-running redundant upload. Identify the exact task client by PID, command and cwd before stopping it; never stop the BuildKit daemon or another user's build. Preserve the first log and exit status, then verify the retried publication normally.

## Hard-won build gotchas (incidents on the previous host)

- ⚠ **Low fd limit kills `uv`'s bytecode compile — and BuildKit ignores `--ulimit`.** BuildKit `RUN`
  steps start with a soft `nofile` of 1024 (on this host too); any step that fans out many
  processes/files (seen: `uv pip install` with `UV_COMPILE_BYTECODE=1`) dies with `No file descriptors
  available (os error 24)`. Passing `docker build --ulimit nofile=…` does NOT reach BuildKit `RUN` steps
  (verified — same failure). Fix in the Dockerfile itself: raise the soft limit inside the step
  (`RUN ulimit -n 65536 && …`, under this host's hard limit of 524288), set `ENV UV_COMPILE_BYTECODE=0`
  (costs only first-import speed), or otherwise cap the step's parallelism.
- ⚠ **Never trust "same version == same bytes" from PyPI or a mirror — same-version re-releases are
  real.** Incident (2026-07-09): a fresh image build resolved `nvidia-cutlass-dsl==4.5.2` whose MAIN
  wheel had been silently re-released with newer code, while its companion `nvidia-cutlass-dsl-libs-*==4.5.2`
  bindings stayed old → an internally inconsistent pair that passed the GPU-less build, then ICE'd at
  first GPU JIT on the deploy box (`mlir_global_dtors() got an unexpected keyword argument 'data'`);
  a months-old venv with the SAME version numbers worked because its pair was consistent. Defenses:
  1. **Byte-pin load-bearing packages**: `COPY` a known-good tarball of the package into the image,
     untar over site-packages after `pip/uv install`, and **assert an md5** of a sentinel file in the
     same `RUN` (build fails loudly if the payload drifts).
  2. When one package is a **family** (main + `-libs`/`-cubin` companions), they must come from the
     same release wave — a version-string match across the family proves nothing about compatibility.
  3. Debugging "works in env A, crashes in env B" with equal `pip list`: **diff file md5s** of the
     frames in the traceback between the two envs before theorizing — same-version different-content
     is a 5-minute check.
- ⚠ **The build box is GPU-less: runtime-JIT breakage cannot be caught at build time.** Anything that
  compiles kernels lazily (flashinfer CuTe-DSL, triton autotune) first runs on the deploy machine.
  Compensate with build-time asserts for what IS checkable (md5 of pinned payloads, `grep` for
  required patch markers, `import torch` dlpack sanity) and a smoke serve on a GPU node as the real
  acceptance gate.
- ⚠ **A `--build-arg` token leaks into the shipped image — use a BuildKit secret.** A build arg used
  in a `RUN` is recorded **expanded** in the image's layer history (`sudo docker history --no-trunc $IMG
  | grep glpat-` finds it), and `git clone https://oauth2:$TOKEN@host/…` bakes the token into the
  clone's `.git/config` remote URL — both are readable by anyone who can pull the image. Fix: pass the
  token as a secret and scrub the clone. In the Dockerfile:
  `RUN --mount=type=secret,id=gitlab_token TOKEN=$(cat /run/secrets/gitlab_token) && git clone
  "https://oauth2:$TOKEN@$HOST/…" repo && git -C repo remote set-url origin "https://$HOST/…"` (the
  shell var `$TOKEN` is NOT expanded in history, unlike a build arg). Build with
  `--secret id=gitlab_token,src=<file-on-box>` (stage the file via stdin, `chmod 600`, delete after).
  **Verify before pushing:** `sudo docker history --no-trunc $IMG | grep -c glpat-` → 0, and grep the
  clone's `.git/config` inside a throwaway `docker run`.
