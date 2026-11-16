#!/usr/bin/env python3
"""Leftovers pointer check: nothing left open stays only in its own folder.

Each bullet of validation.md's Leftovers section has to point somewhere:

    - **L1** <what is left> → specs/<new folder>/intent.md      (to be fixed: a new intent)
    - **L2** <what is left> → roadmap: to do                    (undecided)
    - **L3** <what is left> → roadmap: known limits             (accepted as is)
    - None.

For the two roadmap pointers, specs/roadmap.md (on `main` or in the working
tree) must carry a line containing `(<folder name> L2)` in that section.

Usage: check_leftovers.py [<change folder>]
"""

import re
import sys

import flowlib

ID = re.compile(r"^- \*{0,2}(L\d+)\b")
INTENT_POINTER = re.compile(r"→\s*(specs/[^\s]+/intent\.md)")
ROADMAP_POINTER = re.compile(r"→\s*roadmap:\s*(to do|known limits)", re.IGNORECASE)


def roadmap_sections(root, heading):
    """The section's text on main and in the working tree, joined."""
    texts = [flowlib.roadmap_on_main(root), flowlib.read_worktree(root, flowlib.ROADMAP)]
    return "\n".join(flowlib.section(text, heading) or "" for text in texts if text)


def run(root, folder):
    validation = flowlib.read_worktree(root, folder + "/validation.md")
    body = flowlib.section(validation, "Leftovers")
    if body is None:
        return ["validation.md has no '## Leftovers' section (write '- None.' when nothing is left)"]
    items = flowlib.bullets(body)
    if not items:
        return ["the Leftovers section is empty (write '- None.' when nothing is left)"]
    name = folder.rsplit("/", 1)[-1]
    problems = []
    for item in items:
        if re.match(r"^- none\.?$", item, re.IGNORECASE):
            continue
        intent = INTENT_POINTER.search(item)
        roadmap = ROADMAP_POINTER.search(item)
        if intent:
            path = intent.group(1)
            if flowlib.read_worktree(root, path) is None and not flowlib.on_main(root, path):
                problems.append("leftover points to %s, which does not exist" % path)
        elif roadmap:
            identifier = ID.match(item)
            if not identifier:
                problems.append("leftover needs an ID (L1, L2, ...) to be found in the roadmap: %s" % item)
                continue
            tag = "(%s %s)" % (name, identifier.group(1))
            if tag not in roadmap_sections(root, roadmap.group(1)):
                problems.append("no line containing '%s' in the roadmap's '%s' section" % (tag, roadmap.group(1)))
        else:
            problems.append("leftover has no pointer (new intent, roadmap: to do, roadmap: known limits): %s" % item)
    return problems


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    problems = run(root, folder)
    for sentence in problems:
        print("FAIL leftovers: " + sentence)
    if not problems:
        print("PASS leftovers: every leftover points to a new intent or to the roadmap")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
