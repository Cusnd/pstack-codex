# Verification and alpha limitations

The release is an independently maintained Codex adaptation, not a certification of every workflow on every host. Review the checks for the release commit in [GitHub Actions](https://github.com/Cusnd/pstack-codex/actions).

## Package and scripts

- All 54 upstream skills retain their inventory and invocation policy: 53 explicit-only entries and discoverable setup.
- 53 skills have adapted instructions. `make-bot-ui` explicitly defers the original service-specific integration.
- Validation checks metadata, inventory, local skill links, runtime references, marketplace source, and MIT attribution.
- The Python suite covers source probing, failed/incomplete responses, extraction boundaries, paths containing spaces, worktree preservation, PR state handling, and decision logging.
- Bun tests cover orchestration, plan checks, and PR watch behavior. Strict TypeScript checking covers the PR watcher.
- CI runs the validation and script checks on Windows and Linux. Source-only ZIP packaging checks integrity and skill count and excludes generated dependencies.
- Codex CLI 0.160.0 recognized and installed the candidate marketplace package. Each published alpha also requires an isolated installation check from its release tag; this proves package installation, not execution of every skill.

## Host observations

Development checks demonstrated command execution in a Cloud repository, successful Git and public GitHub API access, a live unchanged-upstream probe, and one native scheduled continuation that repeated those commands. Setup and ordinary Cloud tasks can expose different execution schemas. Follow [networking guidance](../cloud/networking.md) and verify the current host.

These observations do not prove exact timer accuracy, long-term reliability, identical virtual-machine identity, or a changed-source-to-draft-PR update flow. No recurring updater is enabled by this package. Personal environment, chat, schedule, and execution receipts are not part of the public documentation or release assets.

## Known limitations

- Every adapted skill has not been exercised in a live desktop chat. Agent outcomes still depend on the task, model, project, and available tools.
- macOS script execution has not been verified; CI covers Windows and Linux.
- UI verification, independent agents, model overrides, connectors, and schedules depend on the host. Missing tools are an unverified boundary, not a passing check.
- `make-bot-ui` is a planning-only entry until its external integration has an implemented and tested replacement.
- Recurring source maintenance awaits a live changed-source-to-draft-PR rehearsal, including duplicate-run handling. Unit coverage is not that live acceptance test.

See [usage](usage.md) for practical scope and [maintenance](automation-options.md) for the separate update process.
