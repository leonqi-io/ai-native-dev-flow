# Validation: <title>

Spec: `specs/<folder>/spec.md`

## §0 Owner's part
<!-- The only part the owner reads, and the one he runs at validation.
Every step is a block he can paste, followed by one sentence of expected result.
A step whose result does not match is a fail — there is no separate "fails" list. -->

**One-time setup**

```bash
<command>
```
Expected: <one sentence>.

**Steps**

1. <what this step shows> (R1)

```bash
<command>
```
Expected: <one sentence>.

**Do not touch:** <real data or a real environment that has to stay as it is — or "nothing">.

**Judgments asked of the owner:** <what only a person can judge: wording, layout, "does this read right"> (R2)

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
<!-- Appended, never rewritten. Lines the scripts read (each written as a list item):
  <date time> · review (fresh session) · Important open: 0 · Nit: 2
  <date time> · test-release: <path> — <why> — §1 row <T-ID>
Other entries are free text: what was approved, by whom, when. -->
