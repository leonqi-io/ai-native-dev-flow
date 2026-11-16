#!/usr/bin/env python3
"""Close check: everything that must hold before a change is merged.

Runs, for the current branch's change folder:
  shape        every artifact of the tier has its sections
  R-ID         every R-ID of spec.md is cited in validation.md §0 / §1 / §2   (normal, high-risk)
  test scope   no unreleased change to a test file since the lock started
  plan drift   no changed product file missing from plan.md                    (normal, high-risk)
  leftovers    every leftover points to a new intent or to the roadmap
  review       the Approval log's latest review entry has no open Important finding

The review entry is a line of the Approval log of this form:
  - <date time> · review (fresh session) · Important open: 0 · Nit: 2
  - <date time> · review (verifier) · Important open: 0          (small change)

Usage: close_check.py [<change folder>]        exit 0 = may merge, 1 = refused
"""

import re
import sys

import check_leftovers
import check_plan_drift
import check_rid_coverage
import check_shape
import check_test_scope
import flowlib

REVIEW_LINE = re.compile(r"review \((fresh session|verifier)\).*Important open:\s*(\d+)", re.IGNORECASE)


def review_problems(root, folder, tier):
    entries = [REVIEW_LINE.search(line) for line in flowlib.bullets(flowlib.approval_log(root, folder))]
    entries = [entry for entry in entries if entry]
    if not entries:
        return ["the Approval log has no review entry"]
    kind, important_open = entries[-1].group(1).lower(), int(entries[-1].group(2))
    problems = []
    if tier != "small" and kind != "fresh session":
        problems.append("the %s tier needs a review from a fresh session; the latest entry is '%s'" % (tier, kind))
    if important_open:
        problems.append("%d Important finding(s) still open in the latest review entry" % important_open)
    return problems


def run(root, folder, config=None):
    """List of (check name, problems). A check with an empty list passed."""
    config = config or flowlib.load_config(root)
    tier = flowlib.tier_of(root, folder)
    if tier is None:
        return [("tier", ["%s/intent.md carries no 'Tier:' line" % folder])]
    results = []
    names = ["intent", "validation"] if tier == "small" else ["intent", "spec", "validation", "plan"]
    shape = []
    for name in names:
        path = "%s/%s.md" % (folder, name)
        kind = check_shape.kind_of(path, tier)
        shape += ["%s: %s" % (path, sentence) for sentence in check_shape.problems_in(kind, flowlib.read_worktree(root, path), tier)]
    results.append(("shape", shape))
    if tier != "small":
        results.append(("R-ID", check_rid_coverage.run(root, folder)))
    results.append(("test scope", check_test_scope.run(root, folder, config)))
    if tier != "small":
        results.append(("plan drift", check_plan_drift.run(root, folder, config)[0]))
    results.append(("leftovers", check_leftovers.run(root, folder)))
    results.append(("review", review_problems(root, folder, tier)))
    return results


def report(results):
    failed = False
    for name, problems in results:
        if problems:
            failed = True
            for sentence in problems:
                print("FAIL %s: %s" % (name, sentence))
        else:
            print("PASS %s" % name)
    return failed


def main():
    root = flowlib.repo_root()
    folder = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else flowlib.change_folder(root)
    if not root or not folder:
        print("FAIL no change folder: run this on a working branch or name the folder")
        return 2
    try:
        failed = report(run(root, folder))
    except flowlib.FlowError as error:
        print("FAIL close check: %s" % error)
        return 2
    print("close check: %s" % ("REFUSED — fix the lines above" if failed else "all checks passed"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
