# Codex runtime contract

This file maps pstack workflow intent to the tools actually available in the current Codex host. Read it before delegation, model selection, history access, automation, or verification. Higher-priority host instructions and the user's scope govern every action.

## Invocation and paths

Use the host's explicit skill picker or `$skill-name` where supported. A reference such as `how` means read the sibling `skills/how/SKILL.md`; it is not a shell command. Resolve supporting files relative to the current skill. Give delegates absolute paths, including this runtime contract and the relevant role reference. Do not search other users' plugin caches or select an arbitrary newest installation.

Generated project skills normally belong in `.agents/skills/<name>/SKILL.md`, with personal placement selected by the user's host configuration. Use the available skill-creator guidance. Preserve existing invocation policy. For an explicitly requested manual skill, store `policy.allow_implicit_invocation: false` in `agents/openai.yaml` rather than an unsupported frontmatter field.

## Delegation

Discover the current collaboration API. Typical hosts expose spawn, wait, message, follow-up, and interrupt tools; their exact names and parameters vary. Use only advertised arguments. For ordinary implementation delegates, include [delegate.md](delegate.md). For the comment review role, include `skills/no-comments/references/reviewer.md` by its resolved absolute path. Custom role files are prompts, not automatically registered agent types.

Keep the parent's orchestration role. Partition writes into disjoint paths or isolated worktrees. Subagents may share a filesystem and inherited permissions. A read-only instruction expresses intent; only an actual host sandbox enforces it. Do not weaken permissions to obtain connectors. If delegation is unavailable or prohibited, perform the planned angles sequentially and label the loss of independent review. Preserve all verification lanes even when they must run in batches.

Respect the actual concurrency limit, including the parent. Queue additional workers. Do not request imaginary cloud/local environment parameters or create user-visible chats to emulate delegates. Use a separate Cloud task only when that is explicitly part of the requested workflow. Capture its repository, branch, base SHA, environment, and task ID.

## Models and budget

Defaults inherit the parent's model and reasoning configuration. Optional project configuration lives in `.codex/pstack/config.json`; it is a pstack convention, not a built-in Codex setting. Read it when this workflow needs role selection. A scalar role has one seat; panel roles may have a list. Default panel size is two independent seats; the cross-judge pool defaults to one seat; reflection retains its three review lenses.

Supported role keys are `feature, refactoring`, `bug-fix`, `perf-issue`, `hillclimb`, `judgment and prose`, `hardest tasks`, `how explorer`, `how explainer`, `why investigators`, `why synthesizer`, `reflect tooling`, `reflect judgment, divergent, synthesizer`, `arena runners`, `arena cross-judge pool`, `swarm workers`, `architect runners`, and `interrogate reviewers`.

A seat is `{"model":"inherit-parent"}` or `{"model":"<verified model>","reasoning_effort":"<verified effort>"}`. `auto` also means inherit. Omit model and effort arguments for inherited seats. Never encode effort or speed by constructing a model slug. Some hosts permit overrides only for a fresh-context spawn; then pass a complete brief with that spawn rather than an incompatible history fork. If an explicit model is unavailable or rejected, use inheritance, report the substitution, and do not silently rewrite saved choices.

Prefer different supported models for judgment-sensitive panels when requested and available. Independent runs on one model provide multiple observations, not cross-family evidence. Identify actual models used; if unknown, say inherited/unknown. A budget label is a preference mapped only to supported effort values, not a promise of unlimited usage. Fast mode is a separate host capability, never a guessed suffix.

## Current work and future schedules

For an authorized task, continue until its completion predicate is met, a real dependency blocks progress, or an execution limit is reached. Do not infer permission to install a timer from a request to keep working in this turn. When recurring work is requested, use the host's scheduling tool and its supported destination. An application heartbeat may require a running computer; Cloud execution and scheduled Cloud dispatch are separate capabilities.

Record a resumable checkpoint before stopping a long run. Include the base and current commits, pending work, evidence paths, process ownership, and next action. A timer firing is not evidence of task success. Do not create a goal or change its status except through a supported tool and within the user's explicit request.

## History and reflection

Prefer supported chat listing and reading tools. Narrow by the user's project, topic, and time range. Verify thread identity before reading message content. Never treat all personal sessions as the default corpus. If no scoped history tool is available, use the current conversation or a user-supplied transcript, and state the missing evidence. For local session files, confirm the current host's format and workspace identity first; do not assume one JSONL line always has a user-message shape.

Do not write personal memories without an explicit request. Skill improvements belong in an editable source repository, not an installed cache. Preserve the user's selected subset when applying reflection findings. External tracker messages require authorization.

## Verification and external tools

Use the existing test harness first. For browser or desktop checks, use the available supported computer/browser tools. For CLI/TUI behavior, use a terminal/PTY and inspect actual output and exit status. If the required surface is unavailable, retain that check as blocked rather than treating a static result as a pass.

Before a commit, review the diff for accidental generated files, repetition, scope creep, unsupported claims, and broken references; run proportionate checks. The no-comments role is a separate optional workflow when invoked. Tool availability does not authorize sending messages, changing external state, publishing, merging, or deploying outside the user's request. If a PR is created in a host with an artifact-attachment tool, attach its verified URL.

