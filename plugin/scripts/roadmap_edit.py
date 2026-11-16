#!/usr/bin/env python3
"""Dispose of one line of the roadmap's "To do" section, on `main`.

    roadmap_edit.py delete --match "<text>" --reason fix-now|dismissed
    roadmap_edit.py move   --match "<text>"

delete   the line leaves the roadmap (fix now: its intent carries a "Source"
         line; dismissed: Git history keeps it)
move     the line leaves "To do" and its sentence joins "Planned stages"

<text> has to match exactly one To do line. Run by the agent, the hook turns
the call into a prompt showing the line; the owner approves with one click.
"""

import sys

import flowlib


def parse(arguments):
    if len(arguments) < 3 or arguments[0] not in ("delete", "move") or arguments[1] != "--match":
        return None
    action, text, rest = arguments[0], arguments[2], arguments[3:]
    reason = None
    if action == "delete":
        if len(rest) != 2 or rest[0] != "--reason" or rest[1] not in ("fix-now", "dismissed"):
            return None
        reason = rest[1]
    elif rest:
        return None
    return action, text, reason


def find_line(root, text):
    """The single To do line on `main` containing text; raises FlowError otherwise."""
    roadmap = flowlib.roadmap_on_main(root)
    if roadmap is None:
        raise flowlib.FlowError("no %s on `main`" % flowlib.ROADMAP)
    found = [line for line in flowlib.todo_lines(roadmap) if text in line]
    if len(found) != 1:
        raise flowlib.FlowError("'%s' matches %d To do line(s); it has to match exactly one" % (text, len(found)))
    return roadmap, found[0]


def main():
    parsed = parse(sys.argv[1:])
    if not parsed:
        print(__doc__.strip())
        return 2
    action, text, reason = parsed
    root = flowlib.repo_root()
    try:
        roadmap, line = find_line(root, text)
        roadmap = flowlib.edit_section(roadmap, "To do", lambda body: [item for item in body if item.strip() != line])
        if action == "move":
            sentence = line.split(" · ", 2)[-1]

            def append(body):
                while body and not body[-1].strip():
                    body.pop()
                return body + ["- " + sentence, ""]

            roadmap = flowlib.edit_section(roadmap, "Planned stages", append)
            message = "to do → planned: " + sentence[:50]
        else:
            message = "to do %s: %s" % ("→ intent" if reason == "fix-now" else "dismissed", line.split(" · ", 2)[-1][:50])
        commit = flowlib.commit_to_main(root, {flowlib.ROADMAP: roadmap}, message)
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    print("%s on `main` (%s):\n%s" % ("moved to Planned stages" if action == "move" else "deleted (%s)" % reason, commit[:7], line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
