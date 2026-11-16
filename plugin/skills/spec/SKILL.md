---
name: spec
description: Design stage. From an accepted intent, writes spec.md (atomic testable requirements with R-IDs, design, traces, codebase facts, concerns with owners) and validation.md (the owner's steps, test requirements, machine checks), through a bounded question loop, and hands the pair to the owner for "spec accepted". Use when the intent of a change is accepted and its requirements and design are to be written.
when_to_use: 「intent 已经接受了，开始写 spec」「写需求和设计」「写 spec 和 validation」 · "the intent is accepted, write the spec"
---

# Spec and validation (Design stage)

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. `intent.md` has to be on `main`; the hook refuses `spec.md` and `validation.md` otherwise.

2. **Facts first.** Use the `researcher` subagent before any question is asked: the code and documents the change touches, each fact with file, line and the HEAD it was read at; the existing test assertions on any data shape about to change.

3. **Draft `spec.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/spec.md`:
   - requirements are atomic and testable, one behaviour per R-ID, including the empty, error, first-use and returning states;
   - every constraint and every open question of the intent is traced;
   - what cannot be closed becomes a numbered concern with a class, a proposal and an **owner**.
   - **UI change:** build the mock (`mock.html` in the change folder) before asking about layout or wording; it is part of the spec.

4. **Draft `validation.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/validation.md` — its parts are divided by who executes them:
   - **§0 the owner's part** — the only part he reads and runs: every step a block he can paste, with one sentence of expected result; what must not be touched; the judgments asked of him.
   - **§1 test requirements** — one row per asserted behaviour, citing R-IDs.
   - **§2 machine checks** — a command with its expected result; omit when there are none. A change to the product's model behaviour (a prompt, a model, a retrieval parameter, a threshold) names the project's product-eval command here.
   - **§3 expected changes** — only when validation touches real data or a real environment; mandatory in the high-risk tier, which also includes one pass on real data.
   - **Leftovers**, **Approval log** — last.

5. **Question loop.** Follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`. In this stage ask behaviour, edge cases and policy conflicts; for UI, against the mock. Write each ruling into its concern row.

6. **Dry run.** Have the `researcher` run every command of §0 and §2 against the state the repository will be in at that step, and fix what cannot run as written.

7. **Check and commit on the working branch.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_rid_coverage.py"
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" spec specs/<folder>/spec.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" validation specs/<folder>/validation.md
   ```

8. **Hand over.** The owner rules the open concerns, reads `validation.md` §0 (and §3 when present), and accepts the pair by his commit. Give him the line the state report prints (`accept.py spec`). It refuses while an R-ID is cited nowhere in §0, §1 or §2.

## Rules
- Speak to the owner in the owner's language; where the owner is not the developer, her questions are few, in her words, in one batch.
- No number without a basis; a threshold in a requirement says where it comes from.
- You commit only on the working branch. Changing `spec.md` after acceptance is allowed and shows in the diff — it is counted.
- End by saying the next step in one sentence: after "spec accepted", the plan.
