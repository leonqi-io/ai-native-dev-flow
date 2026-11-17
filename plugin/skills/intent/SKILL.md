---
name: intent
description: Plan stage. Captures a wanted change as intent.md in a new change folder — problem, proposed outcome, affected users, constraints, open questions, out of scope — through a bounded question loop, and hands it to the owner for "intent accepted". Use when the person describes a new feature, a fix or a change they want that is more than a small change.
when_to_use: 「我想加一个功能：……」「我想做一个改动：……」「写一份 intent」「这个问题要修，先写 intent」 · "I want to add …", "write the intent for …"
---

# Intent (Plan stage)

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. The project has to be set up. If a change is already in progress on this branch, continue that one.

2. **Tier.** Decide it from what the person said, and say which one you chose and why:
   - **small** — no behaviour a user would notice changes, or one place only (typo, copy, a config value, a dependency bump, a single-hunk fix). → Stop here and use the `small-change` skill.
   - **high-risk** — the change touches any of: an irreversible data change · credentials or personal data · public release or deploy configuration · a stored or emitted data shape.
   - **normal** — everything else.

3. **Folder and branch.** The folder is `specs/<YYYY-MM-DD>-<slug>/` (today's local date); the working branch has the folder's name. Bring `main` up to date first (it does nothing where there is no origin):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync_main.py"
   git switch -c <YYYY-MM-DD>-<slug> main
   ```

4. **Draft `intent.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/intent.md`, in the owner's words where they gave them. The problem carries a number. "Source" says who raised it and when, or which To do line or leftover it comes from.

5. **Question loop.** Follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`. In this stage ask what, why, for whom, constraints and out of scope — never how. Look a scope question up in `specs/mission.md` before asking it.

6. **Mission conflict.** If the intent asks for something `specs/mission.md` says the product does not do, stop and say so: the owner amends the mission first (the amended file is committed on this branch and he types「接受立项」, which here commits the project files only), then the intent is accepted. No intent goes out of scope silently.

7. **Check and commit on the working branch.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" intent specs/<folder>/intent.md
   ```

8. **Hand over.** The owner reads `intent.md` and accepts it by typing **「接受 intent」** as a chat message of its own. The plugin's hook then runs `accept.py intent` and its result reaches you as context; when it says "intent accepted", carry on. You cannot run it for him in this tier. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

9. **If the intent came from a To do line:** once it is accepted, remove the line (the owner confirms with one click):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" delete --match "<text of the line>" --reason fix-now
   ```

## Rules
- Speak to the owner in the owner's language.
- No `Status` field: on the branch the intent is a draft, on `main` it is accepted.
- You commit only on the working branch. `main` moves by the owner's act — his sentence, never your call of the script.
- End by saying the next step in one sentence: after "intent accepted", the spec.
