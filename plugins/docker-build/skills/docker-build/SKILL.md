---
name: docker-build
description: >-
  Build Docker images from a Dockerfile on the remote build box (SSH alias `docker-build` →
  10.172.3.216, user xqing) and publish only to registry-cn-shanghai.siflow.cn.
  Use for building, tagging, or pushing container images to this registry. Covers sudo Docker
  authentication, context staging, NVMe buildx builds with xqing-nvme1, detached execution,
  publication verification, and cleanup on the shared build host.
---

# Building & pushing Docker images on the remote build box

A playbook for driving image builds on a dedicated remote box from your control node (docker 26.1.3 + buildx, no local docker-group membership).

Publish only to `registry-cn-shanghai.siflow.cn`. Use one build invocation with an immutable tag. Completion requires successful publication and a published digest matching the build's exporter digest. Follow an explicit user request to build without pushing.

For each new build, publish one tagged `linux/amd64` image manifest. Pass `--provenance=false --sbom=false` to prevent BuildKit from adding an image index and extra attestation artifacts. This keeps the registry listing to one entry for the new build. See [Docker build attestations](https://docs.docker.com/build/metadata/attestations/). If the user explicitly requests attestations or multiple platforms, follow that request and adjust verification accordingly.

These flags affect new builds only. Existing registry artifacts remain for user-managed cleanup unless cleanup is explicitly requested.

## 0. Build host and storage

- SSH alias: `docker-build`, user `xqing`, x86_64. Every SSH command must explicitly `cd` before doing work.
- Run every Docker command with `sudo docker`; sudo is passwordless. Registry credentials belong to `/root/.docker/config.json`.
- Use the existing **`xqing-nvme1` builder** for builds on the NVMe disk. Inspect the live host before relying on recorded disk sizes:

```bash
ssh docker-build 'cd /var/lib/container && sudo docker buildx inspect xqing-nvme1 && df -h / /var/lib/container /var/lib/containerd && findmnt -T /var/lib/containerd && lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINT'
```

Verified on 2026-09-27: the builder uses the `remote` driver at `unix:///run/buildkit/buildkitd.sock`. Its containerd worker stores content and snapshots under `/var/lib/containerd`, a bind mount from `/dev/nvme1n1[/containerd]`. The disk is mounted at `/var/lib/container`. BuildKit metadata under `/var/lib/buildkit` and Docker daemon storage under `/var/lib/docker` still use the root disk.

**Changing the build context directory alone does not move Docker storage.** Select `--builder xqing-nvme1` explicitly and use `--push`. Do not use `--load` when the root disk is low: it loads the image into the root-disk Docker daemon. The remote builder has a separate cache, so a base image cached by `docker images` may still need downloading on its first build.

This is a shared host. Do not format a disk, migrate Docker storage, restart daemons, create a replacement builder, or prune shared caches as a routine build step. If the builder or mount is missing, investigate and report it before changing infrastructure.

## 1. Registry login

The examples use the Harbor project **`skyinfer`**. A Harbor project is not a GitLab namespace. Confirm that this project exists and the account can push to it on `registry-cn-shanghai.siflow.cn`. Use existing root credentials where possible; check only whether the registry hostname is present, never print credential contents:

```bash
ssh docker-build 'cd /var/lib/container || exit 1
registry=registry-cn-shanghai.siflow.cn
if sudo grep -Fq "$registry" /root/.docker/config.json; then
  printf "%s: credential entry present\n" "$registry"
else
  printf "%s: credential entry missing or unreadable\n" "$registry"
  exit 1
fi'
```

If credentials need renewal, log in to `registry-cn-shanghai.siflow.cn` using the approved token through stdin or interactive login. A stored entry alone does not prove that credentials are valid or that push access is granted. Resolve missing access before starting the build. Do not hardcode secrets in scripts or build arguments. Every login/build/push command must use `sudo docker` so the same credentials are used.

## 2. Stage the context on NVMe

Use a task-specific directory under `/var/lib/container/xqing-builds/`. Keep the build context in `ctx/` and logs/control files alongside it. Respect the user's checkout restrictions: stage required build inputs, do not clone or create a new worktree without authorization. Keep credentials, checkpoints and unrelated experiment files out of the context.

```bash
REMOTE_DIR='/var/lib/container/xqing-builds/<unique-task>'
ssh docker-build "cd /var/lib/container && mkdir -p '$REMOTE_DIR/ctx'"
tar --exclude-vcs -czf - -C ./my-context . | ssh docker-build "cd '$REMOTE_DIR/ctx' && tar -xzf -"
```

The Dockerfile and every `COPY`/`ADD` input must be present. Use a focused context and `.dockerignore`. Tar over SSH works without remote rsync. Do not stage large contexts under `/tmp` or the root filesystem.

## 3. Build and push with the NVMe builder

Run in the staged context directory on `docker-build`:

```bash
IMAGE_PATH='skyinfer/<image>:<immutable-tag>'
sudo docker buildx build --builder xqing-nvme1 \
  --platform linux/amd64 --progress=plain \
  --provenance=false --sbom=false \
  --metadata-file ../build-metadata.json \
  -t "registry-cn-shanghai.siflow.cn/$IMAGE_PATH" \
  --push .
```

Prefer a date plus source commit for the tag; publish a moving `latest` tag only if requested. Pin the base image by digest when reproducibility matters. Add `--build-arg`, `-f`, `--pull` or `--no-cache` only when needed. Do not silently fall back to the default builder when the selected builder fails.

The image is pushed directly to `registry-cn-shanghai.siflow.cn` and need not appear in `sudo docker images`. Do not follow this with `sudo docker push`: that uses daemon-local tags and may push an older image with the same name. See the [Docker exporter documentation](https://docs.docker.com/build/exporters/image-registry/).

### Python package index: the Tsinghua mirror, not PyPI's CDN

From this box, PyPI's CDN (`files.pythonhosted.org`, Fastly `151.101.x`) is too slow for image builds. Measured on 2026-10-17, on the same 16–64 MB wheel ranges within the same hour:

| source | speed |
|---|---|
| `files.pythonhosted.org` (PyPI) | 20–64 KiB/s (about 1 MiB/s at best earlier that day; a torch + CUDA-wheel layer took 23 min) |
| `https://pypi.tuna.tsinghua.edu.cn/simple` | 7.6–12.2 MiB/s |
| `https://mirrors.aliyun.com/pypi/simple` | 3.1–4.5 MiB/s |
| `mirrors.cloud.aliyuncs.com` (Aliyun VPC endpoint) | unreachable |
| GitHub release assets; Ubuntu and NVIDIA apt repositories | 9.6 MiB/s; about 24 MB/s |

The host's own link was idle (52 KiB/s in total), so the bottleneck is the route to Fastly, and it drifts. Rules:

- Use `https://pypi.tuna.tsinghua.edu.cn/simple` for every pip or uv download in a build. If a download step looks slow, re-measure before blaming the build:
  - fetch a range of one wheel from each index (`curl -r 0-63999999 -o /dev/null -w '%{speed_download}'`);
  - check the host's `/proc/net/dev` rate.
- Pass the index as a build argument that the Dockerfile declares in each stage that downloads (`ARG PIP_INDEX_URL=https://pypi.org/simple` before the `RUN pip install`; uv reads `UV_DEFAULT_INDEX`). Then build with `--build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`. Do not bake the mirror into the image with `ENV` or `pip.conf`. The URL is recorded in the image history, which is acceptable because it is not a secret.
- Choose the index before the first build of a Dockerfile. Adding or changing the argument invalidates that `RUN` and every later layer. Switching mid-build costs a restart in a fresh run directory (§5).
- The mirror changes transport only. pip checks each file against the `#sha256=` its index lists, but version pins still do not pin bytes; byte-pin load-bearing packages (§7).
- GitHub and apt downloads are fast from this box and need no mirror.

## 4. Run long builds detached and record completion

Create `run-build.sh` beside `ctx/`, replacing the image path with the intended repository and immutable tag. The verification step uses Python 3 on the build host:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
trap 'rc=$?; printf "%s\n" "$rc" > build.status' EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP
command -v python3 >/dev/null
IMAGE_PATH='skyinfer/<image>:<immutable-tag>'
image="registry-cn-shanghai.siflow.cn/$IMAGE_PATH"
sudo docker buildx build --builder xqing-nvme1 \
  --platform linux/amd64 --progress=plain \
  --provenance=false --sbom=false \
  --metadata-file build-metadata.json \
  -f ctx/Dockerfile -t "$image" --push ctx
expected_digest=$(python3 -c 'import json; print(json.load(open("build-metadata.json"))["containerimage.digest"])')
if [[ ! "$expected_digest" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  printf 'Missing or invalid exporter digest\n' >&2
  exit 1
fi
sudo docker buildx imagetools inspect "$image" > image-inspect.txt
sudo docker buildx imagetools inspect --format '{{json .Manifest}}' "$image" > image-inspect.json
sudo docker buildx imagetools inspect --raw "$image" > image-manifest.json
python3 - image-manifest.json <<'PY'
import json
import sys

with open(sys.argv[1]) as source:
    manifest = json.load(source)
image_types = (
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
)
if manifest.get("mediaType") not in image_types or "manifests" in manifest:
    raise SystemExit("Expected one image manifest; found an index or unsupported artifact")
PY
actual_digest=$(python3 -c 'import json; print(json.load(open("image-inspect.json"))["digest"])')
if [[ "$actual_digest" != "$expected_digest" ]]; then
  printf '%s: digest mismatch (expected %s, got %s)\n' "$image" "$expected_digest" "$actual_digest" >&2
  exit 1
fi
printf 'Verified %s@%s\n' "$image" "$actual_digest"
```

Launch once from a fresh task directory. The braces keep `cd` and the PID capture in the intended shell:

```bash
ssh docker-build "cd '$REMOTE_DIR' && { nohup bash run-build.sh > build.log 2>&1 </dev/null & pid=\$!; printf '%s\n' \"\$pid\" > build.pid; cat build.pid; }"
ssh docker-build "cd '$REMOTE_DIR' && tail -n 20 build.log && if test -f build.status; then cat build.status; fi"
```

Record the remote directory, PID and log path. Check shortly after launch for immediate errors. Poll in short calls while continuing useful independent work. A missing `build.status` means completion is unconfirmed; read the log and process state. Lack of new log output alone does not prove a hang. On timeout or an interrupted turn, reconnect to the same job instead of launching another build. Stop polling once the recorded exit code is available and handle failures before retrying.

### Slow pushes into a new repository

A new image name can require transferring base layers even when the base image already exists in another repository on the same registry. Check transfer counters and target blob availability before assuming the exporter is stuck. Do not estimate push time from the small application diff alone.

If both repositories are authorized, the Registry V2 cross-repository blob mount API can reuse the exact existing digest. A successful mount returns 201; confirm the target blob with HEAD. Keep registry credentials in memory and never print or persist tokens. This is troubleshooting, not a required build step. Only after every required blob is available, a cached retry can avoid an already-running redundant upload. Identify the exact task client by PID, command and cwd before stopping it; never stop the BuildKit daemon or another user's build. Preserve the first log and exit status, then verify the retried publication normally.

## 5. Verify the published result

Require all of the following before reporting a successful image:

1. `build.status` is `0` and the build log has no unresolved failure.
2. `build-metadata.json` contains the exporter digest.
3. `sudo docker buildx imagetools inspect "registry-cn-shanghai.siflow.cn/$IMAGE_PATH"` resolves the published tag to the exporter digest and expected platform. Under the default single-image policy, the raw manifest must have an OCI image or Docker schema 2 image media type and no `manifests` array. An image index or attestation entries fail this requirement even when the digest matches. Save the inspection and manifest files; the [Docker inspection documentation](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/) describes the JSON manifest output. Run these checks through SSH with an explicit `cd`.
4. Run applicable build-time imports, source/version checks and CPU tests. On an authorized GPU machine, smoke-test model loading and generation when its container runtime is available. If GPU testing used the same source outside the final image, state that limitation explicitly.

Record the source commits, base digest, published image reference/digest and verification results. If the push or inspection fails, or the digest differs, report the failure and current publication state; do not claim success. Preserve the logs, inspect the Shanghai destination, resolve the cause, and use a fresh run directory for a deliberate retry with the same source, pinned inputs and tag. Verify the final digest again.

Registry inspection proves publication; a clean pull from a different authorized host provides an additional pull check. Do not claim a pull or GPU-container test that was not performed.

## 6. Cleanup on the shared host

Inspect disk use first. Remove only the task's own staging directory or explicitly identified artifacts after recording needed logs and digests. Keep reusable cache unless its ownership and impact are understood.

- Do not run blanket `docker system prune`, `docker builder prune`, `docker buildx prune` or `docker image prune`. Dangling objects and caches may still belong to other users.
- Removing a local image tag does not clean a remote builder's cache. Do not manually delete containerd content or snapshots.
- If cleanup is deferred, list the exact task directory that can be deleted.

## 7. Hard-won build gotchas (from real incidents on this box)

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

## Bundled legacy helper

`scripts/build-push.sh` uses the classic Docker daemon builder, accepts only one destination through `IMAGE`, and defaults to staging under `/tmp/dbuild`. It does **not** support the NVMe builder. Do not use it for the current workflow; use sections 2–5 above. Its existing options remain available for explicitly requested legacy builds targeting `registry-cn-shanghai.siflow.cn`, after reviewing storage and shared-host constraints.
