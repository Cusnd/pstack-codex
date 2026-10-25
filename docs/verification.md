# Verification and alpha limitations

The release is an independently maintained Codex adaptation, not a certification of every workflow on every host. Review the checks for the release commit in [GitHub Actions](https://github.com/Cusnd/pstack-codex/actions).

## Package and scripts

- The development candidate retains all 58 upstream skills and their invocation policy: 57 explicit-only entries and discoverable setup.
- 57 skills have adapted instructions. `make-bot-ui` explicitly defers the original service-specific integration.
- Validation checks metadata, inventory, local skill links, runtime references, marketplace source, and MIT attribution.
- The Python suite covers source probing, failed/incomplete responses, extraction boundaries, paths containing spaces, worktree preservation, PR state handling, and decision logging.
- Preparation tests also cover repeat reuse, unrelated upstream commits with the same subtree, damaged receipts/source/diffs, interrupted preparation, and preservation of the accepted lock.
- Bun tests cover orchestration, plan checks, and PR watch behavior. Strict TypeScript checking covers the PR watcher.
- CI runs the validation and script checks on Windows and Linux. Source-only ZIP packaging checks integrity and skill count and excludes generated dependencies.
- Codex CLI 0.160.0 recognized and installed the candidate marketplace package. Each published alpha also requires an isolated installation check from its release tag; this proves package installation, not execution of every skill.

## Host observations

Development checks demonstrated command execution in a Cloud repository, successful Git and public GitHub API access, a live unchanged-upstream probe, and one native scheduled continuation that repeated those commands. Setup and ordinary Cloud tasks can expose different execution schemas. Follow [networking guidance](../cloud/networking.md) and verify the current host.

Separately, a scheduled continuation in ChatGPT Work on 2026-10-19 ran `pwd`, `git rev-parse HEAD`, `git ls-remote origin HEAD`, and the live upstream probe with exit code 0. This confirms command and network execution in that Work conversation; it is not a claim about the earlier Codex Cloud environment or identical virtual-machine identity.

These observations do not prove exact timer accuracy or long-term reliability. Installing this package does not enable a recurring updater. Personal environment, chat, schedule, and execution receipts are not part of the public documentation or release assets.

## Known limitations

- Statechart needs Node 22.15+ (Node 24 in CI), Java 11+, TLC 1.7.4, and optional pinned npm renderers. A checked fixture with only TypeOK is not proof of application correctness; inspect each model's rules, bounds, and real-code replay. The source suite includes platform-specific process, namespace, font, and fault-injection tests; record unavailable coverage explicitly.
- Ketchup video needs an actual encoder and frame-inspection capability. If unavailable, the skill returns actionable text with the rendering gap, not a claimed video.

- Every adapted skill has not been exercised in a live desktop chat. Agent outcomes still depend on the task, model, project, and available tools.
- macOS script execution has not been verified; CI covers Windows and Linux.
- UI verification, independent agents, model overrides, connectors, and schedules depend on the host. Missing tools are an unverified boundary, not a passing check.
- `make-bot-ui` is a planning-only entry until its external integration has an implemented and tested replacement.
- Each maintenance host must pass a live changed-source-to-draft-PR rehearsal and duplicate-run handling before its recurring task is enabled. Record that evidence in the maintenance PR; unit coverage alone is insufficient.
- The development candidate has not been installed from a published release tag. The existing isolated release installation evidence applies to `0.1.0-alpha.1`.

See [usage](usage.md) for practical scope and [maintenance](automation-options.md) for the separate update process.
