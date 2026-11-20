# Validation: <title>

Spec: `specs/<folder>/spec.md`

## §0 Owner's part
<!-- Two parts, shown together on the end screen.
Inventory: what can be counted or compared — run a command, compare its output, count what a page shows.
The session does every step itself (terminal or browser) and lists the results; the owner glances at the list.
Judgments: what only the owner can answer. Each carries an ID and one sentence on what a right answer shows.
Strike a question whose object is test material, that is already ruled, or whose right answer shows nothing.
The owner may answer "not judged": recorded, with a Leftovers line saying where the question goes. -->

### Inventory (done by the session)

**One-time setup**

```bash
<command>
```
Expected: <one sentence>.

1. <what this step shows> (R1)

```bash
<command>
```
Expected: <one sentence>.

**Do not touch:** <real data or a real environment that has to stay as it is — or "nothing">.

### Judgments (the owner's)
- **J1** <a question only a person can answer: wording, layout, "does this read right"> (R2) — a right answer shows: <what>.

## §1 Test requirements
<!-- One row per asserted behaviour. The plan names and counts the tests from this table,
and it is the yardstick for "was a red test weakened afterwards". -->
| Row | R-ID | Behaviour asserted | Kind of test |
|---|---|---|---|
| T1 | R1 | <behaviour> | <unit / integration / end-to-end> |

## §2 Machine checks
<!-- Checks specific to this change: a command with its expected result, run by the verifier and the review session.
Delete this section when there are none. A change to the product's model behaviour (a prompt, a model,
a retrieval parameter, a threshold) names the project's product-eval command here. -->
| Check | Command | Expected result |
|---|---|---|
| M1 (R2) | `<command>` | <output> |

## §3 Expected changes
<!-- Only when validation touches real data or a real environment; mandatory in the high-risk tier.
Delete this section otherwise. -->
- Will change: <what>
- Must stay byte-equal: <what>
- Comparison command: `<command>`

## Leftovers
<!-- Nothing left open stays only here. Forms:
  **L1** <what> → specs/<new folder>/intent.md
  **L2** <what> → roadmap: to do          (the roadmap line ends with "(<this folder's name> L2)")
  **L3** <what> → roadmap: known limits   (same tag)
Write "- None." when nothing is left. -->
- None.

## Approval log
<!-- Appended, never rewritten. The lines the scripts read are written by record.py (review, validation,
test-release, ruling); its docstring has their form. Other entries are free text. -->
