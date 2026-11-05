---
type: llm
---

PASS if the plan stages the build context on the docker-build host in a fresh directory, starts the skill's run-build.sh there detached, tags the image registry-cn-shanghai.siflow.cn/skyinfer/infer-server with an immutable tag (date and commit, not only latest), and treats build.status 0 with a `Verified <image>@<digest>` log line as success.
FAIL if it builds on this machine, pushes with a separate `docker push`, or tags only latest.
