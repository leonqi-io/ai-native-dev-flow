---
name: review
description: Review of a change by a fresh session that did not implement it, reading the project's REVIEW.md — fixed passes (bugs and logic, security, compliance with spec and plan), findings tagged Important or Nit, a line in the Approval log. Also re-checks findings after a fix round, and gives the second read of a high-risk plan. Use when a branch is ready for review, when fixes are to be re-checked, or when a high-risk plan needs a second read before approval.
when_to_use: 「评审一下这个分支」「评审这个改动」「复核一下修好了没有」「二读这份 plan」 · "review this branch", "re-check the fixes"
---

# Review (a fresh session)

**First:** if this session wrote or edited product files of this change, stop and tell the owner to open a new session. The session that reviews is not the session that implemented. This session reports; it does not approve, block or change code.

## A. Review of a branch

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"` and read the project's `REVIEW.md` — it is the instruction for this review; where it and this skill differ, `REVIEW.md` wins.
2. Read the change folder (`intent.md`, `spec.md`, `validation.md`, `plan.md`), then the diff: `git diff main...HEAD`.
3. Run the verify command and every §2 machine check of `validation.md`; note each result against its expected result.
4. Do the passes of `REVIEW.md` in order, then its fixed checks — including the small changes merged since the last fresh-session review that the state report lists: read each one's intent and diff, and add to its `validation.md` Approval log
   `- <date time> · small-change read (fresh session) · behaviour changed: yes|no`.
5. **Report:** findings grouped by pass, each tagged **Important** or **Nit**, with file and line. Every Important finding says how to confirm it — a command, or a step of `validation.md`. Leave out what `REVIEW.md` lists under "Do not report".
6. **Record:** append to the Approval log of this change's `validation.md`
   `- <date time> · review (fresh session) · Important open: <n> · Nit: <n>`
   and commit on the working branch (a record file, not product).
7. Where the project uses pull requests and a PR exists, post the report as a PR comment (`gh pr comment`).

A single-hunk fix found here may be done on the spot as a small change and recorded; anything larger goes back to the implementing session as a finding.

## B. Re-check after a fix round
Run the confirmation of each Important finding again. Append a new review line with the count still open. Do not edit the earlier line.

## C. Second read of a high-risk plan
Read `intent.md`, `spec.md`, `validation.md` and the draft `plan.md`. Answer: what could break; which step is the riskiest; is the revert path named; could a stranger implement from this plan alone; does every line cite an R-ID or a concern. Report to the owner before he approves the plan, and append
`- <date time> · plan second read (fresh session) · Important open: <n>` to the Approval log.

## Rules
- Speak to the owner in the owner's language.
- A mistake this review flags for the second time is written into `CLAUDE.md` now (two-strike rule); a line of `CLAUDE.md` the change made outdated is reported.
- A problem in code the change does not touch is not a finding of this review — record it with the `todo` skill.
- End by saying the next step in one sentence: Important findings → back to the implementing session; none open → the owner's validation.
