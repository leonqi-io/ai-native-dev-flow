---
name: validate
description: The end screen of a change, in its one session — the session runs the inventory of validation §0 itself (commands, outputs, what pages show) and lists the results; the owner sees one screen and answers only the judgment questions (or "not judged"); a script records his answers. What he finds becomes a fix in this session or a leftover. Use when a change has passed its review loop and the owner is ready for the end screen.
when_to_use: 「带我走一遍验收」「开始验收」「走 validation」「看结果」 · "walk me through validation", "show me the result"
---

# Validation (the end screen)

The owner's second sitting. Everything that can be counted or compared is done before he arrives; he answers only what he alone can answer.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. The latest review has to be the reviewer's with 0 Important open; otherwise the review loop of the `implement` skill is not finished.

2. **A validation that only makes sense after a merge** (two branches that must work together) runs on an integration branch; merging that branch into `main` is then the approval.

3. **The inventory, by you.** Run every inventory step of §0, every §2 check and the §3 comparison yourself — in the terminal, or in the browser for what a page shows — exactly as written. Keep to "Do not touch". A step that does not give its expected result is a failure inside this change: fix it first (the `implement` skill's fix round), then run the inventory again. The owner is not called to a failing inventory.

4. **One screen**, in one message, short:
   - what was built, in two or three lines;
   - the inventory: a table of step, expected, seen — all matching;
   - the judgment questions (J1, J2 …), each with what a right answer shows, and how he looks at it (a link, a command);
   - what differs from what was agreed at the start: the plan's "Spec changed after acceptance" and "Departures", and the ruling lines of the Approval log;
   - the tests changed after the red run and the new ones: the output of `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_test_scope.py"`;
   - the leftovers, each with where it goes, and the findings not fixed with their disposition;
   - the "Not recorded" group of `validation.md`, as one block: he accepts the group, or names the ones to keep. Each one he keeps becomes a Leftovers line with its pointer. Record his answer: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" ruling "not recorded: group accepted" --checked "the end screen"` (or what he kept).

5. **His answers.** Ask the judgments one at a time. Each answer is pass, fail (note what he saw, word for word), or "not judged" (「这题不判断」) — only he can give that one; for it, add a Leftovers line naming the question (J2) and where it goes. You do not answer a judgment in his place.

6. **Record** his answers, and commit on the working branch:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" validation J1=pass J2=not-judged
   ```

   The line carries every answer so far; the close check reads it.

7. **What he finds:**
   - a failed judgment or a wrong behaviour inside this change's scope → fix it in this session (the `implement` skill's fix round, the review loop included); run again the inventory steps the reviewer's latest report lists under "Look at again after the fix"; show him only what changed, ask the failed judgments again and record them;
   - something real but outside this change's scope → a leftover under "Leftovers", with its pointer.

8. **Then, without a stop:** the close (the `close` skill), in this session.

## Rules
- Speak to the owner in the owner's language. One judgment per message.
- His observation is the result of a judgment; the inventory is yours.
