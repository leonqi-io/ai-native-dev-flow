# Decisions — <product>

<!-- Written once per project, at project setup; approved by the owner ("接受立项").
The project-level decisions that CLAUDE.md does not already lock: the shape of the product and its stack,
how the work is organised, how it is released. A source of constraints when a spec is written.
A later project-level decision is added here, with who decided and when, and approved by the owner again.
What is still undecided does not belong here — it is a line in the roadmap's To do. -->

## Decisions
<!-- With more than a handful, group them under `###` headings of your own
(for example: Shape and stack · Processes · Where things run · How content reaches `main`). -->
- <decision> — <why, in one line> (<who decided, date>)

## Cost of a bad release
<One sentence: what does it cost if production is down or wrong for a few days?>

<!-- The answer decides what the flow asks of this project:
  acceptable   → no staging; validation before release in the local preview; rollback is one line,
                 not rehearsed; no automatic check after release.
  unacceptable → (real traffic, money or user data, a commitment to others) a validation environment before
                 release, one rehearsed rollback command, a deterministic check after release, and a release
                 approval separate from the merge. Written in the rules, not enabled today. -->

## Deployment
<!-- Only for a project that deploys; delete otherwise. Decided per project — the flow prescribes no form,
it only asks that these five lines are answered. -->
- How a release happens: <for example: the merge into `main` triggers the pipeline, which builds and publishes>
- What triggers it: <the merge | a schedule | the owner's command after the merge | …>
- Where the deploy credentials live, and who or what can reach them: <…>
- Rollback: <for example: revert that merge; the pipeline deploys again>
- Release approval: <the merge itself — where the merge triggers the release | otherwise: who approves a release, and by what act>

<!-- Recommended where nothing speaks against it: the merge triggers the release and the credentials sit where
the agent cannot reach them (a CI secret store). Then nothing goes live without a merge, at no extra work,
and the merge is also the release approval.
`deploys` in .claude/flow.json is true only while a merge publishes: it puts the line
"Merging publishes to production" into the merge prompt and the PR description. A project that releases by
another route — or has switched to a fallback route — sets it to false and names its release approval above. -->
