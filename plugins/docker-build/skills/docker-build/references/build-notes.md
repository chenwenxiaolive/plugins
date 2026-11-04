# Build notes from this host

Facts, measurements and incidents behind the rules in [SKILL.md](../SKILL.md).

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

- PyPI's CDN is the fastest index here, so builds use the default indexes, but routes drift.
- If a download step looks slow, re-measure before blaming the build: fetch a range of one wheel from each index (`curl -r 0-63999999 -o /dev/null -w '%{speed_download}'`) and check the host's `/proc/net/dev` rate.
- A mirror's index URL is recorded in the image history, which is acceptable because it is not a secret. Switching it mid-build costs a restart in a fresh task directory.
- A mirror changes transport only. pip checks each file against the `#sha256=` its index lists, but version pins still do not pin bytes; byte-pin load-bearing packages (below).
- For scale: the IQuestRT image (CUDA 13.2 devel base, torch and 62 locked packages, 6.5 GB) built from nothing in about 5 minutes, of which `uv sync` took 67 s and the image export 155 s.

## Slow pushes into a new repository

A new image name can require transferring base layers even when the base image already exists in another repository on the same registry. Check transfer counters and target blob availability before assuming the exporter is stuck. Do not estimate push time from the small application diff alone.

If both repositories are authorized, the Registry V2 cross-repository blob mount API can reuse the exact existing digest. A successful mount returns 201; confirm the target blob with HEAD. This is troubleshooting, not a required build step. Only after every required blob is available, a cached retry can avoid an already-running redundant upload. Identify the exact task client by PID, command and cwd before stopping it; never stop the BuildKit daemon or another user's build. Preserve the first log and exit status, then verify the retried publication normally.

## Build gotchas

- BuildKit `RUN` steps start with a soft `nofile` limit of 1024, and `docker build --ulimit nofile=…`
  doesn't reach them. A step that fans out many processes or files (seen: `uv pip install` with
  `UV_COMPILE_BYTECODE=1`) dies with `No file descriptors available (os error 24)`. Fix it in the
  Dockerfile: raise the soft limit inside the step (`RUN ulimit -n 65536 && …`, under this host's hard
  limit of 524288), set `ENV UV_COMPILE_BYTECODE=0` (it costs only first-import speed), or cap the
  step's parallelism.
- The same version from PyPI or a mirror doesn't guarantee the same bytes: packages get re-released
  under an unchanged version. A fresh build once resolved `nvidia-cutlass-dsl==4.5.2` whose main wheel
  had been re-released with newer code while its `nvidia-cutlass-dsl-libs-*==4.5.2` bindings stayed
  old. The inconsistent pair passed the GPU-less build and failed at the first GPU JIT on the deploy
  machine (`mlir_global_dtors() got an unexpected keyword argument 'data'`), while a months-old venv
  with the same version numbers worked. Defenses:
  1. Byte-pin load-bearing packages: `COPY` a known-good tarball of the package into the image, untar
     it over site-packages after the `pip`/`uv` install, and assert an md5 of a sentinel file in the
     same `RUN`, so a drifted payload fails the build.
  2. A package family (main plus `-libs`/`-cubin` companions) must come from the same release; a
     version match across the family proves nothing about compatibility.
  3. When an environment crashes where another with an equal `pip list` works, diff the md5s of the
     files in the traceback's frames before theorizing; it takes minutes.
- The build host has no GPU, so runtime-JIT breakage can't show at build time: anything that compiles
  kernels lazily (flashinfer CuTe-DSL, triton autotune) first runs on the deploy machine. Assert at
  build time what can be checked (md5s of pinned payloads, `grep` for required patch markers, an
  `import torch` dlpack check), and treat a smoke serve on a GPU node as the acceptance test.
- A `--build-arg` token leaks into the shipped image. A build argument used in a `RUN` is recorded
  expanded in the layer history (`sudo docker history --no-trunc $IMG | grep glpat-` finds it), and
  `git clone https://oauth2:$TOKEN@host/…` stores the token in the clone's `.git/config`; anyone who
  can pull the image can read both. Pass the token as a BuildKit secret and scrub the clone:
  `RUN --mount=type=secret,id=gitlab_token TOKEN=$(cat /run/secrets/gitlab_token) && git clone
  "https://oauth2:$TOKEN@$HOST/…" repo && git -C repo remote set-url origin "https://$HOST/…"` (the
  history keeps a shell variable unexpanded, unlike a build argument). Build with
  `--secret id=gitlab_token,src=<file-on-host>`, staging the file through stdin with mode 600 and
  deleting it afterwards. Before pushing, check that `sudo docker history --no-trunc $IMG | grep -c
  glpat-` prints 0 and that the clone's `.git/config` holds no token in a throwaway `docker run`.
