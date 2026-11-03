---
name: docker-build
description: >-
  Build Docker images on the shared remote build host (SSH alias `docker-build`) and publish
  them only to registry-cn-shanghai.siflow.cn. Use for building, tagging, pushing or verifying
  container images for this registry.
---

# Docker builds on the build host

Build on the shared host `docker-build` and publish only to
`registry-cn-shanghai.siflow.cn`: one `linux/amd64` image manifest per build, with
an immutable tag (date plus source commit; `latest` only on request). A build is
done when the registry serves the exporter's digest. Follow an explicit request to
skip the push, add attestations or build more platforms.

Read [references/build-notes.md](references/build-notes.md) before writing or
changing a Dockerfile, when a download or push is slow, or when an image misbehaves
at runtime: it holds this host's measurements and incidents.

## Host

- `docker-build` (10.172.3.216), user `xqing`, x86_64. Every ssh command starts with a `cd`. Docker runs as `sudo docker` (passwordless), so registry credentials are root's `/root/.docker/config.json`; check only that the registry's entry exists (`sudo grep -Fq registry-cn-shanghai.siflow.cn /root/.docker/config.json`), never print it. An entry doesn't prove push access to the Harbor project (`skyinfer` in the examples).
- Build with the existing `xqing-nvme1` builder (remote BuildKit driver, content on the NVMe disk at `/var/lib/container`) and `--push`. `--load` would fill the root disk. The builder has its own cache, so a base image in `docker images` may still be downloaded on its first build; pin the base by digest when reproducibility matters. Check it first with `sudo docker buildx inspect xqing-nvme1` and `df -h / /var/lib/container`.
- The host is shared: don't format disks, migrate storage, restart daemons, replace the builder or run any `docker ... prune`. Report a missing builder or mount instead.

## Build

1. Stage the context in a fresh `/var/lib/container/xqing-builds/<task>/ctx` per build or retry: `tar --exclude-vcs -czf - -C <context> . | ssh docker-build "cd <dir>/ctx && tar -xzf -"`. Keep it focused (`.dockerignore`) and free of credentials and checkpoints.
2. Copy [scripts/run-build.sh](scripts/run-build.sh) beside `ctx/` and start it detached. It runs one `buildx build --builder xqing-nvme1 --platform linux/amd64 --provenance=false --sbom=false --push`, checks that the tag serves a single manifest with the exporter digest, and writes `build.status` (including `143` when killed). Extra arguments go to `buildx build`:

   ```bash
   ssh docker-build "cd -- $(printf %q "$REMOTE_DIR") && cat > run-build.sh" < "$SKILL_DIR/scripts/run-build.sh"
   printf -v start 'cd -- %q && { nohup bash run-build.sh %q --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple > build.log 2>&1 </dev/null & echo $! > build.pid; }' "$REMOTE_DIR" "$IMAGE"
   ssh docker-build "$start"
   ```

3. Poll `build.log` and `build.status` in short calls. Without `build.status` the result is unknown; reconnect to the same build rather than starting another.

- Pass the Tsinghua index as a build argument that each downloading stage declares (`ARG PIP_INDEX_URL`; uv reads `UV_DEFAULT_INDEX`), never as `ENV` or `pip.conf`. Changing it invalidates that layer and all later ones.
- Never pass a token with `--build-arg`: it is recorded in the image history. Use `--secret` (build notes).
- Don't run `docker push` afterwards: it pushes daemon-local tags, possibly an older image. Don't fall back to the default builder.
- A build without a push is the same `buildx build` by hand without `--push`.

## Verify and clean up

- Success needs `build.status` `0` and a log ending in `Verified <image>@<digest>`. Then run the checks that apply (imports, versions, CPU tests) and, on a GPU node the user named, a smoke test; say when GPU testing used the source outside the image.
- Report the source commits, base digest, image reference and digest, and what was verified. On failure, report the publication state; retry in a fresh directory with the same inputs and tag.
- Remove only this build's directory, once its logs and digest are recorded.
