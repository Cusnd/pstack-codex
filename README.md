# pstack for Codex

A maintained adaptation of [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack), with the original MIT license. Source and adaptation versions are tracked independently.

The first port is in progress. The normalized package contains 54 upstream skills with their invocation policy preserved, but it is not ready to install until runtime-specific instructions have been adapted and verification passes.

- `upstream/pstack`: untouched input at `upstream.lock.json`.
- `plugins/pstack-codex`: the installable plugin directory once validated.
- `adapter`: conversion rules and per-skill capability status.
- `scripts`: validation, packaging, and update automation.
- `tests`: behavior checks for adaptation and synchronization.

Use Python 3.11 or newer and install `requirements.txt`. Run `python scripts/validate.py --metadata-only` to check package metadata during the initial port. Run `python scripts/validate.py` for release eligibility. The latter deliberately fails while any skill is still pending.

Cloudflare Workers is being evaluated for scheduled detection and coordination. Cloud execution, authentication, CI checks, and publication remain separate concerns. No automatic deployment or personal installation is enabled by this source import.

