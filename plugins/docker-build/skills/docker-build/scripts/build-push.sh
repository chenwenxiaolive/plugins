#!/usr/bin/env bash
# build-push.sh — copy a build context to the remote docker box, then build (+push) an image
# DETACHED on the box, streaming the log to completion. Exits with the build's real return code.
# Legacy single-destination helper. Use SKILL.md sections 2–5 for the current NVMe
# workflow that publishes only to registry-cn-shanghai.siflow.cn.
#
# Usage:
#   IMAGE=registry-cn-shanghai.siflow.cn/<project>/<name>:<tag> build-push.sh [CONTEXT_DIR]
#
# Env:
#   IMAGE         (required) full image ref incl. registry + tag
#   CONTEXT       build context dir            (default: $1, else ".")
#   DOCKERFILE    Dockerfile path, rel. to CONTEXT or absolute (default: Dockerfile)
#   HOST          ssh alias of the build box   (default: docker-build)
#   REMOTE_DIR    staging base on the box      (default: /tmp/dbuild/<sanitized-image>)
#   PUSH          1=build+push (default), 0=build only
#   NO_CACHE      1 => add --no-cache
#   PULL          1 => add --pull (refresh base image)
#   BUILD_ARGS    extra args passed verbatim to `docker build` (e.g. "--build-arg K=V")
#   POLL_TIMEOUT  seconds to wait for completion (default 3600)
#   POLL_INTERVAL seconds between polls          (default 6)
#   ATTACH        1 => skip copy+launch, just stream an ALREADY-RUNNING build's log to completion —
#                 use after a poll TIMEOUT (exit 124); the same IMAGE resolves to the same log path
#   MIN_FREE_GB   preflight: warn if the box has under this many GB free on / (default 20)
#
# docker on the box runs via sudo (the user is not in the docker group); creds live in /root/.docker.
# One-time login:  ssh -t "$HOST" 'sudo docker login registry-cn-shanghai.siflow.cn -u <user>'
set -euo pipefail

IMAGE="${IMAGE:?set IMAGE=registry-cn-shanghai.siflow.cn/<project>/<name>:<tag>}"
CONTEXT="${1:-${CONTEXT:-.}}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
HOST="${HOST:-docker-build}"
PUSH="${PUSH:-1}"
ATTACH="${ATTACH:-0}"
POLL_TIMEOUT="${POLL_TIMEOUT:-3600}"
POLL_INTERVAL="${POLL_INTERVAL:-6}"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=no"

