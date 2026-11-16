#!/usr/bin/env python3
"""R-ID coverage: every requirement of spec.md is checked by somebody.

Committing validation.md into `main` approves the whole file, while the owner
reads §0 (and §3) only. This check answers "is any requirement checked by
nobody" with a script: each R-ID defined in spec.md's Requirements section
has to appear in validation.md §0, §1 or §2.

Usage: check_rid_coverage.py [<change folder>]   (default: the current branch's folder)
"""

import re
import sys

import flowlib

DEFINED = re.compile(r"^\s*[-*]\s*\*{0,2}(R\d+)\b", re.MULTILINE)


def run(root, folder):
    """List of problems, empty when every R-ID is covered."""
    spec = flowlib.read_worktree(root, folder + "/spec.md")
    validation = flowlib.read_worktree(root, folder + "/validation.md")
    if spec is None or validation is None:
        return ["%s needs both spec.md and validation.md" % folder]
    defined = []
    for rid in DEFINED.findall(flowlib.section(spec, "Requirements") or ""):
        if rid not in defined:
            defined.append(rid)
    if not defined:
        return ["spec.md defines no R-ID in its Requirements section"]
    checked_text = "\n".join(flowlib.section(validation, part) or "" for part in ("§0", "§1", "§2"))
    return [
        "%s is not cited in validation.md §0, §1 or §2" % rid
        for rid in defined
        if not re.search(r"\b%s\b" % rid, checked_text)
    ]


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    problems = run(root, folder)
    for sentence in problems:
        print("FAIL R-ID coverage: " + sentence)
    if not problems:
        print("PASS R-ID coverage: every R-ID of spec.md is cited in validation.md §0, §1 or §2")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
