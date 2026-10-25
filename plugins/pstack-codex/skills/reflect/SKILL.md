---
name: reflect
description: Spawn three parallel review subagents over the active transcript, surface
  learnings, and route each to a concrete edit on an existing skill. Use when the
  user says reflect.
---

# Reflect

Mine the current conversation for durable learnings, then route them into skill edits.

Invoke when the user says "reflect" or "$reflect". Skip when the conversation is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings.

## 1. Locate the active transcript

Use the current conversation or a scoped history reader under the [Codex runtime contract](../poteto-mode/references/codex-runtime.md). Confirm conversation and project identity. Pass only the relevant transcript or a clearly labeled digest to reviewers. If the host cannot read prior messages, work from available context and identify the gap; do not scan unrelated personal histories.

## 2. Spawn three reviewers in parallel

Use the [Codex runtime contract](../poteto-mode/references/codex-runtime.md) to launch three independent review lenses, queuing to the actual concurrency limit. Reviewers may read scoped connected sources when available, without widening permissions or sending messages. They use these templates:

| Lens | Role | Template |
| --- | --- | --- |
| Judgment | `reflect judgment, divergent, synthesizer` | `references/judgment-reviewer.md` |
| Tooling | `reflect tooling` | `references/tooling-reviewer.md` |
| Divergent | `reflect judgment, divergent, synthesizer` | `references/divergent-reviewer.md` |

Pass the appropriate template and relevant transcript/digest to each. All roles inherit by default. Reviewers return findings and evidence in their completion response. If only sequential self-review is available, preserve the three lenses and label that limitation.

## 3. Synthesize

Use one synthesizer under `reflect judgment, divergent, synthesizer`. Pass `references/synthesizer.md` with the full reviewer outputs. It spot-checks citations using available scoped tools and returns Accepted / Rejected / Backlog. If delegation is unavailable, perform this stage yourself and report that boundary.

## 4. Structural enforcement check

Move any Accepted item that a lint rule, script, metadata flag, or runtime check would enforce more reliably to Backlog. See the **encode-lessons-in-structure** principle skill.

## 5. Apply

Present the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval before applying any Accepted edit. The user picks the subset and may redirect routings. Skill changes affect every future agent in the org. Do not auto-apply.

Present Backlog items locally. File them in an external tracker only when the user has authorized that destination and action. Apply approved skill changes to editable source, never an installed plugin cache. Personal memory changes require an explicit user request.

Before approval, name the editable destination, such as the project's `.agents/skills/<skill>/` or the host's supported personal skill source. If only an installed cache exists, copy the approved skill into that destination and edit the copy. Reflect alone does not authorize opening a PR or pushing a repository; follow explicit user scope and the host's normal skill-saving requirements.

Follow each approved row's Routing exactly:

- Trivial existing-skill edit (a one-line bullet, a tightened sentence, a stale fact corrected): the parent does it directly.
- Substantive existing-skill edit (a new section, a new pattern table, more than ~10 lines): hand to available `skill-creator` guidance and run its draft / test / iterate loop.
- `tune description: <skill path>` (the skill exists but didn't trigger when it should have): hand to `create-skill` and run its description-optimization loop.
- `new skill via create-skill: <kebab-name>`: hand creation to `create-skill`. Do not invent the shape ad hoc.

If your environment ships a SKILL.md validator, run it on every touched skill before declaring done.

## 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`. What changed, one line each.
- New skills created: `<skill path>`. One line each (rare).
- Backlog filed to the devex tracker: `<issue title>` (`<tags>`). One line each.
- Dropped: one line per rejected finding + reason from the synthesizer.
