#!/usr/bin/env python3
"""Accept: put an approval file on `main` — the approval record of the flow.

    accept.py setup    mission.md, tech-stack.md, roadmap.md (+ CLAUDE.md, REVIEW.md, .claude/ files when present)
    accept.py intent   specs/<branch>/intent.md                    "intent accepted"
    accept.py spec     specs/<branch>/spec.md + validation.md      "spec accepted"
    accept.py plan     specs/<branch>/plan.md                      "plan approved"

Who runs it:
  normal and high-risk tiers — the owner, in his own terminal (it is his commit);
  small change, `intent` only — the agent; the hook turns that call into a
  prompt the owner approves with one click.

It refuses unless the files are committed on the working branch, have the
shape of their template, and (for `spec`) every R-ID is covered. It then
commits exactly those files onto `main` and merges `main` back into the
working branch, so the branch contains its own approval commits.
"""

import os
import sys

import check_rid_coverage
import check_shape
import flowlib

SETUP_EXTRAS = ["CLAUDE.md", "REVIEW.md", flowlib.CONFIG_PATH, ".claude/settings.json"]
MESSAGES = {"intent": "intent accepted", "spec": "spec accepted", "plan": "plan approved"}


def fail(sentence):
    print("REFUSED: " + sentence)
    return 1


def files_for(root, what, folder):
    if what == "setup":
        extras = [path for path in SETUP_EXTRAS if os.path.isfile(os.path.join(root, path))]
        return flowlib.SETUP_FILES + extras
    if what == "intent":
        return [folder + "/intent.md"]
    if what == "spec":
        return [folder + "/spec.md", folder + "/validation.md"]
    return [folder + "/plan.md"]


def shape_problems(root, what, files, tier):
    problems = []
    for path in files:
        kind = check_shape.kind_of(path, tier)
        if kind:
            problems += ["%s: %s" % (path, sentence) for sentence in check_shape.problems_in(kind, flowlib.read_worktree(root, path), tier)]
    return problems


def main():
    what = sys.argv[1] if len(sys.argv) == 2 else None
    if what not in ("setup", "intent", "spec", "plan"):
        print(__doc__.strip())
        return 2
    root = flowlib.repo_root()
    if not root:
        return fail("not a Git repository")
    branch = flowlib.current_branch(root)
    if not branch or branch == flowlib.MAIN:
        return fail("run this on the working branch (for setup: a branch named `setup`), not on `main`")
    folder = flowlib.change_folder(root)
    tier = None
    if what != "setup":
        if not flowlib.is_setup(root):
            return fail("the project is not set up: mission.md, tech-stack.md and roadmap.md are not all on `main`")
        tier = flowlib.tier_of(root, folder)
        if tier is None:
            return fail("%s/intent.md is missing or carries no 'Tier:' line" % folder)
        if what in ("spec", "plan") and tier == "small":
            return fail("a small change has no spec.md and no plan.md")
        if what == "spec" and not flowlib.on_main(root, folder + "/intent.md"):
            return fail("intent.md is not on `main` yet — 'intent accepted' comes first")
        if what == "plan" and not (flowlib.on_main(root, folder + "/spec.md") and flowlib.on_main(root, folder + "/validation.md")):
            return fail("spec.md and validation.md are not on `main` yet — 'spec accepted' comes first")
    files = files_for(root, what, folder)
    missing = [path for path in files if flowlib.read_worktree(root, path) is None]
    if missing:
        return fail("missing: " + ", ".join(missing))
    dirty = flowlib.git_out(["status", "--porcelain", "--"] + files, cwd=root)
    if dirty:
        return fail("commit these on the working branch first:\n" + dirty)
    problems = shape_problems(root, what, files, tier)
    if what == "spec":
        problems += check_rid_coverage.run(root, folder)
    if problems:
        return fail("\n  ".join(["the files are not ready:"] + problems))

    try:
        if what == "setup" and not flowlib.main_exists(root):
            # A new repository: `main` starts at the setup branch's commit.
            flowlib.git_must(["branch", flowlib.MAIN, "HEAD"], cwd=root)
            print("project setup accepted: `main` created at %s" % flowlib.git_out(["rev-parse", "--short", "HEAD"], cwd=root))
            return 0
        label = "project setup" if what == "setup" else "%s: %s" % (MESSAGES[what], folder.rsplit("/", 1)[-1])
        changes = {path: flowlib.read_worktree(root, path) for path in files}
        commit = flowlib.commit_to_main(root, changes, label)
    except flowlib.FlowError as error:
        return fail(str(error))
    if commit is None:
        print("nothing to do: `main` already has these files in this version")
        return 0
    print("%s — commit %s on `main`:" % (label, commit[:7]))
    for path in files:
        print("  " + path)
    merged = flowlib.git(["merge", "--no-edit", "-q", flowlib.MAIN], cwd=root)
    if merged.returncode != 0:
        print("NOTE: could not merge `main` back into %s automatically; run `git merge main` here.\n%s" % (branch, merged.stderr.strip()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
