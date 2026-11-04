---
name: docker-build
description: >-
  Build Docker images on the shared remote build host (SSH alias `docker-build`) and publish
  them only to registry-cn-shanghai.siflow.cn. Use for building, tagging, pushing or verifying
  container images for this registry.
---

# Docker builds

Build on the shared host `docker-build` and publish only to
`registry-cn-shanghai.siflow.cn` (Harbor project `skyinfer`): one `linux/amd64` image
manifest per build, with an immutable tag (date plus source commit; `latest` only on
request). A build is done when the registry serves the digest the build exported.

## Host (checked 2026-11-03)

- SSH alias for user `xqing` at 10.161.41.7, reached through `sh-gate`; passwordless `sudo`. Ubuntu 22.04, 192 CPUs, 2 TiB RAM, no GPU. `/` (1 TB) holds home and build contexts; `/data` (7 TB) is Docker's root.
- Docker 29.5.2 with the containerd image store. Use the `default` builder (docker driver, BuildKit 0.30): a build also lands in the local store, and `--push` publishes the same digest.
- Docker runs as `sudo docker`, so registry credentials are root's `/root/.docker/config.json`. Check only that the registry entry exists; never print it.
- The host is shared: no `docker ... prune`, daemon restarts or configuration changes. Remove only your own tags and build directories.

## Build

```bash
sudo docker buildx build --builder default --platform linux/amd64 --provenance=false --sbom=false \
  --push --metadata-file build-metadata.json -t <image> ctx
```

- Stage the context in a fresh `~/builds/<task>-<date>-XXXXXX/ctx` per build: `git archive <commit>` or a tar over ssh, without credentials or checkpoints.
- Run the build detached, as gpu-cluster describes for `run.sh`: traps record `build.status`, and you reconnect instead of rebuilding.
- Publish only with `--push`. A later `docker push` of a local tag may send an older image.
- Verify: `sudo docker buildx imagetools inspect <image>` must show a single manifest (no index) whose digest equals `containerimage.digest` in `build-metadata.json`. Then check imports and versions with `sudo docker run --rm --network=none <image> ...`.

## What builds have taught

- PyPI's CDN is the fastest index here (29 MiB/s, against 13 for Tsinghua and 4.5 for Aliyun). Routes drift: the previous host got 20–64 KiB/s from PyPI. Measure a 64 MB range from each index before switching, and pass a mirror only as a declared `ARG PIP_INDEX_URL` (uv reads `UV_DEFAULT_INDEX`); changing it invalidates that layer and all later ones.
- BuildKit `RUN` steps start with a soft `nofile` limit of 1024 and ignore `--ulimit`. `uv` with `UV_COMPILE_BYTECODE=1` dies with "No file descriptors available". Raise the limit inside the step (`ulimit -n 65536 && ...`) or set `UV_COMPILE_BYTECODE=0`.
- Same version doesn't mean same bytes. A silently re-released `nvidia-cutlass-dsl==4.5.2` main wheel, paired with older `-libs`, passed the build and crashed at the first GPU JIT. Byte-pin load-bearing packages: copy a known-good tarball in and assert an md5 in the same `RUN`. Take package families from one release, and diff file hashes before theorizing about "same pip list, different behavior".
- The host has no GPU, so lazily compiled kernels (CuTe-DSL, triton autotune) first run on the deploy node. Assert what you can at build time, and smoke-test on a GPU node the user names.
- A `--build-arg` token is recorded, expanded, in the image history, and a token in a clone URL stays in `.git/config`. Use `RUN --mount=type=secret,id=gitlab_token` with `--secret id=gitlab_token,src=<file>`, reset the clone's remote URL, and check `sudo docker history --no-trunc <image> | grep -c glpat-` is 0 before pushing.
- A new repository name can re-upload base layers that exist elsewhere in the registry; a 6.5 GB push took about 108 s. If it stalls, the Registry V2 cross-repository blob mount can reuse an existing digest (201 on success).
