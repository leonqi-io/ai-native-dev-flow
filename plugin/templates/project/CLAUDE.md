# <Project> — instructions for Claude

<!-- Keep this under a page. It holds what a session needs every time; everything else is a pointer. -->
<!-- flow-template: 2026-11-21 — the date the "Development flow" section was last brought in step with the plugin's template; the state report says when the template is newer. -->

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
- A normal or high-risk change runs in one session, from the intent to the merge; after each approval the work goes on without a stop — except where the owner chose, at the plan, to stop after its approval. The owner approves three times: 「接受 spec」 (intent, spec and validation together), the plan (accepting it in plan mode), 「确认合并」. A small change: two clicks.
- `main` moves only by the owner's act. You work and commit on the working branch, which is named after its change folder `specs/<date>-<slug>/`. An approval sentence is a chat message of its own, and the plugin's hook runs the script; you never run `accept.py`, `merge.py` or `gh pr merge` for him.
- Where there is an origin: before a branch is started from `main`, and after a pull request was merged on GitHub, bring `main` up to date with the plugin's `sync_main.py` (the state report prints the line when `main` is behind). You do not pull or push `main` yourself.
- Pull requests: <yes — the reports in the change folder are posted as a PR comment | no>.
- Not product, committed directly on the working branch with the reason in the message: notes, the roadmap's status line, corrections to this file, and what this change's rulings bring to the roadmap's planned stages and to `specs/decisions.md`. The roadmap's To do lines are not edited on a branch: they enter through `todo_add.py` and leave through `roadmap_edit.py`.
- When the owner wants a second pair of eyes on something this session wrote: start a subagent with no context, give it the text and one specific question, and report what it says. Explanations, questions and rulings stay between him and this session.
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
