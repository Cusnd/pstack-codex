# Changelog

## 0.1.0-alpha.2 — pending publication

- Adapt upstream pstack 0.15.27, including `create-formal-verification-skill`; preserve all 55 skill entries.
- Carry through ketchup completeness, setup/help/recipe refinements, sharpen guidance, and TypeScript type guards.
- Verify and reuse immutable update candidates, rejecting damaged or incomplete candidates without advancing the accepted lock.
- Gate automated releases on Linux and Windows validation and identical source-only ZIPs. Preserve existing tags and assets.

Known limits: `make-bot-ui` remains deferred. Live macOS/desktop execution and personal installation are not established; an alpha release is not a claim of stable support.

## 0.1.0-alpha.1 — 2026-10-16

First public alpha of pstack for Codex, based on upstream pstack 0.15.25.

- Preserve all 54 skills, original MIT attribution, and invocation policies.
- Adapt 53 skill entries to actual Codex host capabilities; retain `make-bot-ui` with an explicit unimplemented integration boundary.
- Provide portable Python helpers, Bun dependency caching outside installed source, and Windows/Linux validation.
- Publish a Git marketplace, fixed-version installation commands, usage examples, and migration/removal instructions.
- Separate public maintenance guidance from personal Cloud operation records.

Known limits: full live workflow coverage and macOS execution are not established. Recurring maintenance is disabled; a live changed-source-to-draft-PR rehearsal is still required before activation.
