---
name: arena
description: Spawn N parallel candidates at the same task, pick a base, graft the
  strongest parts of the losers into it. Use for $arena, 'arena this', 'throw it in
  the arena', or when one attempt at a non-trivial artifact would lock in the wrong
  shape.
---

# Arena

Open a todolist with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate is producing.
2. Derive the rubric, 3-6 concrete gradeable criteria for what success looks like on *this* task. It is the picker's tool in Phase D. Candidates only see the task.
3. Pick the runners using `arena runners` from the [Codex runtime contract](../poteto-mode/references/codex-runtime.md). Default to two independent inherited-model seats. Prefer actual supported model diversity when available, and record what was used. Never infer a valid model from a family prefix. Use more runners when separate design directions justify them.
4. Give each candidate its own output location (a git worktree where possible, otherwise a task-owned directory under the platform temporary directory, with one child per candidate), per the **separate-before-serializing-shared-state** principle skill.

## Phase B: Fan out

Launch independent candidates through the actual delegation API up to the available concurrency limit, queuing the rest. Give each the same task, shared grounding path, separate output path, and a short rationale requirement. If no delegation is available, run the candidates sequentially and label that limitation.

If a candidate produces no output, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After all Phase B candidates complete, select one judge from `arena cross-judge pool` using the [Codex runtime contract](../poteto-mode/references/codex-runtime.md). Default to one inherited-model seat; prefer a different supported model when available. Give it read-only review scope, the rubric and candidate paths. It scores each criterion and recommends a base with rationale, in parallel with your reading when possible. Do not spawn it while candidates are writing. If there is no independent judge, label the second pass as self-review.

## Phase D: Pick a base

Read every candidate end to end before picking. Score each against the rubric criterion by criterion, not on holistic feel, and compare with the cross-judge. Agreement on the base confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous. Read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants. When two feel tied, prefer the cleaner boundary or smaller API, per the Laziness Protocol.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting into the base, usually one or two things per candidate, not most of it. Fold each graft in by hand, per the **redesign-from-first-principles** principle skill, so the result stays coherent under one mental model. Don't paste mechanically.

If the candidates converge on one shape, that is strong agreement. Note it and ship the consensus shape. No graft is needed. If they wildly diverge, Phase A was under-specified. Reframe and re-run rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output, per the **prove-it-works** principle skill. If verification finds a problem the arena missed, either Phase A was wrong (re-frame and re-run) or a candidate caught it and you missed the graft (go back to Phase E). Don't paper over it.

## Outputs

One synthesized artifact, with a short synthesis note alongside naming the base and why, the cross-judge's verdict, each graft with its source candidate, what was rejected and why, any convergence or dropouts, and the verification result.
