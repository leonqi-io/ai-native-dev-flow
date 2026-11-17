---
name: close
description: Closes a normal or high-risk change before its merge — settles the leftovers, updates the roadmap's status line, runs the deterministic close check, then hands the merge to the owner (his approval sentence merges the branch, or the pull request). Use when a change has passed review and the owner's validation and is ready to be merged.
when_to_use: 「验收过了，收尾准备合并」「收尾」「准备合并」 · "validation passed, close it"
---

# Close (before the merge)

## Steps

1. **Leftovers.** Every bullet under "Leftovers" in `validation.md` points somewhere; nothing left open stays only in its own folder:
   - to be fixed → `**L1** … → specs/<new folder>/intent.md` (the new intent's "Source" names this leftover);
   - undecided → `**L2** … → roadmap: to do`, and add the line with its tag:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/todo_add.py" --who "<who raised it>" "<one sentence> (<folder name> L2)"
     ```

   - accepted as it is → `**L3** … → roadmap: known limits`, and add `- <one sentence> (<folder name> L3)` to "Known limits" in `specs/roadmap.md` on this branch;
   - nothing left → `- None.`

2. **Roadmap.** On this branch, update the `Status:` line of `specs/roadmap.md` (where the work stands, what comes next). Look at the To do lines: what this change settles can be disposed of now — the owner confirms each with one click:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" delete --match "<text>" --reason fix-now
   ```

3. **`CLAUDE.md`.** A mistake corrected twice during this change is written under "Things Claude gets wrong here"; a line the change made outdated is fixed.

4. **Commit on the working branch, then run the close check** and fix what it refuses:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/close_check.py"
   ```

   It checks: the shape of every file, R-ID coverage, no unreleased change to a test file since the red commit, no changed product file missing from the plan, every leftover's pointer, and a fresh-session review entry with no Important finding open.

5. **The merge is the owner's act: he types 「确认合并」 as a chat message of its own.** The plugin's hook then runs `merge.py` and its result reaches you as context. Before you ask for the sentence:
   - **Project without pull requests:** nothing more. The script runs the close check again, moves `main` to this branch's head and pushes `main` where there is an origin.
   - **Project with pull requests:** push the branch and open the PR.

     ```bash
     git push -u origin <branch>
     gh pr create --base main --title "<title>" --body-file <file>
     ```

     Where a merge publishes (`deploys: true`), the PR description's first line is exactly: **Merging publishes to production.** Then the intent in two lines, and the pasted output of the close check. Post the review report as a PR comment if it is not there yet. The script runs the close check again, merges the PR (`gh pr merge --merge`) and brings local `main` up to date. If the owner merges on the GitHub page instead, he types the sentence afterwards and the script only tidies up.

   After the merge the checkout is on `main` and the working branch is deleted, here and on origin. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

## Rules
- Speak to the owner in the owner's language.
- You do not merge, you do not run `gh pr merge`, and you do not push `main`. A small change does not use this skill — its merge is the second click of `small-change`.
- End by saying what happens after the merge in one sentence (where the merge publishes: the pipeline runs now; the rollback is the one `specs/decisions.md` names. Where a release is a separate act: say what that act is).
