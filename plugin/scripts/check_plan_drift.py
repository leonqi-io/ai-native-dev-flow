#!/usr/bin/env python3
"""Plan drift: did the change touch a product file the plan does not list?

plan.md's "Files that change" section lists paths (or globs) in backticks,
in its list items — on the item's own line or on the indented lines that
continue it. Square brackets in a path are literal (`pages/[slug].astro`).
A departure from the plan is fine when plan.md is updated in the same commit;
this check refuses a product file that changed on the branch and is nowhere
in that list. A listed file that did not change is only reported.

Usage: check_plan_drift.py [<change folder>]
"""

import re
import sys

import flowlib

BACKTICKED = re.compile(r"`([^`]+)`")


def listed_paths(section_text):
    """Backticked entries of the section's list items, continuation lines included."""
    listed, inside_item = [], False
    for line in (section_text or "").splitlines():
        if line.startswith("- "):
            inside_item = True
        elif not (inside_item and line[:1].isspace() and line.strip()):
            inside_item = False
            continue
        listed.extend(BACKTICKED.findall(line))
    return listed


def run(root, folder, config=None):
    """(problems, notes)"""
    config = config or flowlib.load_config(root)
    plan = flowlib.read_worktree(root, folder + "/plan.md")
    listed_text = flowlib.section(plan, "Files that change")
    if listed_text is None:
        return ["plan.md has no '## Files that change' section"], []
    listed = listed_paths(listed_text)
    base = flowlib.merge_base(root)
    if not base:
        return ["cannot find where this branch left `main`"], []
    changed = flowlib.git_out(["diff", "--name-only", base], cwd=root).splitlines()
    changed += flowlib.git_out(["ls-files", "--others", "--exclude-standard"], cwd=root).splitlines()
    product = sorted(set(path for path in changed if not flowlib.is_non_product(path, config)))
    problems = [
        "%s changed but is not in plan.md's 'Files that change' (update the plan in the same commit)" % path
        for path in product
        if not flowlib.matches(path, listed)
    ]
    notes = ["listed in the plan but unchanged: %s" % entry for entry in listed if not any(flowlib.matches(path, [entry]) for path in product)]
    return problems, notes


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    try:
        problems, notes = run(root, folder)
    except flowlib.FlowError as error:
        print("FAIL plan drift: %s" % error)
        return 2
    for sentence in problems:
        print("FAIL plan drift: " + sentence)
    for sentence in notes:
        print("NOTE plan drift: " + sentence)
    if not problems:
        print("PASS plan drift: every changed product file is in the plan's list")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
