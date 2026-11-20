---
name: continue
description: Entry point of the development flow. Reads the repository state, says which stage the work is in and what comes next, then loads that stage's skill. Use when the person wants to carry on with development work without naming a step, or asks where things stand.
when_to_use: 「继续」「接着做」「看看现在到哪一步了」「现在该做什么」 · "continue", "where are we"
---

# Continue

1. Run the state script and read its report:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"
   ```

2. Tell the person, in their language, in three short lines: the stage, what is waiting and on whom, the next step. When the report has an "owner's approval" line, show the sentence the owner types (「…」) and say that it has to be a chat message of its own; the terminal line is the fallback.

3. Load the skill of that stage and carry on with it:

   | The report says | Skill |
   |---|---|
   | the flow is not in use, or the project is NOT SET UP | `setup-project` |
   | no change in progress | ask what they want to change → `intent`, or `small-change` when it qualifies |
   | Plan (intent drafted, spec not started) | `intent`, then `spec` |
   | Design | `spec` |
   | Build (the plan is not approved yet) | `plan` |
   | Test, or Build / Test | `implement` (its review loop included) |
   | Validation | `validate` |
   | Close | `close` |
   | Small change | `small-change` |
   | Merged | none — the branch is already in `main`: the owner's「确认合并」only tidies up (switches to `main`, deletes the branch) |

   A normal or high-risk change runs in one session; when a session ended midway, this one picks up at the step the report names — everything a step needs is in the change folder.

4. Mention, in one line each and only when the report has them: the number of open To do lines with the oldest date; small changes not yet read by a fresh session (a fresh-session review reads them when the owner asks for one).

Rules that hold in every stage: `main` moves only by the owner's act — his approval sentence, or his click in a small change; you commit on the working branch only and never run `accept.py`, `merge.py` or `gh pr merge` for him; the review is the reviewer subagent's, with a fresh context and the change folder's name as its only brief; after an approval the work goes on without a stop.
