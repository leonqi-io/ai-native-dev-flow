---
name: validate
description: The owner's validation of a change — walks him through validation.md §0 one step at a time, each step as a block he can paste with its expected result, records the outcome in the Approval log, and turns what he finds into fixes or leftovers. Use when a change is implemented and reviewed and the owner is ready to validate it himself.
when_to_use: 「带我走一遍验收」「开始验收」「走 validation」 · "walk me through validation"
---

# Validation (the owner runs §0)

The owner executes; you hand him each step. He is not sent to read `validation.md` and find the commands himself.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. There has to be a review entry with no Important finding open; otherwise say what is missing.

2. **A validation that only makes sense after a merge** (two branches that must work together) runs on an integration branch; merging that branch into `main` is then the approval.

3. **Walk §0, one step per message:**
   - the one-time setup first;
   - then each step: the command block exactly as written in `validation.md`, and the one sentence of expected result;
   - wait for what he saw. Matches → next step. Does not match → that step failed; note what he saw, word for word.
   - Remind him once, before the first step, of "Do not touch".
   - UI changes: he is at the screen. Ask each "judgment asked of the owner" as its own question.

4. **§3, when present:** give him the comparison command and check its output against "will change" and "must stay byte-equal".

5. **What he finds:**
   - a failed step or a wrong behaviour inside this change's scope → back to the implementing session (the `implement` skill's fix round), then validate that step again;
   - something real but outside this change's scope → a leftover: record it under "Leftovers" with its pointer (a To do line through the `todo` skill, tagged `(<folder name> L<n>)`).

6. **Record** in the Approval log of `validation.md` and commit on the working branch:
   `- <date time> · validation by <owner> · <n> steps, <m> failed · <one line on what was found>`

## Rules
- Speak to the owner in the owner's language. One step per message; no step is skipped or merged with another.
- You do not judge a step in his place: his observation is the result.
- End by saying the next step in one sentence: all steps pass → the close.
