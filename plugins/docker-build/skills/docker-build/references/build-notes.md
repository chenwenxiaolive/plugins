# Build notes from this box

Measurements and incidents behind the rules in [SKILL.md](../SKILL.md).

## Python package index: the Tsinghua mirror, not PyPI's CDN

From this box, PyPI's CDN (`files.pythonhosted.org`, Fastly `151.101.x`) is too slow for image builds. Measured on 2026-10-17, on the same 16–64 MB wheel ranges within the same hour:

| source | speed |
|---|---|
| `files.pythonhosted.org` (PyPI) | 20–64 KiB/s (about 1 MiB/s at best earlier that day; a torch + CUDA-wheel layer took 23 min) |
| `https://pypi.tuna.tsinghua.edu.cn/simple` | 7.6–12.2 MiB/s |
| `https://mirrors.aliyun.com/pypi/simple` | 3.1–4.5 MiB/s |
| `mirrors.cloud.aliyuncs.com` (Aliyun VPC endpoint) | unreachable |
| GitHub release assets; Ubuntu and NVIDIA apt repositories | 9.6 MiB/s; about 24 MB/s |

The host's own link was idle (52 KiB/s in total), so the bottleneck is the route to Fastly, and it drifts.

- If a download step looks slow, re-measure before blaming the build: fetch a range of one wheel from each index (`curl -r 0-63999999 -o /dev/null -w '%{speed_download}'`) and check the host's `/proc/net/dev` rate.
- The index URL is recorded in the image history, which is acceptable because it is not a secret. Switching it mid-build costs a restart in a fresh task directory.
- The mirror changes transport only. pip checks each file against the `#sha256=` its index lists, but version pins still do not pin bytes; byte-pin load-bearing packages (below).
- GitHub and apt downloads are fast from this box and need no mirror.

## Slow pushes into a new repository

A new image name can require transferring base layers even when the base image already exists in another repository on the same registry. Check transfer counters and target blob availability before assuming the exporter is stuck. Do not estimate push time from the small application diff alone.

If both repositories are authorized, the Registry V2 cross-repository blob mount API can reuse the exact existing digest. A successful mount returns 201; confirm the target blob with HEAD. Keep registry credentials in memory and never print or persist tokens. This is troubleshooting, not a required build step. Only after every required blob is available, a cached retry can avoid an already-running redundant upload. Identify the exact task client by PID, command and cwd before stopping it; never stop the BuildKit daemon or another user's build. Preserve the first log and exit status, then verify the retried publication normally.

## Hard-won build gotchas (from real incidents on this box)

- ⚠ **Low fd limit kills `uv`'s bytecode compile — and BuildKit ignores `--ulimit`.** The daemon's
  default `nofile` is low; any `RUN` step that fans out many processes/files (seen: `uv pip install`
  with `UV_COMPILE_BYTECODE=1`) dies with `No file descriptors available (os error 24)`. Passing
  `docker build --ulimit nofile=…` does NOT reach BuildKit `RUN` steps (verified — same failure).
  Fix in the Dockerfile itself: `ENV UV_COMPILE_BYTECODE=0` (costs only first-import speed), or
  otherwise cap the step's parallelism.
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
