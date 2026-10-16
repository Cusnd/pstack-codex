---
name: make-bot-ui
description: Plan a local UI that triggers an agent routine. The upstream service-specific
  webhook integration is deferred in this Codex port; use for make-bot-ui or designing
  such an integration.
---

# Make Bot UI

This entry preserves the upstream workflow's intent: a local UI whose actions wake an agent routine. The original service-specific webhook, state-update tools, and secret-request UI do not have a verified equivalent in this Codex port. No runnable integration is bundled, and this skill must not claim that one was created.

## Design an integration when requested

1. Identify the action each button should perform, its input, completion state, and the intended agent/scheduler service.
2. Discover an actually available service with a documented invocation API. Distinguish current-turn execution, recurring scheduling, and event-triggered routines. Do not fabricate an endpoint or use an internal browser API as a public contract.
3. Establish the authorization boundary. Keep secrets on a trusted backend or local server. Never put sender keys in browser code, repository commits, query strings, or chat messages. Use a supported credential-entry flow if one exists.
4. Design the local UI, backend request, state feedback, timeout, retry, and duplicate-action behavior. Keep UI controls disabled until a verified backend exists; label a mock explicitly.
5. Implement only when the user requests this separate integration and the selected service is available. Verify one harmless action end to end and report its actual response and state transition.

Until those prerequisites exist, return the concrete integration specification and the missing capability. The rest of pstack does not depend on this integration.
