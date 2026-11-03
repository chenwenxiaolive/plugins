---
name: docker-build
description: >-
  Build Docker images on the shared remote build host (SSH alias `docker-build`) and publish
  them only to registry-cn-shanghai.siflow.cn. Use for building, tagging, pushing or verifying
  container images for this registry.
---

# Building & pushing Docker images on the remote build box

A playbook for driving image builds on a dedicated remote box from your control node (docker 26.1.3 + buildx, no local docker-group membership).

Publish only to `registry-cn-shanghai.siflow.cn`. Use one build invocation with an immutable tag. Completion requires successful publication and a published digest matching the build's exporter digest. Follow an explicit user request to build without pushing.

For each new build, publish one tagged `linux/amd64` image manifest. Pass `--provenance=false --sbom=false` to prevent BuildKit from adding an image index and extra attestation artifacts. This keeps the registry listing to one entry for the new build. See [Docker build attestations](https://docs.docker.com/build/metadata/attestations/). If the user explicitly requests attestations or multiple platforms, follow that request and adjust verification accordingly.

These flags affect new builds only. Existing registry artifacts remain for user-managed cleanup unless cleanup is explicitly requested.

Read [references/build-notes.md](references/build-notes.md) before writing or changing a Dockerfile, when a download or push is slow, and when a built image misbehaves at runtime. It holds the package-index measurements and incidents from this box.

## 0. Build host and storage

- SSH alias: `docker-build` (10.172.3.216), user `xqing`, x86_64. Every SSH command must explicitly `cd` before doing work.
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

Use a fresh task-specific directory under `/var/lib/container/xqing-builds/` for each build, including a deliberate retry. Keep the build context in `ctx/` and logs/control files alongside it. Respect the user's checkout restrictions: stage required build inputs, do not clone or create a new worktree without authorization. Keep credentials, checkpoints and unrelated experiment files out of the context.

```bash
REMOTE_DIR='/var/lib/container/xqing-builds/<unique-task>'
ssh docker-build "cd /var/lib/container && mkdir -p '$REMOTE_DIR/ctx'"
tar --exclude-vcs -czf - -C ./my-context . | ssh docker-build "cd '$REMOTE_DIR/ctx' && tar -xzf -"
```

`ctx/Dockerfile` and every `COPY`/`ADD` input must be present. Use a focused context and `.dockerignore`. Tar over SSH works without remote rsync. Do not stage large contexts under `/tmp` or the root filesystem.

## 3. Build, publish and check with the bundled script

This skill's [scripts/run-build.sh](scripts/run-build.sh) runs one `sudo docker buildx build --builder xqing-nvme1 --platform linux/amd64 --provenance=false --sbom=false --push` of `ctx/`, then inspects the published tag and requires a single image manifest whose digest equals the exporter digest in `build-metadata.json`. It records its exit code in `build.status`, also when killed (`143` for SIGTERM). Copy it beside `ctx/` and launch it detached; extra arguments go to `buildx build`:

```bash
IMAGE='registry-cn-shanghai.siflow.cn/skyinfer/<image>:<immutable-tag>'
SKILL_DIR='<this skill directory>'
ssh docker-build "cd -- $(printf %q "$REMOTE_DIR") && cat > run-build.sh" < "$SKILL_DIR/scripts/run-build.sh"
printf -v start \
  'cd -- %q && { nohup bash run-build.sh %q --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple > build.log 2>&1 </dev/null & printf "%%s\\n" "$!" > build.pid; cat build.pid; }' \
  "$REMOTE_DIR" "$IMAGE"
ssh docker-build "$start"
ssh docker-build "cd -- $(printf %q "$REMOTE_DIR") && tail -n 20 build.log && if test -f build.status; then cat build.status; fi"
```

- Prefer a date plus source commit for the tag; publish a moving `latest` tag only if requested. Pin the base image by digest when reproducibility matters. Add `--pull` or `--no-cache` only when needed. Do not silently fall back to the default builder when the selected builder fails.
- Use the Tsinghua index for every pip or uv download, passed as a build argument that each downloading stage declares (`ARG PIP_INDEX_URL=https://pypi.org/simple`; uv reads `UV_DEFAULT_INDEX`). Do not bake it in with `ENV` or `pip.conf`. Choose the index before the first build of a Dockerfile: changing the argument invalidates that `RUN` and every later layer.
- The image goes straight to the registry and need not appear in `sudo docker images`. Do not follow it with `sudo docker push`: that uses daemon-local tags and may push an older image with the same name. See the [Docker exporter documentation](https://docs.docker.com/build/exporters/image-registry/).
- Never pass a token through `--build-arg`: it is recorded expanded in the image history. Pass it with `--secret` and a BuildKit secret mount, as the build notes describe.
- For a requested build without a push, run the same `buildx build` command by hand without `--push`; there is nothing to verify in the registry.

Record the remote directory, PID and log path. Check shortly after launch for immediate errors. Poll in short calls while continuing useful independent work. A missing `build.status` means completion is unconfirmed; read the log and process state. Lack of new log output alone does not prove a hang. On timeout or an interrupted turn, reconnect to the same job instead of launching another build. Stop polling once the recorded exit code is available and handle failures before retrying.

## 4. Verify the published result

Require all of the following before reporting a successful image:

1. `build.status` is `0`, the log ends with `Verified <image>@<digest>`, and it has no unresolved failure. The script saved `build-metadata.json`, `image-inspect.txt`, `image-inspect.json` and `image-manifest.json` beside `ctx/`; the [Docker inspection documentation](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/) describes their format.
2. Run applicable build-time imports, source/version checks and CPU tests. On an authorized GPU machine, smoke-test model loading and generation when its container runtime is available. If GPU testing used the same source outside the final image, state that limitation explicitly.

Record the source commits, base digest, published image reference/digest and verification results. If the push or inspection fails, or the digest differs, report the failure and current publication state; do not claim success. Preserve the logs, inspect the Shanghai destination, resolve the cause, and use a fresh task directory for a deliberate retry with the same source, pinned inputs and tag. Verify the final digest again.

Registry inspection proves publication; a clean pull from a different authorized host provides an additional pull check. Do not claim a pull or GPU-container test that was not performed.

## 5. Cleanup on the shared host

Inspect disk use first. Remove only the task's own staging directory or explicitly identified artifacts after recording needed logs and digests. Keep reusable cache unless its ownership and impact are understood.

- Do not run blanket `docker system prune`, `docker builder prune`, `docker buildx prune` or `docker image prune`. Dangling objects and caches may still belong to other users.
- Removing a local image tag does not clean a remote builder's cache. Do not manually delete containerd content or snapshots.
- If cleanup is deferred, list the exact task directory that can be deleted.
