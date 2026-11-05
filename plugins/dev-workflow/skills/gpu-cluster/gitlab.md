# Internal GitLab

- Keep TLS certificate checks on. `gitlab-cn-beijing.siflow.cn` in old docs, scripts or locks is historical; for a dependency still pinned there, use its per-command URL override (such as `MEGATRON_REPO_URL`) rather than editing pins.
- On the nodes and gates, authentication comes from `/volume/.bashrc` and `/volume/.config`. `glab auth status` showing no login means nothing; test with a read-only request (`git ls-remote <url>` or `glab api projects/:id`).
- Run `glab` in the checkout so it infers the project: `glab issue view <iid>`, `glab mr list`, `glab api --paginate 'projects/:id/issues/<iid>/notes?sort=asc&per_page=100'` (without paging you get only the newest 20 notes). `glab api` has no `--jq`; pipe it to `jq`. `-R <group>/<project>` targets another repository.
- From this machine, GitLab goes through `sh-gate`'s proxy over the local tunnel `gate-proxy-tunnel.service` (`127.0.0.1:18080`); `glab` and Git already use it. For raw requests: `curl --proxy http://127.0.0.1:18080 --noproxy '' https://gitlab.iquest-inner.com/...`. Nodes and gates use their own network; don't copy this proxy to them.
- If access fails, check `systemctl status gate-proxy-tunnel.service` first.
- For one item of a tracking issue, write `#<N> item <X>` without a closing keyword.
