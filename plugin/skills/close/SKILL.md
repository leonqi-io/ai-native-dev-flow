---
name: close
description: Closes a normal or high-risk change before its merge, in the change's one session right after the end screen — settles the leftovers (the to-do lines in one commit), updates the roadmap's status line as it will read after the merge, runs the deterministic close check, then hands the merge to the owner (his「确认合并」merges the branch, or the pull request). Use when a change has passed its review loop and the owner's end screen and is ready to be merged.
when_to_use: 「验收过了，收尾准备合并」「收尾」「准备合并」 · "validation passed, close it"
---

# Close (before the merge)

## Steps

1. **Leftovers.** Every bullet under "Leftovers" in `validation.md` points somewhere; nothing left open stays only in its own folder:
   - to be fixed → `**L1** … → specs/<new folder>/intent.md` (the new intent's "Source" names this leftover);
   - undecided → `**L2** … → roadmap: to do`;
   - accepted as it is → `**L3** … → roadmap: known limits`;
   - nothing left → `- None.`

   Add all the to-do lines in **one** call — one commit on `main`, one push:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/todo_add.py" --who "review loop" "<one sentence> (<folder name> L2)" "<one sentence> (<folder name> L4)" --who "<owner>" "<one sentence> (<folder name> L5)"
   ```

   Each `--who` names who raised the sentences after it.

   Then bring `main` into this branch before you touch the roadmap here: `git merge main`.

2. **Roadmap, on this branch.**
   - Known limits: add `- <one sentence> (<folder name> L3)` for each such leftover.
   - The `Status:` line says where the work stands **after this merge** and what comes next — no "waiting for the merge".
   - Look at the To do lines: what this change settles can be disposed of now — the owner confirms each with one click:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" delete --match "<text>" --reason fix-now
     ```

     A line whose object is not a product file and that a commit of this branch already fixed (a correction to `CLAUDE.md`, a note): `--reason fixed-directly --commit <hash>`. Never edit the To do section in the file yourself — the hook and the close check refuse it.

3. **`CLAUDE.md`.** A mistake corrected twice during this change is written under "Things Claude gets wrong here"; a line the change made outdated is fixed — the reviewer's reports say which.

4. **Commit on the working branch, then run the close check** and fix what it refuses:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/close_check.py"
   ```

   It checks: the shape of every file (and that a mock is confirmed), R-ID coverage, no change to an existing test file since the red commit that its latest release line does not cover, no changed product file missing from the plan, every leftover's pointer, no To do line of the roadmap changed by this branch itself, the reviewer's latest line with no Important open, its report on disk and no product change after the commit it records, and the latest validation line (every judgment answered, none failed, each one not judged named in Leftovers).

   **When the check refuses because of its own fault** (it misreads a file that is right): stop and tell the owner which check, why you think the check is wrong, and how you would work around it. Touch an approved file only after he agrees, and record his ruling with `record.py ruling`.

5. **The merge is the owner's act: he types 「确认合并」 as a chat message of its own.** The plugin's hook then runs `merge.py` and its result reaches you as context. Before you ask for the sentence:
   - **Project without pull requests:** nothing more. The script runs the close check again, moves `main` to this branch's head and pushes `main` where there is an origin.
   - **Project with pull requests:** push the branch and open the PR.

     ```bash
     git push -u origin <branch>
     gh pr create --base main --title "<title>" --body-file <file>
     ```

     Where a merge publishes now (`deploys: true` in `.claude/flow.json`), the PR description's first line is exactly: **Merging publishes to production.** Then the intent in two lines, and the pasted output of the close check. Post the reports in `specs/<folder>/reports/` as a PR comment. The script runs the close check again, merges the PR (`gh pr merge --merge`) and brings local `main` up to date. If the owner merges on the GitHub page instead, he types the sentence afterwards and the script only tidies up.

   After the merge the checkout is on `main` and the working branch is deleted, here and on origin. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

## Rules
- Speak to the owner in the owner's language.
- You do not merge, you do not run `gh pr merge`, and you do not push `main`. A small change does not use this skill — its merge is the second click of `small-change`.
- End by saying what happens after the merge in one sentence (where the merge publishes: the pipeline runs now; the rollback is the one `specs/decisions.md` names. Where a release is a separate act: say what that act is).
