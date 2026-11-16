# Review instructions

Read by the review session: a fresh session that did not implement the change. It reports; it does not approve, block or change code. One exception: a single-hunk fix may be done on the spot as a small change and recorded.

## What to read
- The change folder: `intent.md`, `spec.md`, `validation.md`, `plan.md`.
- The branch's diff against `main`.
- `CLAUDE.md` and the policies it points to.

## Passes, in this order
1. **Bugs and logic** — wrong results, unhandled states (empty, error, first use, returning), broken edge cases.
2. **Security** — secrets in code or logs, unchecked input, a wider permission than the change needs.
3. **Compliance** — every R-ID of `spec.md` is met; the diff matches `plan.md` (files, order, proof); the project's policies hold.

## Fixed checks
- **Small change:** did it alter behaviour a user would notice, or touch more than one place? If yes it should have been a normal change — Important.
- **Released test change:** for each `test-release:` entry of the Approval log, did the change weaken the §1 row it belongs to? If yes — Important.
- **Small changes merged since the last fresh-session review** (the state report lists them): read each one's intent and diff, judge "did behaviour change", and add to its Approval log the line `<date time> · small-change read (fresh session) · behaviour changed: yes|no`. A "yes" is reported as Important in this review.
- **`CLAUDE.md`:** does this change make any line of it outdated? A mistake this review flags for the second time is written into `CLAUDE.md` now.

## Severity
- **Important** — wrong behaviour, a security problem, a requirement not met, a departure from the plan that the plan does not record. Handled before the merge. Every Important finding says how to confirm it: a command, or a step of `validation.md`.
- **Nit** — worth a fix, not worth a delay. When there are many of one kind, report the kind once.

## Do not report
- Style, naming, readability, formatting — lint and the code-reviewer own these.
- What `spec.md` lists as out of scope.
- A problem in code the change does not touch — record it as a finding in the roadmap's To do instead.
- Anything in the roadmap's Known limits.

## Output
1. The report: findings grouped by pass, each tagged Important or Nit, with file and line.
2. One line appended to the Approval log of `validation.md`:
   `- <date time> · review (fresh session) · Important open: <n> · Nit: <n>`
3. Where the project uses pull requests: the report posted as a PR comment.
