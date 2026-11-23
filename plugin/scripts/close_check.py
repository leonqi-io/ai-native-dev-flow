#!/usr/bin/env python3
"""Close check: everything that must hold before a change is merged.

Runs, for the current branch's change folder:
  shape        every artifact of the tier has its sections; a change with a
               mock names who confirmed it, and each output a person reads
               has a sample its reader confirmed                              (normal, high-risk)
  R-ID         every R-ID of spec.md is cited in validation.md §0 / §1 / §2   (normal, high-risk)
  test scope   no unreleased change to an existing test file since the lock started
  plan drift   no changed product file missing from plan.md                    (normal, high-risk)
  leftovers    every leftover points to a new intent or to the roadmap
  to do        the branch itself did not remove, rewrite or add a line of the
               roadmap's To do section (whatever made the change)
  handoff      no handoff.md of a paused session is left in the change folder
  review       the Approval log's latest review line has no open Important finding,
               its report is on disk, and no product file changed after the
               commit it records
  validation   the latest validation line answers every judgment of §0, none
               failed, and each one not judged has a Leftovers line   (normal, high-risk)

The review and validation lines are written by record.py, which also reads
them; the forms are in its docstring. A normal or high-risk change needs its
latest review from the reviewer subagent (or a fresh session); a small
change's review is the verifier's.

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
import record


def review_problems(root, folder, tier, config):
    review = record.latest_review(flowlib.approval_log(root, folder))
    if review is None:
        return ["the Approval log has no review entry (record.py review)"]
    problems = []
    if tier != "small" and review["kind"] == "verifier":
        problems.append("the %s tier needs the reviewer subagent's review (or a fresh session's); the latest entry is the verifier's" % tier)
    if review["important"]:
        problems.append("%d Important finding(s) still open in the latest review entry" % review["important"])
    if review["report"] and flowlib.read_worktree(root, review["report"]) is None:
        problems.append("the latest review entry points to %s, which is not on disk" % review["report"])
    return problems + changed_since_review(root, review["at"], config)


def changed_since_review(root, reviewed_at, config):
    """Product files that differ from the commit the latest review line records (committed or not)."""
    if not reviewed_at:
        return ["the latest review entry records no commit ('at <hash>'): record it with record.py review"]
    if not flowlib.is_ancestor(root, reviewed_at, "HEAD"):
        return ["the commit the latest review entry records (%s) is not in this branch's history: review again" % reviewed_at]
    listing = flowlib.git_out(["diff", "--name-only", reviewed_at], cwd=root).splitlines()
    changed = [path for path in listing if not flowlib.is_non_product(path, config)]
    if not changed:
        return []
    return ["product files changed after the latest review (at %s): %s — run the review loop again"
            % (reviewed_at, ", ".join(changed[:5]) + (" …" if len(changed) > 5 else ""))]


def todo_problems(root):
    """The roadmap's To do lines move on `main` only; a branch that changed them itself is refused."""
    base = flowlib.merge_base(root)
    before = flowlib.read_at(root, base, flowlib.ROADMAP) if base else None
    after = flowlib.read_worktree(root, flowlib.ROADMAP)
    if before is None or after is None:
        return []
    removed, added = flowlib.todo_difference(before, after)
    problems = ["this branch removed or rewrote a To do line: %s" % line for line in removed]
    problems += ["this branch added a To do line: %s" % line for line in added]
    if problems:
        problems.append("put the section back as it is on `main` (git merge main brings its lines) — " + flowlib.todo_route())
    return problems


def handoff_problems(root, folder):
    """A paused session's note belongs to the stage it was written in; none of them is the merge."""
    note = flowlib.handoff_note(root, folder)
    if not note:
        return []
    return ["%s is still there: the stage it was written in is over — delete it in a commit that says so" % note]


def validation_problems(root, folder):
    answers = record.latest_validation(flowlib.approval_log(root, folder))
    if answers is None:
        return ["the Approval log has no validation entry (the end screen's answers: record.py validation)"]
    validation = flowlib.read_worktree(root, folder + "/validation.md")
    leftovers = "\n".join(flowlib.bullets(flowlib.section(validation, "Leftovers")))
    problems = ["%s of §0 has no answer in the latest validation entry" % question
                for question in record.questions_asked(validation) if question not in answers]
    for question, answer in sorted(answers.items()):
        if answer == "fail":
            problems.append("%s failed in the latest validation entry: fix it, then ask it again" % question)
        elif answer == "not judged" and not re.search(r"\b%s\b" % question, leftovers):
            problems.append("%s was not judged and no Leftovers line names it" % question)
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
    if tier != "small":
        shape += flowlib.mock_review_problems(root, folder)
        shape += flowlib.output_sample_problems(root, folder)
    results.append(("shape", shape))
    if tier != "small":
        results.append(("R-ID", check_rid_coverage.run(root, folder)))
    results.append(("test scope", check_test_scope.run(root, folder, config)))
    if tier != "small":
        results.append(("plan drift", check_plan_drift.run(root, folder, config)[0]))
    results.append(("leftovers", check_leftovers.run(root, folder)))
    results.append(("to do", todo_problems(root)))
    results.append(("handoff", handoff_problems(root, folder)))
    results.append(("review", review_problems(root, folder, tier, config)))
    if tier != "small":
        results.append(("validation", validation_problems(root, folder)))
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
