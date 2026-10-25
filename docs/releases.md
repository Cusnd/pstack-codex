# Guarded releases

This repository's owner has authorized unattended maintenance merges and releases after validation. This does not authorize personal installation, deployment, changing repository protections, or weakening the adaptation contract. Other installations must obtain their own owner's authorization; adding this plugin does not grant permission to release any project.

The `Validate port` workflow runs the full validator, Python tests, Bun tests, strict TypeScript checking, and package inspection on Linux and Windows. Only a successful **main push in Cusnd/pstack-codex** can enter the release job. PRs and forks cannot publish. Only that job has `contents: write`; checkout does not persist credentials and the token is supplied only to the publisher step.

The publisher checks the exact workflow commit, clean checkout, current remote main, plugin version, and version-specific changelog. It rebuilds the ZIP and compares it byte for byte to **both** validation artifacts from that same workflow run. Publication is serialized without cancelling a running release. A superseded main job leaves at most a draft for inspection, not a published stale package.

For a new version it creates a draft, uploads the ZIP and `SHA256SUMS`, verifies sizes and GitHub's SHA-256 asset digests, creates a new tag at the tested commit, and only then publishes. Alpha/beta/rc versions remain prereleases, never latest stable. The release notes identify the accepted upstream commit/tree, validation run, and host limits.

Reruns reuse matching drafts and assets. An identical already-published package whose tag is an ancestor of main is a no-op (useful for documentation-only changes). Conflicting tags, changed packages under an existing version, duplicate/unexpected assets, missing digests, or a draft for a different commit fail closed. Nothing deletes or replaces an existing tag, release, or asset. Do not resolve a conflict by overwriting it; inspect the evidence and, when package contents changed, propose a new version.

Retry a transient interrupted release by rerunning its GitHub Actions run. A permission failure requires the repository owner to repair the relevant permission; do not copy personal credentials or bypass protected workflows. Tests use an in-memory API and never publish. Public release creation does not update a user's installed plugin.
