<!-- Paste into ~/.claude/CLAUDE.md (user level). The flow's core does not hold this table.
Ruled 2026-11-15; rows replaced 2026-11-19; rewritten 2026-11-20 (the model is the owner's choice; checks fixed on Opus).
Replaces, for development work, the Track B table and §0 #9 of the career repository's task_model_allocation.md. -->

## Which model runs which step — a reference, not a rule

The owner chooses the model. This table is what he starts from; the flow only suggests Fable, in the two cases below, and never switches by itself.

| Work | Model |
|---|---|
| A normal or high-risk change — one session from the intent to the merge | Opus |
| A small change | Sonnet; when it turns out not to be small it becomes a normal change, on Opus |
| The verifier and the reviewer subagents (the checks), in every tier | Opus, fixed in their definitions, whatever the session runs on |
| The researcher and the code-reviewer subagents | the session's model |
| A fresh-session review, when the owner asks for one | Opus |

- **Doing and checking are treated differently.** Doing shows when it goes badly — tests fail, the session is stuck, two fix rounds do not get there — so it stays on Opus until then. Checking does not show it: a review that missed a problem and a clean review both report 0 Important (flightcat's first change: the verifier reported 0, and a second run on the same code found that a date which does not exist crashed the page). So the checks are fixed on Opus and do not wait for a visible failure.
- **When the flow suggests Fable.** (1) A mistake in this change would cost a lot: the session says so once, on the spec's one screen, with the facts that make it think so (not just "high risk") — "run the checks, or the whole change, on Fable; your call". (2) The work is not going well and raising the effort level did not fix it. The owner decides; the session does not switch.
- **How Fable reaches a check.** The implementing session names it in the Agent call (`model: fable`): a model named in the call overrides the `model` in the subagent's definition. `CLAUDE_CODE_SUBAGENT_MODEL` does not — the definition comes first — unless `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is set too, which then overrides every subagent and every call. (code.claude.com, sub-agents page, "Choose a model", read 2026-11-20.)
- **Switching the session's model:** in the same session (`/model`), not in a new one — the change's context stays where it is.
- **Before any model switch, raise the effort level first.** Switch only if that still falls short.
- **Worth suggesting Fable from the start for:** a refactor or an architecture decision across the whole project; designing the flow itself.
- **End of the weekly cycle:** when the owner says there is Fable share left before the reset, Fable may take ordinary work — the share does not carry over.
- **Opening self-check:** at the start of a session, compare the work at hand with the model in use; when they do not match, say so once and continue with what the owner chooses.
- **Watch figure:** spec changes after plan approval. If it worsens, suggest that the owner have the plan's pre-read (the reviewer subagent) run on Fable; the session's model stays.
