---
name: implement
description: Build and Test stages. From an approved plan — writes the tests of validation §1 first and commits the red run, then implements inside a verify loop until green, runs the code-reviewer and verifier subagents, and reports done with pasted output. Also handles the fix round after a review report. Use when the plan of a change is approved and the code is to be written, or when review findings are to be addressed.
when_to_use: 「plan 批了，开始实现」「开始写代码」「先写红测试」「处理评审意见」 · "the plan is approved, implement it", "address the review findings"
---

# Implement (Build and Test stages)

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. `plan.md` has to be on `main`; the hook refuses code and tests otherwise.

2. **Red first.**
   - Write the tests of validation §1 — the rows and the count the plan names, no more and no fewer.
   - Run the project's formatter on the test files **now** (after the red commit a formatter run on them counts as a change).
   - Run the verify command. The new tests must fail, for the reason the requirement is not met yet.
   - Save the literal output as `specs/<folder>/red-run.txt` and commit the tests and that file together on the working branch.

3. **The test files are locked from that commit until the merge.** Reaching green is done by implementation, not by changing a test. If a test is genuinely wrong: say why in your message, make the edit — the owner gets a prompt — and after his approval add to the Approval log of `validation.md`:

   `- <date time> · test-release: <path> — <why> — §1 row <T-ID>`

   A script before the merge diffs the test files against the red commit and refuses every change without such a line, whatever made the change.

4. **Implement inside the feedback loop.** One verify command (in `CLAUDE.md`), run until green. Commit on the working branch as you go. A departure from the plan updates `plan.md` — its "Files that change" too — in the same commit.
   - **UI change:** implement → screenshot → compare with `mock.html`, two or three rounds, in this session's own browser. The browser is used by one session at a time.
   - **Stuck:** when the same problem has failed two fix rounds, stop and say so. The owner raises the effort level first, then decides on the model.

5. **Before saying "done":**
   - run the `code-reviewer` subagent on the diff and fix what it reports;
   - run the `verifier` subagent — its brief is the change folder's name and nothing else;
   - paste the green output of the verify command. A description of the output is not evidence.

6. **Done** = pasted green output + both reports, with what was fixed. Tell the owner the next step in one sentence: open a **fresh session** and ask it to review this branch. This session does not review its own work.

## When a review report comes back (fix round)
- Address every Important finding; confirm each fix with the command or validation step the finding names. Nits at your discretion.
- Do **not** write a review line into the Approval log yourself. Tell the owner to go back to the review session and ask it to re-check; it appends the new line.
- An Important finding that requires a change to `spec.md` or `plan.md`, or a §2 check that cannot be made to pass: stop and bring it to the owner.

## Rules
- Speak to the owner in the owner's language.
- You commit only on the working branch. `main` moves by the owner's act.
- Code conventions: names say what they hold; comment what is hard to follow and the why; short functions, shallow nesting, no duplicated logic.
