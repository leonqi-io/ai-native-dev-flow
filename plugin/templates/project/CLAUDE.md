# <Project> — instructions for Claude

<!-- Keep this under a page. It holds what a session needs every time; everything else is a pointer. -->

## Commands
<!-- Each with what healthy output looks like. -->
- Install: `<command>`
- Run locally: `<command>` → <what you should see>
- Format / lint: `<command>`

## Verifying your work
<!-- One command. "Done" means its literal green output is pasted — not a description of it. -->
- Verify: `<command>` → <the last line of a green run>
- UI changes: open the local preview, take a screenshot, compare it with the change's `mock.html`.

## Development flow
- This repository uses the `flow` plugin (`.claude/flow.json`). Changes to code, content or configuration go through it — a single word included (as a small change).
- The state report at the start of a session says where the work stands. Before any development work, read it; run it again when unsure: the line is in the report.
- `main` moves only by the owner's act. You work and commit on the working branch, which is named after its change folder `specs/<date>-<slug>/`. The owner approves by typing a sentence as a chat message of its own — 「接受 intent」「接受 spec」「批准 plan」「确认合并」 — and the plugin's hook runs the script; you never run `accept.py`, `merge.py` or `gh pr merge` for him.
- Where there is an origin: before a branch is started from `main`, and after a pull request was merged on GitHub, bring `main` up to date with the plugin's `sync_main.py` (the state report prints the line when `main` is behind). You do not pull or push `main` yourself.
- Pull requests: <yes — the project deploys on merge; the review report is posted as a PR comment | no — the review report goes into the Approval log only>.
- Not product, committed directly on the working branch with the reason in the message: notes, the roadmap's status line, corrections to this file.
- Speak to the owner in the owner's language: <language>.

## Conventions
- <a convention specific to this code base>

## Architecture
- <the three or four facts about the structure that a newcomer gets wrong>

## Things Claude gets wrong here
<!-- Two-strike rule: a mistake corrected twice is written here, in the session that corrected it the second time. -->

## Pointers
- Mission, project decisions, roadmap: `specs/mission.md`, `specs/decisions.md`, `specs/roadmap.md`
- Review instructions: `REVIEW.md`
- Policies: <path, with the owner of each>
