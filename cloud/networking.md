# Cloud network execution

Two independent gates apply to command networking: the command sandbox must permit network access, and the managed proxy must allow the destination. A connected environment does not grant network access to every shell invocation.

## Supported execution mode

Inspect the exec tool schema supplied by the current host. In the verified regular Cloud chat, network commands use `sandbox_permissions: "with_additional_permissions"` and `additional_permissions: {"network": {"enabled": true}}`. The environment setup chat exposed only `use_default` and `require_escalated`, and its default execution already permitted network. Use additional permission parameters only where the actual tool exposes them. Local desktop exec tools also have a different schema; do not copy these parameters blindly.

Apply the supported network mode to Git fetch/push, GitHub API requests, dependency installation, and the Python probe/preparation commands. Keep inherited proxy and certificate settings. Do not bypass the proxy, disable TLS verification, copy authentication files, or edit `/etc/codex/network-policy.json` to grant access.

## Destination policy

The updater needs GitHub repository access and the exact API hostname `api.github.com`. A package-manager preset may allow `github.com` without allowing `api.github.com`; inspect the current preset instead of assuming both are included. Add missing destinations through environment settings. Repository authentication remains managed by the host. Public upstream API reads do not require a personal secret.

Change destinations only through the supported environment configuration flow. Save, test, and republish the environment. Existing chats can retain older environment state; inspect their active policy and test their actual requests rather than assuming publication updated them.

## Distinguish failures

| Observed result | Meaning | Next step |
| --- | --- | --- |
| Local socket `EPERM` / operation not permitted, curl 7 / HTTP 000 | Command sandbox may not permit network; this alone does not establish a broken proxy | Retry using the current tool's supported network-enabled mode |
| Proxy `CONNECT tunnel failed, response 403` | Destination was denied before the origin was reached | Inspect the active allowlist and repair the precise destination through environment settings |
| Origin HTTP 401/403 after a successful tunnel | Origin authentication, authorization, or rate limit failure | Inspect the non-secret response; do not confuse it with proxy policy |
| Probe exits 2 / `ok: false` | The check failed | Record an error; never treat it as unchanged |

After changes, run `git ls-remote origin HEAD`, a public GitHub API request, and `python scripts/probe_upstream.py` in the Cloud runtime. A local Windows success is not a substitute. A scheduled network callback is a separate verification of unattended execution.
