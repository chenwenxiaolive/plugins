---
name: docker-build
description: "Builds Docker images on the shared build host (SSH alias docker-build) and publishes them only to registry-cn-shanghai.siflow.cn. Use when building, tagging, pushing or verifying container images for that registry."
---

# Docker builds on the build host

Build on the shared host `docker-build` and publish only to
`registry-cn-shanghai.siflow.cn`: one `linux/amd64` image manifest per build, with
an immutable tag (date plus source commit; `latest` only on request). A build is
done when the registry serves the exporter's digest. Follow an explicit request to
skip the push, add attestations or build more platforms.

Read [references/build-notes.md](references/build-notes.md) before writing or
changing a Dockerfile, when a download or push is slow, or when an image misbehaves
at runtime: it holds this host's facts, measurements and incidents.

## Host

- `docker-build` is an SSH alias for user `xqing` on an x86_64 VM without GPUs, reached through `sh-gate`. Every ssh command starts with a `cd`. Docker runs as `sudo docker` (passwordless), so registry credentials are root's `/root/.docker/config.json`; check only that the registry's entry exists (`sudo grep -Fq registry-cn-shanghai.siflow.cn /root/.docker/config.json`), never print it. An entry doesn't prove push access to the Harbor project (`skyinfer` in the examples).
- Build with the `default` builder: the docker driver, whose BuildKit runs in the daemon and keeps images in its containerd image store under `/data/docker`. A build therefore also leaves its image in the local store, and `--push` publishes that same manifest digest. Pin bases by digest when reproducibility matters. Check the host first with `sudo docker buildx inspect default` and `df -h / /data`.
- The host is shared, with other users' images and containers: don't format disks, migrate storage, restart daemons, change the daemon configuration or run any `docker ... prune`. Remove only your own tags, and report a missing builder or a full disk instead.

## Build

1. Stage the context in `ctx/` of a fresh directory per build or retry (`mkdir -p ~/builds && mktemp -d ~/builds/<task>-$(date +%Y%m%d)-XXXXXX`): `tar --exclude-vcs -czf - -C <context> . | ssh docker-build "cd <dir>/ctx && tar -xzf -"`, or pipe `git archive <commit>` to `tar -xf -` for a committed tree. Keep it focused (`.dockerignore`) and free of credentials and checkpoints.
2. Copy [scripts/run-build.sh](scripts/run-build.sh) beside `ctx/` and start it detached. It runs one `buildx build --builder default --platform linux/amd64 --provenance=false --sbom=false --push`, checks that the tag serves a single manifest with the exporter digest, and writes `build.status` (including `143` when killed). Extra arguments go to `buildx build`:

   ```bash
   ssh docker-build "cd -- $(printf %q "$REMOTE_DIR") && cat > run-build.sh" < "$SKILL_DIR/scripts/run-build.sh"
   printf -v start 'cd -- %q && { nohup bash run-build.sh %q > build.log 2>&1 </dev/null & echo $! > build.pid; }' "$REMOTE_DIR" "$IMAGE"
   ssh docker-build "$start"
   ```

3. Poll `build.log` and `build.status` in short calls. Without `build.status` the result is unknown; reconnect to the same build rather than starting another.

- Use the default package indexes: PyPI's CDN measured faster here than the mirrors. If a download step is slow, measure before switching (build notes), and pass a mirror only as a build argument that each downloading stage declares (`ARG PIP_INDEX_URL`; uv reads `UV_DEFAULT_INDEX`), never as `ENV` or `pip.conf`. Changing it invalidates that layer and all later ones.
- Never pass a token with `--build-arg`: it is recorded in the image history. Use `--secret` (build notes).
- Publish only through `run-build.sh`, not with a later `docker push` of a local tag, which may name an older image.
- A build without a push is the same `buildx build` by hand without `--push`; its image stays in the local store under its tag.

## Verify and clean up

- Success needs `build.status` `0` and a log ending in `Verified <image>@<digest>`. Then run the checks that apply (imports, versions, CPU tests) in the local image with `sudo docker run --rm --network=none`, and, on a GPU node the user named, a smoke test; say when GPU testing used the source outside the image.
- Report the source commits, base digest, image reference and digest, and what was verified. On failure, report the publication state; retry in a fresh directory with the same inputs and tag.
- Remove only this build's directory once its logs and digest are recorded, and its local tags (`sudo docker image rm <tag>`) once nobody needs the image on this host.
