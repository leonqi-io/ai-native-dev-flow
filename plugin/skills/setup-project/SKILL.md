---
name: setup-project
description: Project setup, done once per project before the six stages. Writes specs/mission.md, specs/tech-stack.md and specs/roadmap.md with the owner, plus the project's CLAUDE.md, REVIEW.md and .claude/flow.json. Use when a repository starts using the development flow, or when the state report says the project is not set up.
when_to_use: 「给这个项目立项」「这个仓库开始用开发流程」「写 mission、tech-stack 和 roadmap」 · "set up this project for the flow"
---

# Project setup

Done once per project. The three files sit one level above the single change: the mission is the yardstick for scope, the tech stack is a source of constraints, the roadmap holds what is planned, undecided and knowingly left.

## Steps

1. **Branch.** Work on a branch named `setup` (`git switch -c setup`). Never on `main`.

2. **Read before asking.** Read what the repository already says about the product: README, architecture or design documents, an existing CLAUDE.md, the deploy workflow. Use the `researcher` subagent when there is much to read. What is already written down is not asked again; what is old is checked with the owner against today's reality.

3. **Write the three files with the owner**, from the templates in `${CLAUDE_PLUGIN_ROOT}/templates/project/`. Draft all three first, then run the question loop: follow `${CLAUDE_PLUGIN_ROOT}/reference/question-loop.md`, with the differences its section "At project setup" lists.
   - `specs/mission.md` — the five headings and nothing more: who · what they bring · what they leave with · what they do in between · what this does not do. About one screen.
   - `specs/tech-stack.md` — the technical decisions CLAUDE.md does not already lock, and one sentence: **what does it cost if production is down or wrong for a few days?** For a project that deploys: how it deploys, and where the deploy credentials live. One hard requirement for every deploying project: the credentials sit where the agent cannot reach them (the CI secret store) and the merge triggers the deploy.
   - `specs/roadmap.md` — the status line, the planned stages in order, a "To do" that holds only what the question loop left undecided (empty otherwise), an empty "Known limits".

4. **Write the project's configuration**, from the same template folder:
   - `.claude/flow.json` — its five values are part of the draft: propose each from what the repository shows and put them to the owner in the rounds of step 3: `test_scope` (where the test files are), `deploys` (does a merge publish?), `pull_request` (do changes go through a PR? — yes where there is a remote and a deploy flow), `high_risk_paths` (deploy configuration, credentials), `non_product_paths` (notes and the like). The file's presence is what switches the hooks on.
   - `CLAUDE.md` — keep an existing file; add the "Development flow" and "Verifying your work" blocks of the template to it. Under a page.
   - `REVIEW.md` — the template as it is, plus the project's own policies under "Compliance".
   - `.claude/settings.json` — only if the project has none: the sample, with the verify and format commands filled in.

5. **Check and commit on `setup`.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" mission specs/mission.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" tech-stack specs/tech-stack.md
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check_shape.py" roadmap specs/roadmap.md
   ```

6. **Hand over.** The owner reads the three files and approves them by his commit — give him this line to paste into his own terminal:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/accept.py" setup
   ```

   A later change to the mission, the tech stack or the planned stages is again the owner's commit (the same line), with the reason in the commit message.

## Rules
- Speak to the owner in the owner's language. The files are written in English unless the owner decides otherwise.
- A requirement is scaled to what a failure costs: do not load staging, rehearsed rollbacks or post-release checks onto a project whose bad release is acceptable.
- End by saying the next step in one sentence: after the owner's commit, the first change starts with its intent.
