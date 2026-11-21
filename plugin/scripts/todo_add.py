#!/usr/bin/env python3
"""Add findings to the roadmap's "To do" section, committed straight to `main`.

The way into the development flow: a finding is recorded at once, as one
line, although the agent cannot otherwise move `main`. The script can only
append lines to that one section. Several findings (a change's leftovers at
its close) go in one call: one commit, one push.

Usage: todo_add.py --who <name> "<one sentence>" ["<one sentence>" ...] [--who <other name> "<one sentence>" ...]
Each --who names who raised the sentences after it, up to the next --who.
Line written:  - <date> · <who> · <sentence>
A leftover of a change adds its tag at the end of the sentence: "... (<folder name> L2)"
"""

import sys

import flowlib


def parse(arguments):
    """[(who, sentence)] or None when the arguments are not of the usage's form."""
    if not arguments or arguments[0] != "--who":
        return None
    findings, who, expects_name = [], None, False
    for argument in arguments:
        if argument == "--who":
            if expects_name:
                return None
            expects_name = True
        elif expects_name:
            who, expects_name = argument.strip(), False
            if not who:
                return None
        else:
            sentence = " ".join(argument.split())
            if not sentence:
                return None
            findings.append((who, sentence))
    if expects_name or not findings:
        return None
    return findings


def commit_message(sentences):
    more = " (+%d more)" % (len(sentences) - 1) if len(sentences) > 1 else ""
    return "to do: " + sentences[0][:60] + more


def main():
    parsed = parse(sys.argv[1:])
    if not parsed:
        print(__doc__.strip())
        return 2
    sentences = [sentence for _, sentence in parsed]
    root = flowlib.repo_root()
    if not root or not flowlib.is_setup(root):
        print("REFUSED: the project is not set up (no %s on `main`)" % flowlib.ROADMAP)
        return 1
    lines = ["- %s · %s · %s" % (flowlib.today(), who, sentence) for who, sentence in parsed]

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
