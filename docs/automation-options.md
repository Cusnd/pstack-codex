# Maintainer automation

Installing the plugin does not install an updater or create a Cloud environment. This repository contains preparation tools and a [maintenance prompt](../cloud/update-task.md). The maintainer configures recurring execution separately through the actual host's scheduling tool after verifying that host. The schedule registry, not a sentence in this repository, determines whether a task is enabled.

## Accepted state and candidates

`upstream.lock.json` records the accepted upstream commit, pstack subtree, and source version. `scripts/probe_upstream.py` compares a newly pinned upstream subtree without changing that lock. `scripts/prepare_update.py` places a changed snapshot and binary diff beneath ignored `work/candidates/` and leaves accepted state untouched.

Adaptation compares the accepted source, candidate source, and maintained plugin. It preserves workflow coverage, validates the package, and opens a draft PR. The accepted lock changes only in the reviewed adaptation. Repeated detection of the same tree must reuse or report the existing candidate instead of creating duplicate work.

Preparation publishes a candidate only after its source, patch, and receipt are complete. A repeated run verifies those files against the pinned Git source and reuses them without rewriting them. A damaged or incomplete candidate fails with an error and remains available for inspection. Unrelated upstream commits with the same pstack tree reuse the original candidate commit. Detection and preparation never advance the accepted lock.

## Cloud setup

1. Create an environment scoped to this repository using the host's supported setup flow.
2. Use [cloud/install.sh](../cloud/install.sh) for the development runtimes and [start-skill.md](../cloud/start-skill.md) for startup guidance. The installer resolves its checkout from its own path; the Python environment and pinned Bun runtime remain local to that checkout. Subsequent commands use `.venv/bin/python` and add `work/tools/node_modules/.bin` to PATH.
3. Configure network destinations through environment settings. See [networking.md](../cloud/networking.md); Git and GitHub API access are separate checks.
4. Validate commands in a fresh ordinary Cloud task after publishing the configuration.
5. Run the bounded [proof procedure](../cloud/proof-request.md) only when its one-off callback is explicitly authorized.
6. Before recurring maintenance, rehearse a changed candidate through draft-PR creation and duplicate-run handling. Then explicitly authorize the recurring schedule.

Keep environment IDs, chat IDs, schedule IDs, and raw receipts in local ignored working files or another private operational store. Public verification should describe commands, outcomes, and limitations without those personal identifiers.

## Execution and scheduling

A native scheduled continuation executed repository commands during development. Availability and its execution destination still need verification in each account and host. An initial run does not prove that a scheduled run executed, and a timer firing does not prove that an update succeeded.

A separately verified ChatGPT Work conversation can also run the maintenance prompt with its shell and authorized GitHub connector. Treat Work and Codex Cloud as separate hosts. In Work, a missing scratch checkout can be reconstructed from the public repository into a fresh task directory; never assume that scratch files persist or reset an unrelated checkout. Read the repository instructions and verify Git, public GitHub API, and push access before claiming an update can be delivered.

Each run records a UTC start/end time, accepted and candidate source SHAs, outcome, PR URL when present, and actual command failures in ignored `work/maintenance-status.json`. Preserve the last successful check time on failure. Use remote branches and all-state PRs as the durable duplicate-work registry. Record `unchanged`, `existing_pr`, `draft_pr_created`, `blocked`, or `error`; a failed probe is never `unchanged`. Notify only for a new proposal, a meaningful change, or an actionable failure.

The maintainer task stops at a draft PR. Review and merge advance main; a separately authorized release publishes a new tag and ZIP. Existing installations pinned to an older tag require an explicit upgrade. Do not call any of those later stages complete merely because a maintenance task ran.

Native schedules can invoke a model even when there is no source change. If avoiding those invocations is a requirement, evaluate a separate read-only detector and a supported Cloud dispatch mechanism. An external timer alone does not establish access to the coding environment. No external dispatcher is configured by this repository.

Official references: [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments), [scheduled tasks](https://learn.chatgpt.com/docs/automations), and [developer commands](https://learn.chatgpt.com/docs/developer-commands). Use the actual current tools and schemas; do not infer an environment ID from a chat ID or invent a dispatch endpoint.