# docker treats the part before the first "/" as a registry host only if it contains "." or ":" —
# without one, `docker push` silently targets docker.io instead of the private registry.
imghost=""; case "$IMAGE" in */*) imghost="${IMAGE%%/*}";; esac
case "$imghost" in
  *.*|*:*|localhost) ;;
  *) echo "WARN: IMAGE '$IMAGE' has no registry host — a push would go to docker.io." >&2
     echo "      expected e.g. registry-cn-shanghai.siflow.cn/<project>/<name>:<tag>" >&2 ;;
esac

[ "$ATTACH" = 1 ] || [ -d "$CONTEXT" ] || { echo "context dir not found: $CONTEXT" >&2; exit 2; }
safe=$(printf %s "$IMAGE" | tr '/:@ ' '____')
REMOTE_DIR="${REMOTE_DIR:-/tmp/dbuild/$safe}"
CTX="$REMOTE_DIR/ctx"          # the build context (kept separate so control files never enter the image)
LOG="$REMOTE_DIR/build.log"

# single-quote-escape a value for safe embedding in a remote command
qq() { printf "'%s'" "$(printf %s "$1" | sed "s/'/'\\\\''/g")"; }

extra=""
[ "${NO_CACHE:-0}" = 1 ] && extra="$extra --no-cache"
[ "${PULL:-0}" = 1 ]     && extra="$extra --pull"
[ -n "${BUILD_ARGS:-}" ] && extra="$extra $BUILD_ARGS"

if [ "$ATTACH" = 1 ]; then
  echo ">> ATTACH=1 — skipping copy+launch; streaming the existing build log"
  $SSH "$HOST" "test -f $(qq "$LOG")" \
    || { echo "no log at $HOST:$LOG — nothing to attach to (same IMAGE/REMOTE_DIR as the original run?)" >&2; exit 2; }
else
  # preflight: the box is shared — a full disk fails builds halfway with confusing errors
  free_gb=$($SSH "$HOST" "df -BG --output=avail / 2>/dev/null | tail -1 | tr -dc 0-9" 2>/dev/null || true)
  if [ -n "$free_gb" ] && [ "$free_gb" -lt "${MIN_FREE_GB:-20}" ]; then
    echo "WARN: only ${free_gb}G free on $HOST:/ — consider: ssh $HOST 'sudo docker builder prune -f' (surgical; see SKILL §6)" >&2
  fi

  # ---- [1/3] copy context up (rsync if available on both ends, else tar-over-ssh) ----
  echo ">> [1/3] copy $CONTEXT/ -> $HOST:$CTX/"
  if command -v rsync >/dev/null 2>&1 && $SSH "$HOST" 'command -v rsync >/dev/null 2>&1'; then
    $SSH "$HOST" "mkdir -p $(qq "$CTX")"
    rsync -az --delete -e "$SSH" --exclude '.git' "$CONTEXT"/ "$HOST:$CTX"/
  else
    echo "   (rsync not on both ends — using tar over ssh; context dir wiped first for clean state)"
    $SSH "$HOST" "rm -rf $(qq "$CTX") && mkdir -p $(qq "$CTX")"
    tar -C "$CONTEXT" --exclude-vcs -czf - . | $SSH "$HOST" "tar -C $(qq "$CTX") -xzf -"
  fi

  # ---- [2/3] compose the remote build script locally (no cross-shell quoting), ship via base64, launch detached ----
  # The sentinel line carries the real exit code so the poller can read it unambiguously.
  tmp=$(mktemp)
  {
    echo '#!/usr/bin/env bash'
    echo "cd $(qq "$CTX") || exit 3"
    echo 'rc=0'
    echo "sudo docker build$extra -t $(qq "$IMAGE") -f $(qq "$DOCKERFILE") . || rc=\$?"
    [ "$PUSH" = 1 ] && echo "[ \$rc = 0 ] && { sudo docker push $(qq "$IMAGE") || rc=\$?; }"
    echo 'echo "__DBUILD_DONE__ rc=$rc"'
  } > "$tmp"

  echo ">> [2/3] launch detached on $HOST  (PUSH=$PUSH, image=$IMAGE)"
  $SSH "$HOST" "mkdir -p $(qq "$REMOTE_DIR") && rm -f $(qq "$LOG")"
  base64 < "$tmp" | tr -d '\n' | $SSH "$HOST" "base64 -d > $(qq "$REMOTE_DIR/dbuild.sh")"
  rm -f "$tmp"
  $SSH "$HOST" "cd $(qq "$REMOTE_DIR") && nohup bash dbuild.sh > $(qq "$LOG") 2>&1 </dev/null & echo pid=\$!"
fi

# ---- [3/3] stream the log until the sentinel appears (or timeout) ----
echo ">> [3/3] stream $LOG (timeout ${POLL_TIMEOUT}s)"
start=$(date +%s); prev=0
flush() {  # print new log lines since $prev
  local n; n=$($SSH "$HOST" "wc -l < $(qq "$LOG") 2>/dev/null || echo 0"); n=${n//[!0-9]/}; n=${n:-0}
  if [ "$n" -gt "$prev" ]; then
    $SSH "$HOST" "sed -n '$((prev+1)),\$p' $(qq "$LOG") 2>/dev/null" || true
    prev="$n"
  fi
}
while :; do
  flush
  if $SSH "$HOST" "grep -q '__DBUILD_DONE__' $(qq "$LOG") 2>/dev/null"; then
    flush
    rc=$($SSH "$HOST" "grep '__DBUILD_DONE__' $(qq "$LOG") | tail -1 | sed 's/.*rc=//' | tr -dc 0-9" || true)
    rc=${rc:-1}
    if [ "$rc" = 0 ]; then echo ">> SUCCESS  $IMAGE  (rc=0)"
    else echo ">> FAILED  rc=$rc  — inspect: ssh $HOST \"tail -50 $LOG\"" >&2; fi
    exit "$rc"
  fi
  if [ $(( $(date +%s) - start )) -gt "$POLL_TIMEOUT" ]; then
    echo ">> TIMEOUT after ${POLL_TIMEOUT}s — build may still be running on $HOST (log: $LOG)" >&2
    echo ">> re-attach without rebuilding:  ATTACH=1 IMAGE=$IMAGE bash $0" >&2
    exit 124
  fi
  sleep "$POLL_INTERVAL"
done
