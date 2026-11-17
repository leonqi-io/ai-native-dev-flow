# The question loop (project setup, Plan and Design)

Used by the `setup-project`, `intent` and `spec` skills. The implementation plan and the review do not use it. Its job: settle missed details and boundaries before they cause rework — in several rounds, each entered with bounds, not refined without end.

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

## At project setup
The `setup-project` skill runs the same rounds, with three differences:
- **The draft is the three project files together** (`specs/mission.md`, `specs/tech-stack.md`, `specs/roadmap.md`) plus the five values of `.claude/flow.json`. The mission and the tech stack are what is being written, so "look first" means the documents the repository already has.
- **The completeness checklist is not used** — it is written for a single change. The loop stops only when a round changed nothing in the draft.
- **What is still open then** becomes a line in the roadmap's "To do" (`<date> · <who raised it> · <one sentence>`), since there is no concern list yet. It is not asked again.

## What each stage asks
- **Project setup:** who the product is for and what it does not do; the technical decisions not yet locked, and how it deploys; what a few days of broken production cost; the planned stages.
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
