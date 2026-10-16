---
name: poteto-help
description: Guides users through pstack setup, $poteto-mode, and picking the skill,
  playbook, or principle for a task. Type $poteto-help with a question.
---

# Poteto help

Answer the user's pstack question, give one usable prompt, and link the adapted source file. A help question does not authorize starting its workflow. A request such as "use pstack to fix this bug" does: read [poteto-mode](../poteto-mode/SKILL.md) and carry out the task.

Read the file you recommend before quoting its behavior. Resolve local links in the actual plugin root; the original Cursor guide is background material, not documentation of this port. The runtime contract is [here](../poteto-mode/references/codex-runtime.md).

## Get set up

Use the installation instructions supplied with this Codex plugin and the host's actual plugin manager. Do not invent an add-plugin command or claim the unfinished source checkout is a released package. Run [setup-pstack](../setup-pstack/SKILL.md) to choose optional role and reasoning preferences in `.codex/pstack/config.json`, then invoke `$poteto-mode` with a goal and a checkable finish condition.

Without project preferences, every role inherits the current model. A role override is applied only when the actual host supports it. The configuration is a plugin convention, not a native Codex model-routing field. Review panels and repeated attempts consume more tokens; choose the scope and supported role preferences accordingly without removing required verification coverage.

The upstream invocation policy is preserved. Only setup-pstack is implicitly discoverable. Other skills require an explicit user invocation or an explicit step from an invoked workflow. A source reference does not authorize unrelated use.

If no project `verify-*` skill or app harness exists, recommend [create-verification-skill](../create-verification-skill/SKILL.md) when the question is about proving behavior.

## Start a task

`$poteto-mode` selects a playbook, records its steps in the available planner or checklist, and invokes the skills those steps require. A skipped step retains a concrete reason. Start each new task with the skill or an explicit request to continue its workflow; do not promise Cursor Custom Mode keyboard shortcuts in Codex.

For delegate behavior, pass [delegate.md](../poteto-mode/references/delegate.md) and the task-specific skill paths to the actual subagent API. The file is a role brief, not a registered agent type. Respect concurrency, permissions, and shared filesystem boundaries. A separate worktree is not a separate machine.

Read [prompting](references/prompting.md) and [recipes](references/recipes.md) before helping the user word a request. If their goal is unclear, ask one concise question about setup, starting a task, picking a skill, diagnosing a run, or customization. Do not ask this when their message already identifies the need.

## Pick a skill

| The user wants to | Skill |
|---|---|
| Do any non-trivial task with rigor | [`$poteto-mode`](../poteto-mode/SKILL.md) |
| Check that the agent understood their goal and the problem before it starts | [`$in-your-own-words`](../in-your-own-words/SKILL.md) |
| Aim a task higher before starting: more expert, more outcome-focused, not overspecified | [`$sharpen`](../sharpen/SKILL.md) |
| Know how code works now, or where new code should live | [`$how`](../how/SKILL.md) |
| Know why code is shaped this way, or where a number came from | [`$why`](../why/SKILL.md) |
| Understand a change or subsystem, explained plainly | [`$teach`](../teach/SKILL.md) |
| Catch up on their own recent work on a topic | [`$recall`](../recall/SKILL.md) |
| Catch up on what changed in this chat since their last message, in a few plain sentences and small visuals, with enough context to decide each action item | [`$ketchup`](../ketchup/SKILL.md) |
| Know what a small diff could break outside itself | [`$blast-radius`](../blast-radius/SKILL.md) |
| Settle types and module shape before code that crosses a function boundary | [`$architect`](../architect/SKILL.md) |
| Get several attempts at one brief, merged into the best one | [`$arena`](../arena/SKILL.md) |
| Run parallel checks over slices, or race workers, with verified isolation | [`$swarm`](../swarm/SKILL.md) |
| Have independent reviewers examine a diff and try to break it | [`$interrogate`](../interrogate/SKILL.md) |
| Fix a bug test-first when a cheap local test exists | [`$tdd`](../tdd/SKILL.md) |
| Apply TypeScript rules to `.ts` or `.tsx` work | [`$typescript-best-practices`](../typescript-best-practices/SKILL.md) |
| Strip comments before review, using a reviewer that didn't write them | [`$no-comments`](../no-comments/SKILL.md) |
| Clean AI tells out of prose | [`$unslop`](../unslop/SKILL.md) |
| Write docs, an RFC, a README, a PR description, or a commit message to a standard | [`$technical-writing`](../technical-writing/SKILL.md) |
| Hear the last reply again in plain words | [`$bro`](../bro/SKILL.md) |
| Give agents a scripted way to drive the app and prove behavior | [`$create-verification-skill`](../create-verification-skill/SKILL.md) |
| Bring a verification skill and its feature map back in line with the app | [`$maintain-verification-skill`](../maintain-verification-skill/SKILL.md) |
| Vet a performance number before reporting or acting on it | [`$benchmark-checklist`](../benchmark-checklist/SKILL.md) |
| Run a large or cross-cutting change, or one to review after stepping away | [`$figure-it-out`](../figure-it-out/SKILL.md) |
| Keep a decision log during a run, and review it afterward | [`$show-me-your-work`](../show-me-your-work/SKILL.md) |
| Pick a model for each role and a reasoning budget | [`$setup-pstack`](../setup-pstack/SKILL.md) |
| Turn their own working habits into a personal mode skill | [`$automate-me`](../automate-me/SKILL.md) |
| Turn what a finished task taught into skill edits | [`$reflect`](../reflect/SKILL.md) |
| Stop agents from repeating the same mistakes in this repo | [`$correct`](../correct/SKILL.md) |
| Plan a bot UI and identify missing platform integration | [`$make-bot-ui`](../make-bot-ui/SKILL.md) |
| Find their way around pstack | `$poteto-help` |


