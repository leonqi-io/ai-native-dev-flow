---
name: plan
description: Build stage, first step, in the change's one session. From the accepted spec and validation, drafts the plan in Claude Code's plan mode — what could break, the riskiest step, the alternatives rejected, the points to rule, then files that change, order of work, risks, proof — has the reviewer subagent pre-read spec and plan, and hands it to the owner; his acceptance of the plan in plan mode is the plan approval, and the implementation follows in the same session. Use when the spec of a change is accepted and the implementation plan is to be written.
when_to_use: 「spec 和 validation 批了，出实现计划」「写 plan」「做实现计划」 · "the spec is accepted, write the plan"
---

# Plan (Build stage)

The last part of the owner's first sitting: the last time, before any code, that he learns how the change will be done.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. `spec.md` and `validation.md` have to be on `main`.

2. **Plan mode.** Enter plan mode on the working branch. Have the `researcher` re-check the spec's codebase facts at the current HEAD and write that HEAD into the plan.

3. **Draft the plan** from `${CLAUDE_PLUGIN_ROOT}/templates/change/plan.md`:
   - **For the owner** — four parts, always: what could break, the riskiest step, the alternatives rejected (and why), the points he must rule (each with a default). High-risk tier: the revert path too (a project whose bad release is acceptable names the path; no rehearsal).
   - **Files that change** — every product file the change touches, test files included, in backticks, one path group per list item. The drift check compares the branch's diff with this list.
   - **Order of work** — where the test runner does not exist yet, step 0 builds the toolchain skeleton (manifest and lock files, the runner and its configuration, no product code) and names each side's runner; then the tests of validation §1, named and counted from its rows; then the steps, each citing R-IDs or concerns.
   - **Risks**, **Proof** — proof includes "the screenshot matches the mock" for a UI change.
   - **Spec changed after acceptance**, **Departures** — `- None.` for now; they are filled as the work goes.
   - **Parallel split** — only when the work has disjoint file sets: the shared step first and then frozen, the streams, shared non-file resources (the dev-server port; the browser is used by one session at a time), the merge order and the check after it. Start with two streams; review is the ceiling.

4. **The bar.** An engineer who has not seen this conversation could implement the change from this plan alone. Every line cites an R-ID or a concern.

5. **Pre-read.** Run the `reviewer` subagent on the draft. Its brief: the change folder's name and the path of the plan draft — nothing else. It runs on its own fixed model; only when the owner has accepted the suggestion to run the checks on Fable, name it in the call (`model: fable`). Fold what it finds into the plan: a fix, or a point for the owner to rule. Its report stays in this conversation (plan mode writes no file); the folded result is what the owner reads.

6. **Hand over.** Leave plan mode with the plan (ExitPlanMode). The owner reads "For the owner", asks until he is satisfied — you answer and revise the plan in plan mode — and accepts it. **His acceptance is the plan approval:** the plugin's hook writes the accepted text, unchanged, as `specs/<folder>/plan.md`, writes the approval mark next to it and commits both on the working branch; its result reaches you as context. When he sends the plan back instead, revise and leave plan mode again.
   - If he accepted and no "plan approved" came back: write the accepted plan to `specs/<folder>/plan.md` unchanged, commit it, check its shape, and ask him to type **「批准 plan」** as a chat message of its own — the same mark is then written.

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" plan specs/<folder>/plan.md
   ```

7. **Then, without a stop:** the implementation (the `implement` skill), in this session.

## Rules
- Speak to the owner in the owner's language.
- You commit only on the working branch. No code and no tests before the plan approval — the hook refuses them.
- After the approval the plan changes only through its Departures and "Spec changed after acceptance" sections (and "Files that change"), each in the same commit as the departure. A later trip into plan mode — to plan a fix round — does not replace `plan.md`.
