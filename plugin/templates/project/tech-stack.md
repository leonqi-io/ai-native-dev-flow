# Tech stack — <product>

<!-- Written once per project, at project setup; approved by the owner's commit into `main`.
Holds the technical decisions that CLAUDE.md does not already lock, the form of deployment included.
A source of constraints when a spec is written. -->

## Decisions
- <decision> — <why, in one line> (<who decided, date>)

## Cost of a bad release
<One sentence: what does it cost if production is down or wrong for a few days?>

<!-- The answer decides what the flow asks of this project:
  acceptable   → no staging; validation before release in the local preview; rollback = "revert that merge",
                 not rehearsed; no automatic check after release; the merge is also the release approval.
  unacceptable → (real traffic, money or user data, a commitment to others) a validation environment before
                 release, one rehearsed rollback command, a deterministic check after release, and a release
                 approval separate from the merge. Written in the rules, not enabled today. -->

## Deployment
<!-- Only for a project that deploys. Delete otherwise. -->
- How it deploys: <the merge into `main` triggers the pipeline, which …>
- Where the deploy credentials live: <the CI secret store — never where the agent can reach them>
- Rollback: revert that merge; the pipeline deploys again.
