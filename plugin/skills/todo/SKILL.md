---
name: todo
description: The way into the development flow for findings. Records a noticed problem or wish as one line in the roadmap's "To do" section, and goes through the open lines with the owner to decide each one — fix now, schedule, or dismiss. Use when someone notices something about the product that is not part of the current change, or when the owner wants to go through the open findings.
when_to_use: 「记一条待办：……」「这个先记下来以后再说」「过一遍待办」「处理待办」 · "note this for later", "go through the to-do list"
---

# To do (the way in, and the triage)

The "To do" section of `specs/roadmap.md` holds **undecided findings only** — one line each. It is not an archive: a line leaves as soon as it is decided.

Scope: the development flow covers changes to the product in the repository — code, site, configuration. A work process that *uses* the product is not its business; what crosses over is a person saying, from that work, that the product needs a change.

## Record a finding

One line, in the words it was given. No analysis, no intent yet.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/todo_add.py" --who "<who raised it>" "<one sentence>"
```

Several findings go in one call; a `--who` names who raised the sentences after it, up to the next `--who`.

The script commits the line straight to `main` (it can only append to that section), so the finding is recorded at once. A leftover of a change ends its sentence with the tag `(<folder name> L<n>)`.

## Go through the open lines

List them (the state report gives the count and the oldest date; the lines are in `specs/roadmap.md` on `main`). For each, the owner decides — one question per line, with your default:

| Decision | What happens |
|---|---|
| **Fix now** | Write the intent (`intent` skill, or `small-change` when it qualifies); its "Source" names the line. Then `roadmap_edit.py delete --match "<text>" --reason fix-now`. |
| **Schedule** | `roadmap_edit.py move --match "<text>"` — the sentence joins "Planned stages". |
| **Dismiss** | `roadmap_edit.py delete --match "<text>" --reason dismissed` — Git history keeps it. |
| **Already fixed** — not a product file, corrected directly on a working branch | `roadmap_edit.py delete --match "<text>" --reason fixed-directly --commit <hash>` — after the correction is committed. |

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/roadmap_edit.py" <delete|move> --match "<text>" [--reason fix-now|dismissed|fixed-directly --commit <hash>]
```

Run it alone; the owner confirms each with one click. This script is the only way a line leaves: do not edit the To do section in `specs/roadmap.md` yourself, on any branch — the hook refuses the edit and the close check refuses the branch. A kind of request that keeps coming back and keeps being dismissed belongs in the mission's "What this does not do" — propose the line; the mission changes by the owner's commit.

## Known limits
"Known limits" is a different section: defects knowingly left as they are. A line enters it only when a change is closed with such a leftover, and leaves when the defect is fixed.

## Rules
- Speak to the owner in the owner's language.
- Do not start fixing a finding from here; "fix now" starts a change of its own.
- End by saying, in one sentence, how many lines are still open.
