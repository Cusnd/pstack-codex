# pstack for Codex

A Codex adaptation of [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack): skills for understanding code, planning changes, implementing them, and checking the result against the user's goal.

**Development candidate: `0.1.0-alpha.3` (pending publication).** This checkout tracks upstream 0.15.32 and includes all 58 skills. 57 have adapted instructions; `make-bot-ui` remains a planning-only entry because its original service integration is unavailable. Script checks are automated, but every agent workflow has not been exercised in every host. See [verification and limitations](docs/verification.md).

Check [GitHub Releases](https://github.com/Cusnd/pstack-codex/releases) for publication status; a version in main is not proof that publication succeeded. The installation commands below are pinned to the published `0.1.0-alpha.2` release (55 skills, upstream 0.15.27), not this pending alpha.3 candidate. A maintenance PR or new release does not upgrade installed copies.

## Install

Use a Codex CLI with plugin support (tested with 0.160.0), Git, and an authenticated Codex account. The public repository does not require GitHub credentials to download.

```sh
codex plugin marketplace add https://github.com/Cusnd/pstack-codex.git --ref v0.1.0-alpha.2
codex plugin add pstack-codex@pstack-codex
```

Confirm the installation:

```sh
codex plugin list --marketplace pstack-codex --json
```

Open a **new chat** in your project after installation. If the desktop app has not refreshed its skills, restart it. The fixed tag keeps this installation on the reviewed alpha instead of following development changes.

[Installation, prerequisites, migration, updates, and removal](docs/installation.md) · [Release downloads](https://github.com/Cusnd/pstack-codex/releases/tag/v0.1.0-alpha.2)

## Use it

Start with the exact skill name, **`poteto-mode`**:

```text
Use $poteto-mode to fix the blank page after login.
Infer reasonable completion criteria from the project and explain key assumptions.
Verify the actual login flow. Keep the changes local; do not commit or publish.
```

A goal is enough to start. Completion criteria, constraints, and relevant files help when you have them. The agent should inspect the project, state meaningful assumptions, and ask about product decisions that evidence cannot settle. User scope and host permissions still govern the work.

| Need | Start with |
| --- | --- |
| Plan, implement, and verify a task | `$poteto-mode` |
| Find the right workflow | `$poteto-help` |
| Understand current code | `$how` |
| Review a diff | `$interrogate` |
| Explain a subsystem or change | `$teach` |
| Improve prose | `$unslop` |
| Configure optional project model preferences | `$setup-pstack` |

Setup is optional; model choices inherit the current agent by default. Most skills require explicit invocation. Review panels and repeated attempts can increase usage. [Read the usage guide](docs/usage.md) for examples and capability boundaries.

## What this package provides

- Adapted skills, playbooks, principles, and portable helper scripts.
- Preserved upstream invocation policy: 57 explicit-only entries, plus discoverable setup in the development candidate.
- Runtime guidance for delegation, available models, scoped history, and verification.
- Original MIT license and attribution. This is an independent adaptation, not an official OpenAI or Cursor product.

It does not include a Cloud account, a running updater, or additional model/connector access. Use your host's own available capabilities. `make-bot-ui` does not deploy its original bot integration.

## Development

Python 3.11+ and Bun 1.3.14 are used for repository validation:

```sh
python -m pip install -r requirements.txt
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/setup_statechart.py
cd plugins/pstack-codex/skills/poteto-mode/scripts
bun install --frozen-lockfile
bun test --timeout 30000 orch watch-pr check-plan.test.ts
bun run typecheck
cd ../../../../..
python scripts/package.py
```

The ZIP filename follows the plugin manifest version. Dependencies and runtime caches are excluded. CI runs validation on Windows and Linux. Optional helper tools cache dependencies outside the installed plugin; see the [installation guide](docs/installation.md#optional-helper-tools).

The statechart suite additionally uses Node 24 and Java 17. Set `TLA2TOOLS` to the absolute `work/tools/tla2tools.jar` path and `PSTACK_CACHE_DIR` to an external writable cache, then run `node --test plugins/pstack-codex/skills/statechart/scripts/test/statechart.test.mjs`. Preserve any skipped platform-specific coverage in the verification report.

`upstream/pstack` is the unchanged upstream snapshot pinned in `upstream.lock.json`; `plugins/pstack-codex` is the maintained port. [Adaptation rules](adapter/rules.md) and [per-skill status](adapter/skills.json) track the differences. See [maintainer automation](docs/automation-options.md) for the separately configured update workflow and [guarded releases](docs/releases.md) for publication gates.

## License

[MIT](LICENSE). Original pstack copyright © 2026 Lauren Tan. Codex adaptation maintained by [Cusnd](https://github.com/Cusnd). Preserve the original copyright and permission notice when redistributing.
