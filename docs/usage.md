# Using pstack for Codex

## First task

Open your project in a new Codex chat after [installation](installation.md). Explicitly select the skill or use its exact name:

```text
Use $poteto-mode to add a dark theme to this site.
Follow the project's existing design and theme conventions.
Infer completion criteria, explain key assumptions, and verify the visible result.
Keep changes local; do not commit, push, or deploy.
```

`poteto` is the upstream spelling. The main skill selects a playbook, investigates the code, plans the change, implements it, and gathers evidence appropriate to the goal. It may call other packaged skills as steps in that workflow.

You can supply only the goal. The agent should derive observable completion criteria from the goal and project: for example, readable text, consistent themed controls, preserved existing behavior, and an actual browser check for a visual feature. Product choices such as whether to add a new toggle may require your preference if the project does not already settle them. A build pass alone does not establish that the visible result works.

Useful optional context: relevant files, a reproduction, constraints, expected behavior, and the actions you authorize. You do not need to fill out a template. New tasks need an explicit invocation; continuing an active workflow can be as simple as a follow-up instruction.

## Smaller entrypoints

| Prompt | Expected purpose |
| --- | --- |
| `Use $poteto-help to choose a workflow for this task.` | Explain the best entrypoint without starting implementation merely because you asked for help |
| `Use $how to explain the login path. Do not modify files.` | Trace current behavior and explain it from source |
| `Use $interrogate to review this diff and report actionable findings.` | Review changes; independent reviewers depend on the host's delegation support |
| `Use $teach to explain why this change works.` | Explain the mechanism and reasoning |
| `Use $unslop to rewrite this paragraph while preserving its meaning.` | Improve prose |
| `Use $create-formal-verification-skill to check the retry queue's delivery invariant.` | In the development candidate, verify one property within explicit bounds and leave a reusable project skill |

See the complete [skill guide](../plugins/pstack-codex/skills/poteto-help/SKILL.md) and [playbook index](../plugins/pstack-codex/skills/poteto-mode/SKILL.md).

## Optional setup

```text
Use $setup-pstack. Keep every role on the inherited model and explain the defaults.
```

Setup manages optional project preferences in `.codex/pstack/config.json`. This is a plugin convention, not a native global Codex model-routing setting. Without it, roles inherit the current model and reasoning configuration. Explicit overrides require both a real available model and host support.

Review panels and repeated attempts consume additional usage. The plugin does not bypass account limits, host permissions, or repository instructions.

Setup offers a missing app verification workflow and a missing formal verification workflow once each. Accepting one starts its generator; declining does not block setup. The formal verification skill chooses a tool from the property and code. Generated-input tests are a fallback when no suitable code verifier exists and must not be reported as a formal proof.

## Capability boundaries

- Delegation, UI tools, connectors, and scheduling vary by host. Missing capabilities must be reported. Sequential checks are not independent reviewers.
- Most skills are explicit-only; setup is the sole implicitly discoverable entry. Installation does not activate every workflow automatically.
- Your request defines the scope. A question about a workflow does not authorize implementation. Publishing, external messages, and destructive operations still need applicable authorization.
- A request to continue a current task does not create a recurring timer. `$automate-me` builds a personal workflow skill; it is not a scheduling command.
- `make-bot-ui` can help specify a bot UI, but its original service-specific webhook/state integration is deferred.
- Installation does not include the maintainer's Cloud environment or an upstream updater. The [maintenance workflow](automation-options.md) is separate.

If a run goes wrong, name the failed behavior and the evidence you expected. Report a reproducible issue with the plugin version, host, relevant prompt, and sanitized output. Do not include tokens, private transcripts, or account-specific environment identifiers.
