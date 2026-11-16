# The question loop (Plan and Design)

Used by the `intent` and `spec` skills. Its job: settle missed details and boundaries before they cause rework — in several rounds, each entered with bounds, not refined without end.

## How a round runs
1. **Every round hangs on a draft.** Draft the file from what is known. Questions come from the draft's gaps; answers update the draft.
2. **A question is admitted only if all three hold:**
   - the repository, `specs/mission.md`, `specs/tech-stack.md` and the project's policies do not already answer it (look first — a scope question is looked up in the mission, not asked);
   - it carries a default answer;
   - it says what a wrong answer would cost in rework.
3. **A round's questions come together**, numbered. After each ruling, list the questions still open again, with their defaults, so the owner never scrolls back.
4. **After the answers:** update the draft, then check it against the completeness checklist.

## When the loop stops
It stops when the checklist is met, **or** when a round changed nothing in the draft. What is still open then is carried as a concern (with an owner and a proposal) — it is not asked again.

Completeness checklist:
- the problem carries a number;
- each constraint has its place in the spec;
- the empty, error, first-use and returning states are written;
- out of scope is stated;
- no concern is without an owner.

## What each stage asks
- **Plan (intent):** what, why, for whom, constraints, out of scope. Never how.
- **Design (spec):** behaviour, edge cases, policy conflicts. For a UI change, questions are asked against the mock, not against prose.

## When the owner is not the developer
Her questions are few, in her words, in one batch, relayed by the developer. Technical questions are not hers.

## What the loop cannot catch
- What is visible only on screen → the mock.
- What only a reading of the code finds → codebase facts checked at a HEAD (the researcher), and plan approval.

## The two measures (counted in the pilot, see docs/measures.md)
- Too coarse: spec changes after plan approval; validation findings of the kind "should have been asked".
- Too fine: questions answered on the default that changed nothing in the draft; the loop's wall-clock time.

## Model
When two rounds still fail the checklist, or the draft contradicts itself: say so. The owner raises the effort level first, and switches the model only if that still falls short.
