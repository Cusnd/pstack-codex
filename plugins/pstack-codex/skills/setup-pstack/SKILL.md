---
name: setup-pstack
description: Configure pstack per-role model preferences and reasoning budgets for
  the current Codex project. Use for setup-pstack, configure pstack models, or pstack
  budget.
---

# Setup pstack

Configure pstack's optional project role preferences. Read [the Codex runtime contract](../poteto-mode/references/codex-runtime.md). The file `.codex/pstack/config.json` is owned by this plugin and is not a native Codex setting. The default is to inherit the current model and reasoning configuration.

## 1. Discover and load

Read the actual host's advertised model and reasoning capabilities. Read an existing project config if present and preserve recognized choices. Do not guess model IDs or probe rejected model-name variants. If the host cannot expose a model catalog, keep inheritance rather than asking for secrets or inventing a list.

## 2. Choose a budget and roles

Use the user's existing preference when supplied; otherwise offer inherit, small, medium, large, or maximum reasoning. Translate an explicit budget to supported effort values separately from model IDs. Inherited seats keep the parent's configuration. Explain that maximum reasoning is not unlimited usage.

Use [config.example.json](references/config.example.json) for the role inventory. Panel lists determine seat counts. Default arena, architect, and interrogate panels have two inherited seats; the cross-judge pool has one. Reflection retains three lenses. Show actual available model/effort choices and meaningful changes. Preserve custom fields and retired role entries unless the user wants them removed; report ignored entries instead of silently deleting preferences.

## 3. Validate and save

Validate JSON version 1, role values, nonempty panel lists, and each explicitly selected model/effort against current host support. `inherit-parent` and `auto` both omit overrides. If a requested explicit choice is unavailable, leave the existing file intact and resolve that choice.

Write the approved or already-requested changes to the project config, preserving unrelated settings. Read it back and report the path and effective roles. Skills read this file when invoked; it does not install an always-on global rule. Some hosts cannot apply per-agent model overrides; report that limitation and retain the preference for hosts that can.

## 4. Check verification coverage

Inspect the project's existing harness or `verify-*` skill. If one is missing, offer once to generate a project-local workflow with the sibling `create-verification-skill`. Run it on acceptance; on refusal, move on without pushing. Do not add a verification framework or start a separate task merely because setup ran.

Also check whether the project has a skill that runs a model checker, proof, or another formal verifier. If not, offer once to generate one with [create-formal-verification-skill](../create-formal-verification-skill/SKILL.md), so agents can check a key property in every case within a stated scope. Run it on acceptance or an existing explicit request; otherwise continue without creating it.
