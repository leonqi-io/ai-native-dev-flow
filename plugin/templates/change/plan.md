# Plan: <title>

Spec: `specs/<folder>/spec.md` · Validation: `specs/<folder>/validation.md`
Facts checked at HEAD <sha>.

## For the owner
<!-- The one section the owner reads before he accepts the plan in plan mode — that acceptance is the approval.
Four parts, always; the reviewer subagent has read the spec and this plan once before the owner sees it. -->
- What could break: <...>
- Riskiest step: <...>
- Alternatives rejected: <what, and why>
- Points to rule: <a decision the plan needs, with its default — or "None.">
- Revert path: <high-risk tier only — how this is undone. A project whose bad release is acceptable names the path; no rehearsal.>

## Files that change
<!-- Every product file the change touches, in backticks (a glob is allowed; square brackets are literal).
One path group per list item; a path on an indented line continuing the item counts too.
The drift check compares the branch's diff with this list; a departure updates this list in the same commit. -->
- `<path>` — <what changes> (R1)

## Order of work
<!-- Where the test runner does not exist yet, step 0 builds the toolchain skeleton — manifest and lock files,
the test runner and its configuration, no product code — so the red run fails row by row, not with "no project".
Name the runner of each side. Delete step 0 otherwise. -->
0. Toolchain skeleton: <files>; test runner <name> (<side>).
1. Tests of validation §1 (rows T1–Tn: <count> tests in `<files>`); formatter on the test files; the red run committed with `red-run.txt`.
2. <step> (R1, C1)

## Risks
- <risk> — <how the plan limits it>

## Proof
- The verify command is green, its output pasted.
- The §2 machine checks M1–Mn pass.
- <UI change: the screenshot matches `mock.html` in the states the spec names.>

## Spec changed after acceptance
<!-- Every change to spec.md or validation.md after "spec accepted": what changed, why, and the owner's ruling it rests on. -->
- None.

## Departures
<!-- Every departure from this plan during the work, written in the same commit as the departure: what, and why. -->
- None.

## Parallel split
<!-- Only when the work has disjoint file sets; delete this section otherwise. -->
- Shared step, done first and then frozen: <...>
- Streams: <A: files> · <B: files>
- Shared non-file resources: <dev-server port; the browser — one session at a time>
- Merge order and the check after the merge: <...>
