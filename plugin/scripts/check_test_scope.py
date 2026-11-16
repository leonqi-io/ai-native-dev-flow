#!/usr/bin/env python3
"""Test-scope diff: was a test file changed after the red run without a release?

The Edit / Write hook only stops those two tools; a formatter or a shell
command reaches test files another way. This check finds a changed test file
whatever changed it: it diffs the test scope between the start of the lock
and the current state, and every file that differs needs a `test-release:`
entry in the Approval log.

Start of the lock: the commit that added red-run.txt (normal, high-risk);
the point where the branch left `main` (small change).

Usage: check_test_scope.py [<change folder>]
"""

import sys

import flowlib


def run(root, folder, config=None):
    config = config or flowlib.load_config(root)
    tier = flowlib.tier_of(root, folder)
    if tier == "small":
        base = flowlib.merge_base(root)
        if not base:
            return ["cannot find where this branch left `main`"]
    else:
        base = flowlib.red_commit(root, folder)
        if not base:
            return ["%s/red-run.txt is not committed: the red run comes before the implementation" % folder]
    # Working tree against the base, so an uncommitted change is seen too.
    changed = flowlib.git_out(["diff", "--name-only", base], cwd=root).splitlines()
    untracked = flowlib.git_out(["ls-files", "--others", "--exclude-standard"], cwd=root).splitlines()
    in_scope = [path for path in changed + untracked if flowlib.matches(path, config["test_scope"])]
    log = flowlib.approval_log(root, folder)
    return [
        "%s changed after the lock started and has no 'test-release: %s' entry in the Approval log" % (path, path)
        for path in sorted(set(in_scope))
        if ("test-release: " + path) not in log
    ]


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    try:
        problems = run(root, folder)
    except flowlib.FlowError as error:
        print("FAIL test scope: %s" % error)
        return 2
    for sentence in problems:
        print("FAIL test scope: " + sentence)
    if not problems:
        print("PASS test scope: no unreleased change to a test file since the lock started")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
