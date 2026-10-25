---
name: swarm
description: Fan out N parallel workers, drain them, and return one report. Use for
  $swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration.
---

# Swarm

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Select `swarm workers` using the [Codex runtime contract](../poteto-mode/references/codex-runtime.md), inheriting the parent by default. For a model race, verify and name each arm's available model before launch; unavailable model diversity must be reported.
4. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Launch workers using the actual host delegation API. Queue to the available concurrency limit and give each a separate writable scope. Ordinary delegates may share a filesystem and permissions; do not describe them as independent cloud machines. If delegation is unavailable, run coverage lanes sequentially and label the limitation.

For explicitly authorized remote Cloud tasks, first confirm the target repository, pushed branch, exact base commit, environment and dispatch capability. For local work, use an isolated checkout when needed. Never assume a tool supports a branch/environment parameter that it has not advertised.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

## Phase D: Report

Return one consolidated in-chat report with a result table, issue one-liners, gaps or dropouts, and the race rule when used.
