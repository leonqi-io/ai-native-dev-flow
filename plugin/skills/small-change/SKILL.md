---
name: small-change
description: The small-change path of the development flow — a typo, copy, a config value, a dependency bump or a single-hunk fix. Drafts a short intent, gets the owner's one-click confirmation, then writes validation, makes the change, verifies and reviews without stopping, and halts at the merge prompt. Use when the person or a session says to handle something as a small change, or a requested change alters no behaviour a user would notice or touches one place only.
when_to_use: 「这个按小改动处理：……」「按小改动走」「改个错字」「把这个配置值改一下」 · "handle it as a small change"
---

# Small change

Two touches by the owner, both clicks: the intent, and the merge. In between, no stop.

## Does it qualify?
Small = **no behaviour a user would notice changes, or one place only**. Not small — use the `intent` skill instead: anything that changes behaviour in more than one place; anything touching a path listed under `high_risk_paths` in `.claude/flow.json` (the merge script refuses it); anything that needs a new test. Say which way you decided and why. Under-sizing a change is the risk this path carries: when unsure, it is a normal change.

## Steps

1. **Folder and branch.** Bring `main` up to date first — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync_main.py"` (it does nothing where there is no origin) — then `specs/<YYYY-MM-DD>-<slug>/`, on a branch of the same name: `git switch -c <YYYY-MM-DD>-<slug> main`.

2. **Draft the intent** from `${CLAUDE_PLUGIN_ROOT}/templates/change/intent-small.md` — four or five lines, from the person's sentence: problem, outcome, what must not change, source. `Tier: small`. Commit it on the branch.

3. **First click.** Run this command alone, with nothing chained to it:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/accept.py" intent
   ```

   The owner sees the intent in a prompt and approves. If no prompt appears or the call is refused, ask him to type「接受 intent」as a chat message of its own — the plugin's hook then runs the same script.

4. **Then, without stopping:**
   - write `validation.md` from `${CLAUDE_PLUGIN_ROOT}/templates/change/validation-small.md`;
   - make the change. The test files are locked for the whole branch: no new tests, and an existing test is not edited to pass. (A genuinely wrong test: the edit prompts the owner; then add `- <date time> · test-release: <path> — <why>` to the Approval log.)
   - run the verify command and paste its literal output under "Verify";
   - run the `code-reviewer` subagent and fix what it reports;
   - run the `verifier` subagent — **its brief is the change folder's name and nothing else**. It reads the intent on `main` and the diff itself and runs `REVIEW.md`'s fixed checks, including "did this small change alter behaviour". Write its result under "Review", fix every Important finding and run it again;
   - append `- <date time> · review (verifier) · Important open: <n>` to the Approval log, with the verifier's own count;
   - fill "Leftovers" (each one points to a new intent or to the roadmap; `- None.` otherwise) and commit.

   If the verifier answers that behaviour changed: stop. This is a normal change — say so and start over with the `intent` skill.

5. **Second click.** First `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/merge.py" --check`; when nothing refuses, run alone:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/merge.py"
   ```

   The prompt shows the intent and the changed files and, where a merge publishes, "Merging publishes to production". Stop here; the owner decides. (No prompt: he types「确认合并」as a chat message of its own.) After the merge `main` is pushed where there is an origin, the checkout is on `main` and the branch is deleted.

6. **Afterwards.** If the change came from a To do line, remove it: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" delete --match "<text>" --reason fix-now`.

## Rules
- Speak to the owner in the owner's language.
- The next fresh-session review reads this change again ("did behaviour change") — the independent look is deferred, not dropped.
- Not for files that are not product (notes, the roadmap's status line, corrections to CLAUDE.md): those are committed directly on a working branch with the reason in the message.
