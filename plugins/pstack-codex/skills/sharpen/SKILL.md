---
name: sharpen
description: "Make a task deeper, not bigger, then rewrite the prompt without executing it. Use for $sharpen."
---

Make the task deeper, not bigger. Before rewriting the prompt:

1. Say what a top professional would do here that the user is not asking for.
2. Name the rawest material they would start from instead of an already-digested summary.
3. Name the specific methods and available tools they would use.
4. Say what, other than the agent or the user, would show the result is right.

Then return a rewritten prompt asking for exactly that. Leave the user's choices open. Do not execute the rewritten task or expand its permissions; the deliverable is the prompt.
