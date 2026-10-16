# pstack for Codex

A private Codex adaptation of [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack), preserving its MIT license and tracking source and adaptation versions separately.

The first candidate contains all 54 upstream skills: 53 have adapted instructions, and make-bot-ui explicitly records an unavailable service-specific integration. Invocation policy is preserved: 53 skills require explicit invocation and setup remains discoverable. Read [verification](docs/verification.md) for what was actually tested and the remaining host limitations.

- `upstream/pstack`: original input at `upstream.lock.json`.
- `plugins/pstack-codex`: portable plugin package.
- `adapter`: conversion contract and per-skill capability status.
- `scripts`: validation, source-only packaging, subtree detection, and pinned update preparation.
- `cloud`: reproducible setup and the prepared native update task.
- `.agents/plugins/marketplace.json`: repository marketplace for private installation when requested.

## Validate and package

Use Python 3.11+ and install requirements.txt. Run `python scripts/validate.py`, `python -m unittest discover -s tests`, then `python scripts/package.py`. The archive goes to dist/. These operations do not install the plugin into a personal account.

Bun 1.3.14 is pinned for the existing tools. In `plugins/pstack-codex/skills/poteto-mode/scripts`, run `bun install --frozen-lockfile`, `bun test --timeout 30000 orch watch-pr check-plan.test.ts`, and `bun run typecheck`. Development dependencies in the checkout are excluded from packaging. Installed tools resolve dependencies in a writable cache selected by PSTACK_CACHE_DIR or the platform cache directory.

## Automatic upstream updates

[Native scheduling](docs/automation-options.md) has been empirically verified: a one-off native schedule continued a Cloud chat and executed commands in its repository workspace. An external runner is therefore not a prerequisite for this route. Cloudflare remains an optional way to check tree changes without invoking a model on every tick.

The recurring [update task](cloud/update-task.md) is prepared but not enabled. The Cloud environment has been repaired and republished with the exact GitHub API destination and documented [network execution modes](cloud/networking.md). Use a task started from the updated environment; the old diagnostic chat retains its earlier policy. Accepted source state advances only through a reviewed adaptation PR; detection alone never updates the lock on main. No automatic merge, release, or personal installation is enabled.
