# Spec: <title>

Intent: `specs/<folder>/intent.md`
Policies and skills read: <name at version or commit — or "none">

## Requirements
<!-- One atomic, testable behaviour per ID. Cover the empty, error, first-use and returning states.
Every R-ID has to be cited in validation.md §0, §1 or §2 — a script refuses the commit otherwise.
A requirement over open input (it recognises or parses free text, an outside page or file) names three things:
the forms it must get right (those in the real samples, and those named), what catches a form outside that list,
and that a form outside the list found in review is a leftover. -->
- **R1** <behaviour>
- **R2** <behaviour>

## Design
<How the requirements are met: parts, data, flow. For a UI change the mock is `mock.html` in this folder; it is the design, and the Mock section below records its review.>

## Constraint trace
| Constraint (from the intent) | Where the spec meets it |
|---|---|
| <constraint> | <R-ID or design part> |

## Open-question trace
| Open question (from the intent) | Answer, or the concern that carries it |
|---|---|
| <question> | <answer, or C1> |

## Mock
<!-- UI change only — delete this section when the folder holds no mock.html.
The mock review: the mock is measured against what it replaces, every difference is either meant (it cites a
requirement or a ruling) or the mock is corrected, and a person looks at the mock itself before the spec is accepted.
"Confirmed by" stays empty until that person has opened mock.html; the spec is not accepted without it. -->
- Measured against: <the earlier mockup or the present page it replaces, as a path or URL — or "nothing: a new page">
- Looked at in: <browser, and the widths the requirements name>
- Confirmed by:

| Block | Before | In the mock | Meant by |
|---|---|---|---|
| <header / footer / a section> | <what it was> | <what it is now> | <R-ID or ruling — never empty> |

## Outputs a person reads
<!-- Delete this section when the change makes no output that a person other than the developer reads.
One row per such output: a report, a listing, an email, a message. The sample is a file in this folder, written
before any code, that shows the output as its reader will get it — its language, its sections, its columns — with
values of the kind the real data holds and no value shown as it is stored. "Confirmed by" stays empty until that
person (or the owner for them) has read the sample itself; the spec is not accepted with a row whose sample is
missing or not confirmed. After that the output's language and layout are ruled. -->
| Output | Who reads it | Language | Sample | Confirmed by |
|---|---|---|---|---|
| <the report / listing / message> | <who — not always the one who runs the command> | <language> | `<file in this folder>` | |

## Fact values
<!-- Every value the product will show or store that comes from outside the code — a name, a price, an address,
a text someone approved. The owner confirms each one at the start; a value nobody confirmed is not built in.
"Confirmed as" says whether the wording itself was approved (content) or only where it sits (layout). -->
| Value | Source | Confirmed by | Confirmed as |
|---|---|---|---|
| <value> | <where it comes from> | <who, date — or "open"> | <content / layout> |

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
