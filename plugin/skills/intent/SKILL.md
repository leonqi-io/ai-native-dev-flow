---
name: intent
description: Plan stage, the start of a change's one session. Captures a wanted change as intent.md in a new change folder — problem, proposed outcome, affected users, constraints, open questions, out of scope — through a bounded question loop, then goes straight on to the spec; the owner accepts intent, spec and validation together. Use when the person describes a new feature, a fix or a change they want that is more than a small change.
when_to_use: 「我想加一个功能：……」「我想做一个改动：……」「写一份 intent」「这个问题要修，先写 intent」 · "I want to add …", "write the intent for …"
---

# Intent (Plan stage)

A normal or high-risk change runs in one session, from this skill to the merge. The owner sits down twice: at the start (he says what he wants, answers the questions, confirms the fact values, accepts what the change will be, then reviews the plan) and at the end (one screen of results, his judgments, the merge). This skill is the first part of the start.

## Steps

1. **State.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/state.py"`. The project has to be set up. If a change is already in progress on this branch, continue that one.

2. **Tier.** Propose it from what the person said, and say which one and why; the owner confirms it on the spec's one screen. The tier follows what a mistake would cost, not words in the request:
   - **small** — no behaviour a user would notice changes, or one place only (typo, copy, a config value, a dependency bump, a single-hunk fix). → Stop here and use the `small-change` skill.
   - **high-risk** — a mistake would cost a lot. Usually one of: an irreversible change to data · credentials or personal data · public release or deploy configuration · the stored or emitted shape of data that already exists for real (not a shape nothing real uses yet). Name the facts that make it so.
   - **normal** — everything else.

3. **Folder and branch.** The folder is `specs/<YYYY-MM-DD>-<slug>/` (today's local date); the working branch has the folder's name. Bring `main` up to date first (it does nothing where there is no origin):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync_main.py"
   git switch -c <YYYY-MM-DD>-<slug> main
   ```

4. **Draft `intent.md`** from `${CLAUDE_PLUGIN_ROOT}/templates/change/intent.md`, in the owner's words where they gave them. The problem carries a number. "Source" says who raised it and when, or which To do line or leftover it comes from.

5. **Question loop, straight away.** Do not hand the draft over to be read first: the questions come from its gaps. Follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`. In this stage ask what, why, for whom, constraints and out of scope — never how. Look a scope question up in `specs/mission.md` before asking it.

6. **Mission conflict.** If the intent asks for something `specs/mission.md` says the product does not do, stop and say so: the owner amends the mission first (the amended file is committed on this branch and he types「接受立项」, which here commits the project files only), then the work goes on. No intent goes out of scope silently.

7. **Check and commit on the working branch.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" intent specs/<folder>/intent.md
   ```

8. **Carry on with the spec** (the `spec` skill) in this session, without a stop. The intent is accepted together with the spec and the validation, when the owner types「接受 spec」. A normal or high-risk intent has no approval of its own.

## Rules
- Speak to the owner in the owner's language.
- No `Status` field: on the branch the intent is a draft, on `main` it is accepted.
- You commit only on the working branch. `main` moves by the owner's act — his sentence, never your call of the script.
- A To do line this change comes from is removed after「接受 spec」(the `spec` skill does it).