If a sibling skill is missing from this table, read its frontmatter and route by its description. Principles live in the principle-* directories and in the main skill's principle index.

Close calls:

- how explains current behavior; why investigates rationale; teach combines the findings without changing the code.
- arena compares attempts at one brief; swarm splits coverage or races attempts and reports the actual isolation used.
- architect proceeds to implementation after the design unless the user asks for a checkpoint.
- interrogate reviews the diff; blast-radius tests assumptions outside the diff.
- recall searches authorized related history; ketchup summarizes only the current chat since the user's last message.
- figure-it-out designs one bespoke workflow; Orchestrate coordinates a standing program; Autonomous run drives one task to a finish condition.

## Playbooks and principles

Playbooks are step lists inside poteto-mode, not separately registered skills. These phrases select them:

- "babysit this PR" drives it to merge-ready; merging still requires authorization.
- "land the stack" selects Shipping.
- "take over this branch" selects Session pickup.
- "pause safely" selects Pause safely.
- "full autopilot on this queue" selects Autopilot-full; "stack them, don't ship" selects Autopilot-stack.
- "run the eval playbook" selects Eval.
- "plan a multi-phase change" selects [Multi-phase plan](../poteto-mode/playbooks/multi-phase-plan.md), whose deliverable is the plan.

The main skill's [playbook index](../poteto-mode/SKILL.md) defines every route. The host's planning mode may be used when available; no pstack planning mode is registered. Principles can be invoked by their actual skill names or applied through the main workflow.

## Fix a run

| Symptom | Check |
| --- | --- |
| The workflow drifted | Restate the active task and invoke poteto-mode; inspect its checklist. |
| A question was treated as implementation | State that the turn is a question or that it starts a new task. |
| A model preference had no effect | Check project configuration, catalog availability, and the host's actual override support. |
| Costs exceeded expectations | Inspect panel counts, repeated attempts, and selected role preferences. |
| A skill did not load automatically | Most skills preserve the upstream explicit-only policy. |
| Agents overwrote each other | Give each writer an owned path or worktree and verify actual isolation. |
| An overnight run made no progress | Check its finish predicate and actual scheduling mechanism. A running turn and a future callback are different capabilities. |
| A build pass was called success | Require evidence from the actual command, UI flow, stored value, or measured profile. |

## Customize pstack

[automate-me](../automate-me/SKILL.md) drafts a personal workflow from authorized history; [reflect](../reflect/SKILL.md) proposes evidence-based skill edits; [correct](../correct/SKILL.md) records recurring repository lessons. Edit maintained source, validate, and reinstall through the normal package workflow. Never modify an installed cache as the maintained source.

Authoring and Eval are main-skill playbooks. Use an available skill-creator capability or the self-contained authoring checks. Diff cleanup, actual UI/CLI tools, and supported scheduling replace the original platform-specific dependencies. [make-bot-ui](../make-bot-ui/SKILL.md) explicitly records the unresolved platform integration.

Lead with the answer. Give at most one tailored example prompt, then the relevant file link. Expand only when the user asks for the whole map.
