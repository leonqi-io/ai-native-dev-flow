#!/usr/bin/env python3
"""Add one finding to the roadmap's "To do" section, committed straight to `main`.

The way into the development flow: a finding is recorded at once, as one
line, although the agent cannot otherwise move `main`. The script can only
append a line to that one section.

Usage: todo_add.py --who <name> "<one sentence>"
Line written:  - <date> · <who> · <sentence>
A leftover of a change adds its tag at the end of the sentence: "... (<folder name> L2)"
"""

import sys

import flowlib


def main():
    arguments = sys.argv[1:]
    if len(arguments) != 3 or arguments[0] != "--who" or not arguments[1].strip() or not arguments[2].strip():
        print(__doc__.strip())
        return 2
    who, sentence = arguments[1].strip(), " ".join(arguments[2].split())
    root = flowlib.repo_root()
    if not root or not flowlib.is_setup(root):
        print("REFUSED: the project is not set up (no %s on `main`)" % flowlib.ROADMAP)
        return 1
    line = "- %s · %s · %s" % (flowlib.today(), who, sentence)

    def append(body):
        while body and not body[-1].strip():
            body.pop()
        return body + [line, ""]

    try:
        text = flowlib.edit_section(flowlib.roadmap_on_main(root), "To do", append)
        commit = flowlib.commit_to_main(root, {flowlib.ROADMAP: text}, "to do: " + sentence[:60])
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    print("added to the roadmap's To do on `main` (%s):\n%s" % (commit[:7], line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
