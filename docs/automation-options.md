# Native scheduling before an external dispatcher

Research checked on 2026-10-15 (America/Los_Angeles). This is a feasibility record, not a deployed automation.

The desired workflow is: read the `pstack` subtree SHA in `cursor/plugins`, compare it with the accepted source tree, adapt a changed pinned snapshot in a cloud coding environment, run checks, and return a draft pull request. A persistent external machine is not inherently required.

## Separate the three responsibilities

| Responsibility | Native candidate | External fallback |
| --- | --- | --- |
| Wake up | ChatGPT web scheduled task or supported GitHub event | Cloudflare Cron Trigger |
| Decide whether work exists | Read the pinned subtree SHA and accepted lock using connected tools | Worker calls GitHub APIs and compares the subtree SHA |
| Execute the adaptation | A scheduled continuation of a chat in the intended Codex Cloud environment, if verified | A supported Cloud submission interface; a short-lived CLI bridge only if necessary |

Neither a timer nor a tree comparison needs a model. If a native scheduled chat invokes a model on every tick, it cannot meet the stricter optimization of zero model invocations while the upstream tree is unchanged. This is a tradeoff to measure, not a reason to claim native scheduling is unavailable.

## What official documentation establishes

[Scheduled tasks](https://learn.chatgpt.com/docs/automations) supports web schedules and returning to an existing chat. Supported GitHub events concern pull request activity, including commit updates and merges; the list does not establish an arbitrary third-party repository path/tree-change trigger. Availability depends on the account and workspace. Desktop project tasks depend on a running computer.

[Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments) supplies repository workspaces and runs while the local computer is asleep. The scheduling documentation does not explicitly establish that a scheduled chat continuation preserves this particular execution environment. Verify that combination with an actual run before promising it.

[GitHub integration](https://learn.chatgpt.com/docs/third-party/github) can start a Legacy Cloud chat from a non-review `@codex` PR comment. It is not the same integration as the new Cloud environment flow. A human comment working does not prove that a bot-generated comment is accepted.

[CLI commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-cloud) documents `codex cloud exec` and `codex cloud list`. The installed CLI is 0.160.0. An empty task list does not prove that no cloud environments exist, and CLI compatibility with a newly published environment remains an execution test.

## Cloudflare's role if native scheduling is insufficient

[Workers Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/) can invoke a scheduled handler that calls GitHub. No continuously running VPS is needed. A Workflow can persist coordination and retries if the process needs multiple steps.

The Workers runtime is not a general Linux process host. Its Node child-process support must not be treated as permission to execute the native Codex CLI. A CLI-only submission path would require a process host such as a short-lived container or CI runner. That bridge submits and observes a Cloud task; it does not need to perform the adaptation itself.

[Cloudflare's Codex sandbox guide](https://developers.cloudflare.com/sandbox/coding-agents/codex/) instead runs `codex exec` inside Cloudflare using an API/gateway setup. This changes the execution product and authentication/billing path. It is an alternative, not evidence that a plain Worker can start a task in the user's ChatGPT Codex Cloud environment.

## Acceptance test before choosing infrastructure

1. Publish a private environment containing only `Cusnd/pstack-codex`.
2. Start a bounded task which records its repository, branch, HEAD, Python and Git versions, reads the lock, and runs metadata validation. Do not install this unfinished plugin into the user's account.
3. Establish whether the same Cloud chat can schedule a continuation. Inspect the resulting schedule, environment identity, and actual run evidence. A reminder or connector-only summary is insufficient.
4. Test no-change and changed-tree cases. Keep accepted source state separate from detected or in-flight state; advance the accepted lock only with the reviewed adaptation.
5. If the native route fails, record the exact unsupported operation. Only then select a Cloudflare dispatcher and the smallest supported submission bridge.

No Cloudflare resource, recurring schedule, release, automatic merge, or personal plugin installation has been enabled by this document.
