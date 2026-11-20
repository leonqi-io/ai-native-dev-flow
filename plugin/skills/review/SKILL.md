---
name: review
description: An extra review of a change by a fresh session, when the owner asks for one — reads the project's REVIEW.md and runs its passes (bugs and logic, security, compliance with spec and plan) and fixed checks, writes the report into the change folder and records the line. Also re-checks the findings of such a review after a fix. The flow's own review is the reviewer subagent inside the implementing session; this skill is the owner's option on top of it. Use when the owner asks for a fresh-session review of a branch, or for a re-check of its findings.
when_to_use: 「评审一下这个分支」「评审这个改动」「复核一下修好了没有」 · "review this branch", "re-check the fixes"
---

# Review (a fresh session, on the owner's request)

**First:** if this session wrote or edited product files of this change, stop and tell the owner to open a new session. This session reports; it does not approve, block or change code.

## A. Review of a branch

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"` and read the project's `REVIEW.md` — it is the instruction for this review; where it and this skill differ, `REVIEW.md` wins.
2. Read the change folder (`intent.md`, `spec.md`, `validation.md`, `plan.md`, the reports in `reports/`), then the diff: `git diff main...HEAD`.
3. Run the verify command and every §2 machine check of `validation.md`; note each result against its expected result.
4. Do the passes of `REVIEW.md` in order, then its fixed checks — including the small changes merged since the last fresh-session review that the state report lists: read each one's intent and diff, and add to its `validation.md` Approval log
   `- <date time> · small-change read (fresh session) · behaviour changed: yes|no`.
5. **Report:** findings grouped by pass, each with an ID and tagged **Important** or **Nit**, with file and line. Every Important finding says how to confirm it — a command, or a step of `validation.md`. List the validation steps to look at again after the fix. Leave out what `REVIEW.md` lists under "Do not report".
6. **Write and record:** write the report to `specs/<folder>/reports/fresh-review-<n>.md`, then

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" review --by fresh-session --important <n> --nit <n> --report specs/<folder>/reports/fresh-review-<n>.md
   ```

   and commit both on the working branch (record files, not product).

A single-hunk fix found here may be done on the spot as a small change and recorded; anything larger goes back to the implementing session as a finding — it reads the report from the folder.

## B. Re-check after a fix
Run the confirmation of each Important finding again. Write the re-check as a new report and record a new line with the count still open. Do not edit the earlier line.

## Rules
- Speak to the owner in the owner's language.
- A mistake this review flags for the second time is written into `CLAUDE.md` now (two-strike rule); a line of `CLAUDE.md` the change made outdated is reported.
- A problem in code the change does not touch is not a finding of this review — record it with the `todo` skill.
- End by saying the next step in one sentence: Important findings → the implementing session fixes them (its review loop runs again); none open → back to where the change stood.
