#!/usr/bin/env python3
"""Dispose of one line of the roadmap's "To do" section, on `main`.

    roadmap_edit.py delete --match "<text>" --reason fix-now|dismissed
    roadmap_edit.py delete --match "<text>" --reason fixed-directly --commit <hash>
    roadmap_edit.py move   --match "<text>"

delete   the line leaves the roadmap
           fix-now          its intent carries a "Source" line
           dismissed        Git history keeps it
           fixed-directly   what it named is not a product file and is already
                            fixed by <hash>, a commit of this branch or of `main`
move     the line leaves "To do" and its sentence joins "Planned stages"

<text> has to match exactly one To do line. Run by the agent, the hook turns
the call into a prompt showing the line; the owner approves with one click.
This script is the only way a To do line leaves: the Edit/Write hook and the
close check refuse a branch that removes or rewrites one itself.
"""

import sys

import flowlib

REASONS = ("fix-now", "dismissed", "fixed-directly")
USAGE = (
    'delete --match "<text>" --reason fix-now|dismissed, '
    'delete --match "<text>" --reason fixed-directly --commit <hash>, or move --match "<text>"'
)


def parse(arguments):
    """(action, text, reason, commit) or None when the arguments are not of the usage's form."""
    if len(arguments) < 3 or arguments[0] not in ("delete", "move") or arguments[1] != "--match":
        return None
    action, text, rest = arguments[0], arguments[2], arguments[3:]
    if action == "move":
        return None if rest else (action, text, None, None)
    if len(rest) < 2 or rest[0] != "--reason" or rest[1] not in REASONS:
        return None
    reason, rest = rest[1], rest[2:]
    if reason != "fixed-directly":
        return None if rest else (action, text, reason, None)
    if len(rest) != 2 or rest[0] != "--commit":
        return None
    return action, text, reason, rest[1]


def find_line(root, text):
    """The single To do line on `main` containing text; raises FlowError otherwise."""
    roadmap = flowlib.roadmap_on_main(root)
    if roadmap is None:
        raise flowlib.FlowError("no %s on `main`" % flowlib.ROADMAP)
    found = [line for line in flowlib.todo_lines(roadmap) if text in line]
    if len(found) != 1:
        raise flowlib.FlowError("'%s' matches %d To do line(s); it has to match exactly one" % (text, len(found)))
    return roadmap, found[0]


def fixing_commit(root, commit):
    """Short hash of the commit that fixed the line; raises FlowError when it is not a commit of this branch or `main`."""
    resolved = flowlib.git_out(["rev-parse", "-q", "--verify", commit + "^{commit}"], cwd=root)
    if not resolved:
        raise flowlib.FlowError("--commit %s is not a commit of this repository" % commit)
    if not (flowlib.is_ancestor(root, resolved, "HEAD") or flowlib.is_ancestor(root, resolved, flowlib.MAIN)):
        raise flowlib.FlowError("--commit %s is neither in this branch's history nor in `main`" % commit)
    return resolved[:7]


def commit_message(action, reason, fixed_by, sentence):
    if action == "move":
        return "to do → planned: " + sentence[:50]
    label = {"fix-now": "→ intent", "dismissed": "dismissed", "fixed-directly": "fixed directly (%s)" % fixed_by}[reason]
    return "to do %s: %s" % (label, sentence[:50])


def main():
    parsed = parse(sys.argv[1:])
    if not parsed:
        print(__doc__.strip())
        return 2
    action, text, reason, commit = parsed
    root = flowlib.repo_root()
    try:
        fixed_by = fixing_commit(root, commit) if commit else None
        roadmap, line = find_line(root, text)
        roadmap = flowlib.edit_section(roadmap, "To do", lambda body: [item for item in body if item.strip() != line])
        sentence = line.split(" · ", 2)[-1]
        if action == "move":

            def append(body):
                while body and not body[-1].strip():
                    body.pop()
                return body + ["- " + sentence, ""]

            roadmap = flowlib.edit_section(roadmap, "Planned stages", append)
        done = flowlib.commit_to_main(root, {flowlib.ROADMAP: roadmap}, commit_message(action, reason, fixed_by, sentence))
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    how = "moved to Planned stages" if action == "move" else "deleted (%s)" % (reason + (", " + fixed_by if fixed_by else ""))
    print("%s on `main` (%s):\n%s" % (how, done[:7], line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
