---
name: setup-project
description: Project setup, done once per project before the six stages. Writes specs/mission.md, specs/decisions.md and specs/roadmap.md with the owner, plus the project's CLAUDE.md, REVIEW.md and .claude/flow.json. Use when a repository starts using the development flow, or when the state report says the project is not set up.
when_to_use: 「给这个项目立项」「这个仓库开始用开发流程」「写 mission、decisions 和 roadmap」 · "set up this project for the flow"
---

# Project setup

Done once per project. The three files sit one level above the single change: the mission is the yardstick for scope, the decisions file is a source of constraints, the roadmap holds what is planned, undecided and knowingly left.

## Steps

1. **Branch.** Work on a branch named `setup` (`git switch -c setup`). Never on `main`. Everything written during setup — an inventory, a note the CLAUDE.md points to — is committed on this branch: the acceptance carries the whole branch to `main`.

2. **Read before asking.** Read what the repository already says about the product: README, architecture or design documents, an existing CLAUDE.md, the deploy workflow. Use the `researcher` subagent when there is much to read. What is already written down is not asked again; what is old is checked with the owner against today's reality.

3. **Write the three files with the owner**, from the templates in `${CLAUDE_PLUGIN_ROOT}/templates/project/`. Draft all three first, then run the question loop: follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`, with the differences its section "At project setup" lists.
   - `specs/mission.md` — the five headings and nothing more: who · what they bring · what they leave with · what they do in between · what this does not do. About one screen.
   - `specs/decisions.md` — the project-level decisions CLAUDE.md does not already lock (the shape of the product and its stack, how the work is organised, how it is released), and one sentence: **what does it cost if production is down or wrong for a few days?** What is still undecided is not written here; it becomes a To do line.
     **Deployment is decided per project** — the flow prescribes no form. For a project that deploys, the "Deployment" section answers five lines: how a release happens, what triggers it, where the deploy credentials live and who or what can reach them, how to roll back, and what the release approval is. Recommend, where nothing speaks against it, that the merge triggers the release and the credentials sit where the agent cannot reach them (a CI secret store): nothing then goes live without a merge, and the merge is also the release approval. Do not require it. Where a release is not triggered by the merge, the section names who approves a release and by what act.
   - `specs/roadmap.md` — the status line, the planned stages in order, a "To do" that holds only what the question loop left undecided (empty otherwise), an empty "Known limits".

4. **Write the project's configuration**, from the same template folder:
   - `.claude/flow.json` — its five values are part of the draft: propose each from what the repository shows and put them to the owner in the rounds of step 3: `test_scope` (where the test files are), `deploys` (does a merge publish now? — true only while the merge itself triggers the release; where the pipeline does not exist yet, false until the change that connects it), `pull_request` (do changes go through a PR? — yes where there is a remote and a deploy flow), `high_risk_paths` (deploy configuration, credentials), `non_product_paths` (notes and the like). The file's presence is what switches the hooks on.
   - `CLAUDE.md` — keep an existing file; add the "Development flow" and "Verifying your work" blocks of the template to it. Under a page.
   - `REVIEW.md` — the template as it is, plus the project's own policies under "Compliance".
   - `.claude/settings.json` — only if the project has none: the sample, with the verify and format commands filled in.

5. **Check and commit on `setup`.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" mission specs/mission.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" decisions specs/decisions.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" roadmap specs/roadmap.md
   ```

6. **Hand over.** Show the owner what will land on `main`:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/accept.py" setup --check
   ```

   Give him its list as it is — the project files, then everything else the branch carries, then anything not committed (commit it or say why it stays out). He reads the three files and approves by typing **「接受立项」** as a chat message of its own. The plugin's hook then runs the acceptance and its result reaches you as context: `main` moves to the head of `setup` and is pushed where there is an origin, the checkout switches to `main`, and `setup` is deleted. You do not run `accept.py setup` yourself. If nothing comes back after his sentence, the plugin's hooks are not running in this session: give him the line the state report prints, for his own terminal.

   A later change to the mission, the decisions or the planned stages is made on a working branch and approved with the same sentence; there it commits the project files only.

## Rules
- Speak to the owner in the owner's language. The files are written in English unless the owner decides otherwise.
- A requirement is scaled to what a failure costs: do not load staging, rehearsed rollbacks or post-release checks onto a project whose bad release is acceptable.
- End by saying the next step in one sentence: after「接受立项」, the first change starts with its intent.
