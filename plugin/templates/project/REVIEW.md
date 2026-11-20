# Review instructions

Read by the reviewer subagent, which the implementing session runs with the change folder's name as its only brief — and by a fresh-session review when the owner asks for one. The reviewer reports; it does not approve, block or change code.

## What to read
- The change folder: `intent.md`, `spec.md`, `validation.md`, `plan.md`, and the earlier reports in `reports/`.
- The branch's diff against `main`.
- `CLAUDE.md` and the policies it points to.

## Pre-read of the plan
Before the owner sees the plan, the reviewer reads spec, validation and the plan draft once and reports: a requirement the plan does not carry out; a contradiction between the three; a validation step that cannot run as written at that point; a "For the owner" part that is empty or generic; a codebase fact the repository does not bear out.

## Passes, in this order
1. **Bugs and logic** — wrong results, unhandled states (empty, error, first use, returning), broken edge cases.
2. **Security** — secrets in code or logs, unchecked input, a wider permission than the change needs.
3. **Compliance** — every R-ID of `spec.md` is met; the diff matches `plan.md` (files, order, proof, and its Departures section); the project's policies hold.

## Fixed checks
- **Validation steps as written:** run as written, does each step of validation §0, §2 and §3 give its expected result? If not — Important, even when the product is right and the record is wrong. Aligning the record (an exception added to a step) is a fix the owner confirms.
- **Released test change:** for each `test-release:` line of the Approval log, did the change weaken the §1 row it belongs to? If yes — Important.
- **New test-setup file:** a test file the change adds that sets how tests run (a `conftest.py`, the test runner's configuration, a shared fixture or setup file) — does it skip, filter, mark as expected to fail or otherwise alter a test that existed before the lock? If yes — Important. A new test file needs no release line, so this check is the only one on it.
- **Small change:** did it alter behaviour a user would notice, or touch more than one place? If yes it should have been a normal change — Important.
- **Small changes merged since the last fresh-session review** (fresh-session review only; the state report lists them): read each one's intent and diff, judge "did behaviour change", and add to its Approval log the line `<date time> · small-change read (fresh session) · behaviour changed: yes|no`. A "yes" is reported as Important in this review.
- **`CLAUDE.md`:** does this change make any line of it outdated? A mistake this review flags for the second time is written into `CLAUDE.md` now.

## Severity
- **Important** — wrong behaviour, a security problem, a requirement not met, a departure from the plan that the plan does not record, a validation step that does not hold as written. Handled before the owner is called to the end screen. Every Important finding says how to confirm it: a command, or a step of `validation.md`.
- **Nit** — worth a fix, not worth a delay. When there are many of one kind, report the kind once.

## Do not report
- Style, naming, readability, formatting — lint and the code-reviewer own these.
- What `spec.md` lists as out of scope.
- A problem in code the change does not touch — name it under "Outside this change"; the session records it in the roadmap's To do.
- Anything in the roadmap's Known limits.

## Output
1. The report: findings grouped by pass, each with an ID and tagged Important or Nit, with file and line; the validation steps to look at again after the fix; the count `Important: <n> · Nit: <n>`.
2. The implementing session writes the report to `specs/<folder>/reports/review-<n>.md`, adds under it what became of each finding it did not fix (a Leftovers line, or the reason it is not done), and records the line with `record.py review`. The line records the commit reviewed; a product change after it means another round before the close check passes.
3. Where the project uses pull requests: the close posts the reports as a PR comment.
