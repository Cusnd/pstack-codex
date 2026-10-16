# Installation

## Requirements

- A Codex account and a CLI that exposes `codex plugin` (tested: 0.160.0).
- Git on `PATH`, plus network access to GitHub.
- A host that supports installing skills from a Git-backed marketplace. Organization policy can restrict external marketplaces.

The plugin has no API key or MCP connection of its own. You use your existing Codex account and whatever tools the host makes available. Installing it does not grant access to additional models, browsers, connectors, or cloud environments.

## Install the fixed alpha

These commands work in PowerShell and POSIX shells:

```sh
codex plugin marketplace add https://github.com/Cusnd/pstack-codex.git --ref v0.1.0-alpha.1
codex plugin add pstack-codex@pstack-codex
codex plugin list --marketplace pstack-codex --json
```

The list should include `pstack-codex`, version `0.1.0-alpha.1`, installed and enabled. Start a new project chat, then send:

```text
Use $poteto-help to explain the available workflows. Do not change project files.
```

If `plugin` is an unknown command, update Codex through its supported installation channel. If skills are absent from an existing desktop chat, start a new chat and, if needed, restart the app. Do not copy files into an installed cache to make it refresh.

The repository marketplace is not an official OpenAI directory listing. The two commands above add this source directly. See the official [CLI plugin commands](https://learn.chatgpt.com/docs/cli/reference#codex-plugin) and [marketplace documentation](https://developers.openai.com/plugins/build/plugins).

## Optional helper tools

Ordinary instruction-based skills do not require the repository's build dependencies. Specific workflows can use:

| Tool | Needed for |
| --- | --- |
| Python 3.11+ | Portable worktree audit and decision log helpers |
| Bun 1.3.14 (tested) | Orchestration and PR watch tools |
| GitHub CLI (`gh`), authenticated by you | GitHub review, checks, and PR operations |

The Bun helpers install their locked dependencies on first use in a writable cache outside the plugin. That step needs package-registry network access. Set `PSTACK_CACHE_DIR` to choose a cache directory. Python helper scripts themselves use the standard library; PyYAML is needed for repository validation, not those helpers. Windows users can invoke the Python and Bun entrypoints directly; shell wrapper scripts require a compatible shell.

## Updating or switching versions

A tag-pinned installation stays on that tag. To switch to another published version, remove this plugin and its marketplace, then repeat the install commands with the desired release tag:

```sh
codex plugin remove pstack-codex@pstack-codex
codex plugin marketplace remove pstack-codex
```

Project preferences in `.codex/pstack/config.json` are separate from the installed package. Preserve them when reinstalling. For development only, `--ref main` tracks the development branch; `codex plugin marketplace upgrade pstack-codex` refreshes that marketplace source. Refreshing a marketplace is not a promise that an installed plugin has been upgraded; install the desired version and verify the list output.

## Migrating from the private candidate

Earlier testers may have `pstack-codex@pstack-codex-private`, version `0.1.0`. Remove that registration before installing the public alpha to avoid duplicate skill names:

```sh
codex plugin remove pstack-codex@pstack-codex-private
codex plugin marketplace remove pstack-codex-private
```

Then follow the fixed-alpha installation above. The public alpha version is intentionally marked as a prerelease; its number should not be treated as an automatic upgrade from the private candidate.

## ZIP download

The [release](https://github.com/Cusnd/pstack-codex/releases/tag/v0.1.0-alpha.1) includes a source-only Agent Plugins 1.0 ZIP and SHA-256 checksum. Use it for inspection or a host's documented archive import flow. The verified Codex installation route is the Git marketplace command above; the ZIP is not a standalone executable installer. GitHub's automatically generated source archives contain the entire repository and are different from the plugin ZIP.

## Uninstall

```sh
codex plugin remove pstack-codex@pstack-codex
codex plugin marketplace remove pstack-codex
```

These commands target only this plugin and marketplace. Project preferences and any helper cache are separate; remove them only if you no longer need them.
