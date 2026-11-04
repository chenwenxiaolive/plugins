#!/usr/bin/env bash
# Build and publish one linux/amd64 image with the default builder, then check that
# the registry serves a single image manifest with the exporter's digest.
#
# Run on docker-build from a task directory whose ctx/ holds the build context:
#   bash run-build.sh registry-cn-shanghai.siflow.cn/<project>/<name>:<tag> [buildx args...]
# Extra arguments such as --build-arg, --pull or --no-cache go to `docker buildx build`.
# Writes build.status (the exit code), build-metadata.json, image-inspect.txt,
# image-inspect.json and image-manifest.json beside ctx/.
set -euo pipefail
cd -- "$(dirname -- "$0")"
trap 'rc=$?; printf "%s\n" "$rc" > build.status' EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
trap 'exit 129' HUP

image=${1:-}
case $image in
  registry-cn-shanghai.siflow.cn/*/*:*) shift ;;
  *)
    printf 'usage: %s registry-cn-shanghai.siflow.cn/<project>/<name>:<tag> [buildx args...]\n' "$0" >&2
    exit 2
    ;;
esac
command -v python3 >/dev/null
test -f ctx/Dockerfile || { printf 'ctx/Dockerfile is missing\n' >&2; exit 1; }

sudo docker buildx build --builder default \
  --platform linux/amd64 --progress=plain \
  --provenance=false --sbom=false \
  --metadata-file build-metadata.json \
  -f ctx/Dockerfile -t "$image" --push "$@" ctx

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
