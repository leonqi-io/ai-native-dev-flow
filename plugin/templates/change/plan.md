# Plan: <title>

Spec: `specs/<folder>/spec.md` · Validation: `specs/<folder>/validation.md`
Facts checked at HEAD <sha>.

## For the owner
<!-- The one section the owner has to read before "plan approved". -->
- Points to rule: <a decision the plan needs, with its default — or "None.">
- What could break: <...>
- Riskiest step: <...>
- Alternatives rejected: <what, and why>
- Revert path: <high-risk tier only — how this is undone. A project whose bad release is acceptable names the path; no rehearsal.>

## Files that change
<!-- Every product file the change touches, in backticks (a glob is allowed).
The drift check compares the branch's diff with this list; a departure updates this list in the same commit. -->
- `<path>` — <what changes> (R1)

## Order of work
1. Tests of validation §1 (rows T1–Tn: <count> tests in `<files>`); formatter on the test files; the red run committed with `red-run.txt`.
2. <step> (R1, C1)

## Risks
- <risk> — <how the plan limits it>

## Proof
- The verify command is green, its output pasted.
- The §2 machine checks M1–Mn pass.
- <UI change: the screenshot matches `mock.html` in the states the spec names.>

## Parallel split
<!-- Only when the work has disjoint file sets; delete this section otherwise. -->
- Shared step, done first and then frozen: <...>
- Streams: <A: files> · <B: files>
- Shared non-file resources: <dev-server port; the browser — one session at a time>
- Merge order and the check after the merge: <...>
