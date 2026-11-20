---
name: implement
description: Build and Test stages, in the change's one session. From the approved plan — writes the tests of validation §1 first and commits the red run, implements inside a verify loop until green, then runs code-reviewer → verifier → reviewer, writing each report into the change folder, until the reviewer reports 0 Important; only then goes on to the end screen. Also handles a fix round — after a review, or after what the owner found at the end screen. Use when the plan of a change is approved and the code is to be written, or when findings are to be fixed.
when_to_use: 「plan 批了，开始实现」「开始写代码」「先写红测试」「处理评审意见」「处理验收意见」 · "the plan is approved, implement it", "address the findings"
---

# Implement (Build and Test stages)

The middle of the change. The owner is not here and reads none of the reports: they go to disk. You call him only when (a) something agreed at the start cannot be done or contradicts itself, (b) the same problem has failed two fix rounds, or (c) the next step is irreversible and the start did not authorise it.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. The plan has to be approved ("plan approved: yes"); the hook refuses code and tests otherwise.

2. **Toolchain skeleton**, when the plan has a step 0: manifest and lock files, the test runner and its configuration, no product code. Commit it.

3. **Red first.**
   - Write the tests of validation §1 — the rows and the count the plan names, no more and no fewer.
   - Run the project's formatter on the test files **now** (after the red commit a formatter run on them counts as a change).
   - Run the verify command. The new tests must fail, for the reason the requirement is not met yet.
   - Save the literal output as `specs/<folder>/red-run.txt` and commit the tests and that file together on the working branch.

4. **The test files that exist at the red commit are locked until the merge.** Reaching green is done by implementation, not by changing a test. If a test is genuinely wrong, change it and record the release right away:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" test-release <path> --why "<why>" --row <T-ID>
   ```

   Nobody is asked. The line records the file's content: change the file again and record another line. The reviewer checks whether the change weakened the test, the end screen lists it, and the close check refuses a changed test file whose latest line does not match its content, whatever made the change. A new test file needs no line (a new test-setup file — `conftest.py`, the runner's configuration — is read by the reviewer).

5. **Implement inside the feedback loop.** One verify command (in `CLAUDE.md`), run until green. Commit on the working branch as you go.
   - A departure from the plan: write it under "Departures" in `plan.md` — and update "Files that change" — in the same commit.
   - A change to `spec.md` or `validation.md`: write it under "Spec changed after acceptance" in `plan.md`, with the owner's ruling it rests on.
   - **UI change:** implement → screenshot → compare with `mock.html`, two or three rounds, in this session's own browser. The browser is used by one session at a time.

6. **A ruling the owner gives midway:** before acting on it, check it against validation §0, §3 and the facts in the spec. If it conflicts with one of them, tell him which, in one line, and let him choose. A defect he accepts, or something he leaves for later, goes under "Leftovers" in `validation.md` now (`**L<n>** … → roadmap: known limits` or `→ roadmap: to do`); the roadmap itself changes at the close. Then record the ruling:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" ruling "<the ruling>" --checked "<what it was checked against: §0 J2, §3, R8 …>"
   ```

7. **The review loop**, on committed work, in this order. Each report is written, unchanged, to `specs/<folder>/reports/` and committed (`code-review-<n>.md`, `verify-<n>.md`, `review-<n>.md`, numbered by round):
   1. **`code-reviewer`** on the diff. Fix what it reports.
   2. **`verifier`** — last before the reviewer, **in the foreground**, on the commit you are handing over (commit first; nothing uncommitted). Its brief is the change folder's name and nothing else. A change to a product file after it means running it again; a change to the records under `specs/` alone does not.
   3. **`reviewer`** — its brief is the change folder's name and nothing else. Record its line:

      ```bash
      python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" review --by reviewer --important <n> --nit <n> --report specs/<folder>/reports/review-<n>.md
      ```

   4. **Important findings open:** fix them, confirm each with the command or validation step the finding names, and run the loop again from (1). The reviewer re-checks the earlier findings. **0 Important:** the loop ends.

   The verifier and the reviewer run on their own fixed model (Opus), whatever this session runs on. Only when the owner has accepted the suggestion to run the checks on Fable, name it in both calls (`model: fable`).

   The review line records the commit reviewed (HEAD; commit first — the script refuses uncommitted product changes). A product change after it means another round: the close check refuses it.

   Under each report, add **Disposition**: for every finding you did not fix, where it goes — a Leftovers line in `validation.md` (with its pointer), or the reason it is not done. "Not done" alone is not a disposition.

   Until the loop ends, the owner gets no report; at most one line ("the verifier is running").

8. **Then, without a stop:** the end screen (the `validate` skill), in this session.

## Fix round after the end screen
The owner says what is wrong. Fix it in this session; run the review loop (7) again; show him only what changed, then ask the failed judgments again (the `validate` skill).

## Rules
- Speak to the owner in the owner's language.
- You commit only on the working branch. `main` moves by the owner's act.
- You do not change the accepted validation §0 or §3 to make your own change pass. When the work and those steps conflict, stop and bring it to the owner.
- **Stuck:** when the same problem has failed two fix rounds, stop and say what was tried. The owner raises the effort level first, then decides whether to switch the model; a switch happens in this session (`/model`), not in a new one. You do not switch it yourself.
- Code conventions: names say what they hold; comment what is hard to follow and the why; short functions, shallow nesting, no duplicated logic.
