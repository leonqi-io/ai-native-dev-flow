# ai-native-dev-flow — instructions for Claude

This repository holds our development flow v3: the rules (`docs/`, in Chinese) and the Claude Code plugin `flow` that carries them out (`plugin/`, in English). Private.

## Commands
- Self-test of the scripts and hooks (no model call): `bash tools/selftest.sh` → last line `selftest: N passed, 0 failed`
- Plugin format check: `claude plugin validate plugin`
- One eval case: `claude plugin eval plugin --case pick-<name> --ablation none` (run by the owner, in his own terminal, signed in with the plan)
- Regenerate the phrasing table: `python3 tools/skill_list.py`

## Verifying your work
- A change to `plugin/scripts/` or `plugin/hooks/` is done when `bash tools/selftest.sh` is green and its output is pasted. Add a line to the self-test for every new refusal, prompt or pass.
- A change to `plugin/templates/project/CLAUDE.md`, `REVIEW.md` or `flow.json`: set its `flow-template` mark to today's date in the same change — the state report compares a project's copy with it, and no script checks that the mark was moved.
- A change to a skill's `description` or `when_to_use`: say that its eval case has to be re-run; do not edit the generated block in `docs/skills.md` by hand.

## Conventions
- **Three labels, never mixed:** what we do today · what v3 trials (v3 试行的做法) · written, not enabled (只写不启用). Do not use the word "现行".
- **No gate numbers.** Stages and plays carry the playbook's names; files carry the SDD names.
- **Language:** `docs/` in Chinese; skills, subagents, script comments and templates in English; trigger phrases in `when_to_use` and eval prompts in Chinese.
- **One source per rule.** A rule lives in `docs/flow.md`; a skill restates only what it needs to act. A rule that must hold has one script, used by the skill and the hook.
- **Scripts:** Python 3 standard library only, 3.9-compatible; a hook does nothing where `.claude/flow.json` is missing, and never blocks when it fails itself.
- No number without a basis. A requirement is scaled to what a failure costs.
- A list holds open items only (`docs/pilot.md`, a roadmap's To do); it is not an archive.

## Where things are decided
- Rulings up to the writing of this repository: LoomCV's `dev_flow/notes/sdd_trial_2026-10-30.md`, indexed in `docs/decisions.md`.
- From the start of the pilot: new rulings are appended to `docs/decisions.md`.
- Two rulings that conflict, or a point no ruling covers: stop and ask the owner; do not fill the gap.

## Things Claude gets wrong here
<!-- Two-strike rule. -->
