<!-- Paste into ~/.claude/CLAUDE.md (user level). The flow's core does not hold this table.
Ruled 2026-11-15; replaces, for development work, the Track B table and §0 #9 of the
career repository's task_model_allocation.md. -->

## Which model runs which step

| Step | Model | Move up when |
|---|---|---|
| Intent, spec, the question loop | Opus | two rounds still fail the completeness checklist, or the draft contradicts itself → Fable |
| Plan | Opus | high-risk tier: the second read of the plan runs on Fable |
| Implementation, small changes | Sonnet | the same problem has failed two fix rounds → Opus |
| Review in a fresh session | Opus | high-risk tier: Fable from the start; validation finds an Important problem the review missed → re-review on Fable |

- **Subagents run on the main session's model.** The flow's three subagent definitions carry no `model` field, so the researcher runs on Opus (spec, plan) and the code-reviewer and the verifier on Sonnet (implementation, small changes) — a small change's review result therefore comes from Sonnet. Change it only if the pilot shows a small change later judged "behaviour changed: yes" that the verifier did not report: then set `CLAUDE_CODE_SUBAGENT_MODEL=opus` at user level (all three subagents move together; the plugin is not edited).
- **Before any model switch, raise the effort level first.** Switch only if that still falls short.
- **Fable from the start only for:** the high-risk tier; a refactor or an architecture decision across the whole project; designing the flow itself.
- **End of the weekly cycle:** when the owner says there is Fable share left before the reset, Fable may take ordinary work — the share does not carry over.
- **Opening self-check:** at the start of a session, compare the step at hand with the model in use; when they do not match, say so once and continue with what the owner chooses.
- **Watch figure:** spec changes after plan approval. If it worsens, the spec step goes back to Fable.
