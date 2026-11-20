#!/usr/bin/env python3
"""Add findings to the roadmap's "To do" section, committed straight to `main`.

The way into the development flow: a finding is recorded at once, as one
line, although the agent cannot otherwise move `main`. The script can only
append lines to that one section. Several findings (a change's leftovers at
its close) go in one call: one commit, one push.

Usage: todo_add.py --who <name> "<one sentence>" ["<one sentence>" ...]
Line written:  - <date> · <who> · <sentence>
A leftover of a change adds its tag at the end of the sentence: "... (<folder name> L2)"
"""

import sys

import flowlib


def parse(arguments):
    """(who, [sentences]) or None when the arguments are not of the usage's form."""
    if len(arguments) < 3 or arguments[0] != "--who" or not arguments[1].strip():
        return None
    sentences = [" ".join(sentence.split()) for sentence in arguments[2:]]
    if not all(sentences):
        return None
    return arguments[1].strip(), sentences


def commit_message(sentences):
    more = " (+%d more)" % (len(sentences) - 1) if len(sentences) > 1 else ""
    return "to do: " + sentences[0][:60] + more


def main():
    parsed = parse(sys.argv[1:])
    if not parsed:
        print(__doc__.strip())
        return 2
    who, sentences = parsed
    root = flowlib.repo_root()
    if not root or not flowlib.is_setup(root):
        print("REFUSED: the project is not set up (no %s on `main`)" % flowlib.ROADMAP)
        return 1
    lines = ["- %s · %s · %s" % (flowlib.today(), who, sentence) for sentence in sentences]

    def append(body):
        while body and not body[-1].strip():
            body.pop()
        return body + lines + [""]

    try:
        text = flowlib.edit_section(flowlib.roadmap_on_main(root), "To do", append)
        commit = flowlib.commit_to_main(root, {flowlib.ROADMAP: text}, commit_message(sentences))
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    count = "1 line" if len(lines) == 1 else "%d lines" % len(lines)
    print("added %s to the roadmap's To do on `main` (%s):\n%s" % (count, commit[:7], "\n".join(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
