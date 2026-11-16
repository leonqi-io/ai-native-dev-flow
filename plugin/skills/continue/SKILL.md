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

2. Tell the person, in their language, in three short lines: the stage, what is waiting and on whom, the next step. When the report has an "owner's line", show it as a block they can paste into their own terminal.

3. Load the skill of that stage and carry on with it:

   | The report says | Skill |
   |---|---|
   | the flow is not in use, or the project is NOT SET UP | `setup-project` |
   | no change in progress | ask what they want to change → `intent`, or `small-change` when it qualifies |
   | Plan (intent drafted or being drafted) | `intent` |
   | Design | `spec` |
   | Build (plan.md being written) | `plan` |
   | Test, or Build / Test / Deploy | `implement`; after its report: `review` in a fresh session, then `validate`, then `close` |
   | Small change | `small-change` |

4. Mention, in one line each and only when the report has them: the number of open To do lines with the oldest date; small changes not yet read by a fresh session.

Rules that hold in every stage: `main` moves only by the owner's act — you commit on the working branch only; the session that reviews is not the session that implemented; end by saying the next step in one sentence.
