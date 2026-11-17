#!/usr/bin/env python3
"""Bring local `main` and origin/main together — by fast-forward and push, nothing else.

When to run it: before a branch is started from `main`, and after a pull
request was merged on GitHub outside the flow's own merge (a routine content
PR, a PR merged on the page). Anyone may run it, the agent included: it
approves nothing. origin/main only moves by the owner's merge — the agent can
neither push to it nor merge a pull request — and local `main` only by the
flow's scripts, so making the two equal carries no new decision.

  origin/main is ahead   local `main` is fast-forwarded to it
  local `main` is ahead  it is pushed (an earlier push that did not get through)
  the two have diverged  refused; the sentence says what the owner does by hand

Usage: sync_main.py
"""

import sys

import flowlib


def main():
    if sys.argv[1:]:
        print(__doc__.strip())
        return 2
    root = flowlib.repo_root()
    if not root:
        print("REFUSED: not a Git repository")
        return 1
    if not flowlib.has_origin(root) or not flowlib.main_exists(root):
        print("nothing to sync: this repository has no `origin` remote, or no `main` yet")
        return 0
    try:
        note = flowlib.sync_main(root)
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    if note:
        print(note)
        if note.startswith("NOTE:"):
            return 1
    local = flowlib.git_out(["rev-parse", flowlib.MAIN], cwd=root)
    if flowlib.origin_main(root) != local:
        pushed, note = flowlib.push_main(root)
        if note:
            print(note)
        if not pushed:
            return 1
    print("`main` and origin/main are both at %s" % local[:7])
    return 0


if __name__ == "__main__":
    sys.exit(main())
