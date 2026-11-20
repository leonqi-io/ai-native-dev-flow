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
   - make the change. The test files are locked for the whole branch: no new tests, and an existing test is not edited to pass. (A genuinely wrong test: change it and record `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" test-release <path> --why "<why>"` — nobody is asked; the verifier checks it.)
   - run the verify command and paste its literal output under "Verify";
   - run the `code-reviewer` subagent and fix what it reports;
   - commit, then run the `verifier` subagent in the foreground — **its brief is the change folder's name and nothing else**. It reads the intent on `main` and the diff itself and runs `REVIEW.md`'s fixed checks, including "did this small change alter behaviour". Write its report to `specs/<folder>/reports/verify-<n>.md` and its result under "Review"; fix every Important finding and run it again;
   - record the verifier's own count: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/record.py" review --by verifier --important <n> --nit <n> --report specs/<folder>/reports/verify-<n>.md`. The line records the commit checked; a product change after it means running the verifier again (the merge refuses otherwise). The verifier runs on its own fixed model (Opus), not on this session's;
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
- A fresh-session review, when the owner asks for one, reads the small changes merged since the last one again ("did behaviour change"); the state report counts them until then.
- Not for files that are not product (notes, the roadmap's status line, corrections to CLAUDE.md): those are committed directly on a working branch with the reason in the message.
