#!/usr/bin/env python3
"""Test-scope diff: was an existing test file changed after the lock started without a release?

A change to a locked test file asks nobody while it is made (ruled
2026-11-19): the session records a `test-release:` line (record.py), the
reviewer checks the change did not weaken the test, and this check — run by
the close check — refuses a changed test file that has no such line. It diffs
the test scope between the start of the lock and the current state, so it
sees a change whatever made it (an edit, a formatter, a shell command).

A release covers the content it was recorded for (ruled 2026-11-20): the line
carries the file's sha256, and a file that changed again after its latest
line counts as unreleased — the reviewer has not seen that version.

A test file that did not exist when the lock started needs no release: a new
test cannot weaken an old one. New files are listed for the end screen.

Start of the lock: the commit that added red-run.txt (normal, high-risk);
the point where the branch left `main` (small change).

Usage: check_test_scope.py [<change folder>]
"""

import sys

import flowlib
import record


def lock_start(root, folder):
    """(commit where the lock started, None) or (None, why there is none)."""
    if flowlib.tier_of(root, folder) == "small":
        base = flowlib.merge_base(root)
        return (base, None) if base else (None, "cannot find where this branch left `main`")
    base = flowlib.red_commit(root, folder)
    return (base, None) if base else (None, "%s/red-run.txt is not committed: the red run comes before the implementation" % folder)


def scan(root, folder, config):
    """{"changed": existing test files that differ, "new": test files added,
    "released": changed ones whose latest release line covers their content now,
    "stale": changed ones released for an earlier content}.

    Raises FlowError when the lock has not started.
    """
    base, why_not = lock_start(root, folder)
    if not base:
        raise flowlib.FlowError(why_not)
    scope = config["test_scope"]
    # Working tree against the base, so an uncommitted change is seen too; renames as delete + add.
    listing = flowlib.git_out(["diff", "--name-status", "--no-renames", base], cwd=root).splitlines()
    untracked = flowlib.git_out(["ls-files", "--others", "--exclude-standard"], cwd=root).splitlines()
    added = [line.split("\t", 1)[1] for line in listing if line.startswith("A\t")] + untracked
    touched = [line.split("\t", 1)[1] for line in listing if "\t" in line and not line.startswith("A\t")]
    log = flowlib.approval_log(root, folder)
    changed = sorted(set(path for path in touched if flowlib.matches(path, scope)))
    recorded = dict((path, record.release_digest(log, path)) for path in changed)
    return {
        "changed": changed,
        "new": sorted(set(path for path in added if flowlib.matches(path, scope))),
        "released": [path for path in changed if recorded[path] == record.content_digest(root, path)],
        "stale": [path for path in changed if recorded[path] is not None
                  and recorded[path] != record.content_digest(root, path)],
    }


def unreleased(found):
    problems = []
    for path in found["changed"]:
        if path in found["stale"]:
            problems.append("%s changed again after its latest test-release line: the release covers an earlier version "
                            "(record.py test-release, once the reviewer has seen this one)" % path)
        elif path not in found["released"]:
            problems.append("%s changed after the lock started and has no 'test-release: %s' entry in the Approval log "
                            "(record.py test-release)" % (path, path))
    return problems


def run(root, folder, config=None):
    """List of problems, empty when every changed existing test file has a release line."""
    try:
        return unreleased(scan(root, folder, config or flowlib.load_config(root)))
    except flowlib.FlowError as error:
        return [str(error)]


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    try:
        found = scan(root, folder, flowlib.load_config(root))
    except flowlib.FlowError as error:
        print("FAIL test scope: %s" % error)
        return 1
    problems = unreleased(found)
    for sentence in problems:
        print("FAIL test scope: " + sentence)
    for path in found["released"]:
        print("NOTE test scope: released: %s" % path)
    for path in found["new"]:
        print("NOTE test scope: new: %s" % path)
    if not problems:
        print("PASS test scope: no unreleased change to an existing test file since the lock started")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
