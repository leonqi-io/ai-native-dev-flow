---
name: plan
description: Build stage, first step. From an accepted spec and validation, drafts plan.md in plan mode — files that change, order of work, risks, proof, each citing R-IDs — and hands it to the owner for "plan approved". Use when the spec of a change is accepted and the implementation plan is to be written.
when_to_use: 「spec 和 validation 批了，出实现计划」「写 plan」「做实现计划」 · "the spec is accepted, write the plan"
---

# Plan (Build stage)

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. `spec.md` and `validation.md` have to be on `main`; the hook refuses `plan.md` otherwise.

2. **Plan mode.** Draft in plan mode. Have the `researcher` re-check the spec's codebase facts at the current HEAD and write that HEAD into the plan.

3. **Draft `plan.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/plan.md`:
   - **For the owner** — the one section he has to read: the points he must rule (each with a default), what could break, the riskiest step, the alternatives rejected.
   - **Files that change** — every product file the change touches, test files included, in backticks. The drift check compares the branch's diff with this list.
   - **Order of work** — the tests of validation §1 first, named and counted from its rows; then the steps, each citing R-IDs or concerns.
   - **Risks**, **Proof** — proof includes "the screenshot matches the mock" for a UI change.
   - **Parallel split** — only when the work has disjoint file sets: the shared step first and then frozen, the streams, shared non-file resources (the dev-server port; the browser is used by one session at a time), the merge order and the check after it. Start with two streams; review is the ceiling.

4. **The bar.** A stranger could implement the change from this plan alone. Every line cites an R-ID or a concern.

5. **High-risk tier, in addition:**
   - the plan names the revert path (a project whose bad release is acceptable names the path; no rehearsal);
   - before the owner approves, the plan is read once more by a **fresh session** — tell the owner to open one and say "二读这份 plan" (the `review` skill).

6. **Check and commit on the working branch.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" plan specs/<folder>/plan.md
   ```

7. **Hand over.** The owner reads "For the owner", rules its points, and approves by typing **「批准 plan」** as a chat message of its own. The plugin's hook then runs `accept.py plan` and its result reaches you as context. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

## Rules
- Speak to the owner in the owner's language.
- You commit only on the working branch. No code and no tests before "plan approved" — the hook refuses them.
- End by saying the next step in one sentence: after "plan approved", the red tests.
