# Spec: <title>

Intent: `specs/<folder>/intent.md` (accepted on `main`, commit <sha>)
Policies and skills read: <name at version or commit — or "none">

## Requirements
<!-- One atomic, testable behaviour per ID. Cover the empty, error, first-use and returning states.
Every R-ID has to be cited in validation.md §0, §1 or §2 — a script refuses the commit otherwise. -->
- **R1** <behaviour>
- **R2** <behaviour>

## Design
<How the requirements are met: parts, data, flow. For a UI change the mock is `mock.html` in this folder and is part of the spec.>

## Constraint trace
| Constraint (from the intent) | Where the spec meets it |
|---|---|
| <constraint> | <R-ID or design part> |

## Open-question trace
| Open question (from the intent) | Answer, or the concern that carries it |
|---|---|
| <question> | <answer, or C1> |

## Codebase facts
<!-- Reported by the researcher: each fact with file, line and the HEAD it was read at. -->
- <fact> — `<path>:<line>` at <sha>

## Amendments to earlier decisions
- <the decision being changed, where it is recorded, what it becomes — or "None.">

## Concerns
<!-- What the question loop could not close. The owner's ruling is written into the row; no concern without an owner. -->
| ID | Class | Concern | Proposal | Owner | Ruling |
|---|---|---|---|---|---|
| C1 | <policy / UX / technical / scope> | <concern> | <default> | <owner> | <ruling and date> |

## Out of scope
- <carried from the intent, plus what the question loop ruled out>
