---
name: spec
description: Design stage, in the change's one session. From the drafted intent, writes spec.md (atomic testable requirements with R-IDs, design, traces, the fact values the owner confirms, codebase facts, concerns with owners) and validation.md (the session's inventory and the owner's judgment questions, test requirements, machine checks), through a bounded question loop, then shows the owner one screen of what the change will be; his「接受 spec」accepts intent, spec and validation together. Use when the intent of a change is drafted and its requirements and design are to be written.
when_to_use: 「intent 写好了，开始写 spec」「写需求和设计」「写 spec 和 validation」 · "write the spec", "the intent is drafted, write the spec"
---

# Spec and validation (Design stage)

The second part of the owner's first sitting. At its end he has confirmed every fact value, struck the judgment questions that mean nothing, and accepted what the change will be.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. `intent.md` has to carry its `Tier:` line; the hook refuses `spec.md` and `validation.md` otherwise.

2. **Facts first.** Use the `researcher` subagent before any question is asked: the code and documents the change touches, each fact with file, line and the HEAD it was read at; the existing test assertions on any data shape about to change.

3. **Draft `spec.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/spec.md`:
   - requirements are atomic and testable, one behaviour per R-ID, including the empty, error, first-use and returning states;
   - every constraint and every open question of the intent is traced;
   - **Fact values:** every value the product will show or store that comes from outside the code (a name, a price, an address, an approved text) — its source, who confirms it, and whether the content or only the layout is confirmed. The owner confirms each one in the question loop; one still "open" at hand-over is a question for him, not a guess;
   - what cannot be closed becomes a numbered concern with a class, a proposal and an **owner**;
   - **UI change:** build the mock (`mock.html` in the change folder) before asking about layout or wording. The mock is the design; it gets its own review (step 7).

4. **Draft `validation.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/validation.md`:
   - **§0 Inventory** — every step that can be counted or compared (run a command, compare its output, count what a page shows): a block, and one sentence of expected result. The session runs these itself at the end; the owner glances at the list.
   - **§0 Judgments** — only what the owner alone can answer, each with an ID (J1, J2 …) and one sentence on what a right answer shows. Do not ask: a question whose object is test material, one already ruled (the layout of a confirmed mock is ruled), one whose right answer shows nothing. **A question a subagent with no context could answer by doing the thing is not a judgment** — write it as an inventory step. For a document another session or another person is to work from, that step is: a subagent that gets only the document and one sample does what it says, and a machine check reads what it produced.
   - **§1 test requirements** — one row per product behaviour that does not exist yet and a test asserts. Checking material (samples, fixtures, records) is not a §1 row; it goes to §2.
   - **§2 machine checks** — a command with its expected result; omit when there are none. A change to the product's model behaviour (a prompt, a model, a retrieval parameter, a threshold) names the project's product-eval command here.
   - **§3 expected changes** — only when validation touches real data or a real environment; mandatory in the high-risk tier, which also includes one pass on real data.
   - **Leftovers**, **Approval log** — last.

5. **Question loop.** Follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`. In this stage ask behaviour, edge cases and policy conflicts; for UI, against the mock. Write each ruling into its concern row; each confirmed fact value into its row.

6. **Too big for one session?** Split the change when any of these holds — no count of requirements decides it:
   - the judgment questions of the end fall into groups that have nothing to do with each other;
   - it changes more than one subsystem;
   - one part could be merged on its own and would hold.
   The parts are separate changes, each with its own folder. Propose the split to the owner with what goes where. The parts not done now are decided work, not findings: write them into the roadmap's "Planned stages" on this branch (they reach `main` with the merge), not into "To do". What the split's rulings change in `specs/decisions.md` is committed on this branch the same way.

7. **Mock review** (a change with a `mock.html`). The owner accepts the design by looking at it, not by reading about it.
   - **What it is measured against:** the earlier mockup or the present page the mock replaces — write its path under "Measured against" in the spec's Mock section; "nothing: a new page" when there is none.
   - **The differences, not listed by you.** You built the mock, so have the `researcher` compare the two block by block. Its brief: the two paths and "list every visible difference" — nothing about what was intended.
   - **Every difference is meant, or the mock is wrong.** A difference that cites a requirement or a ruling is a row of the Mock section's table; one that cites nothing is corrected in the mock.
   - **The owner looks at the mock itself.** Tell him how to open it and at which widths, show him the table of differences, and ask once whether he confirms the mock. What he wants changed is a ruling: write it into its concern row, change the mock, and compare the changed blocks again.
   - **Record who confirmed it:** `- Confirmed by: <who>, <date>` in the Mock section, written only after that person has looked. `accept.py spec` refuses a folder with a mock and no such line.
   - From then on the mock is ruled: the verifier compares the built page with it, and no judgment question of the end reopens the layout.

8. **Dry run.** Have the `researcher` run every command of §0 and §2 against the state the repository will be in at that step, and fix what cannot run as written.

9. **Check and commit on the working branch.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_rid_coverage.py"
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" spec specs/<folder>/spec.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" validation specs/<folder>/validation.md
   ```

10. **One screen: what the change will be.** Show it in one message, short:
   - the tier and one sentence why — it is your proposal, and he changes it with one word (you then edit the `Tier:` line). When you judge that a mistake in this change would cost a lot, add once, after that line, the facts that make you think so (e.g. "it deletes live records and there is no way back") and the suggestion: "run the checks — or the whole change — on Fable; your call". You do not switch the model yourself;
   - what is true when this is done (the intent's outcome, in two or three lines) and what is out of scope;
   - the fact values, each with its confirmation;
   - a UI change: the mock, and who confirmed it (step 7);
   - the judgment questions he will be asked at the end — he strikes any that mean nothing;
   - the open concerns, each with its default, for him to rule.
   Fold his answers into the files and commit. He accepts by typing **「接受 spec」** as a chat message of its own: the plugin's hook runs `accept.py spec`, which commits intent, spec and validation to `main` together and refuses while an R-ID is cited nowhere in §0, §1 or §2, or a mock is not confirmed. Its result reaches you as context. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

11. **Then, without a stop:** if the change came from a To do line, remove it (the owner confirms with one click) — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" delete --match "<text of the line>" --reason fix-now` — and carry on with the plan (the `plan` skill) in this session.

## Rules
- Speak to the owner in the owner's language; where the owner is not the developer, her questions are few, in her words, in one batch.
- No number without a basis; a threshold in a requirement says where it comes from.
- You commit only on the working branch. Changing `spec.md` after acceptance is allowed and shows in the diff — it is counted, and the plan's "Spec changed after acceptance" section says what and why.
