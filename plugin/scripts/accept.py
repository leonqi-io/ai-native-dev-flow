#!/usr/bin/env python3
"""Accept: put an approval on `main` — the approval record of the flow.

    accept.py setup    project setup. On the branch `setup`: the whole branch
                       lands on `main`. On any other branch (a later
                       amendment): the project files only.
    accept.py intent   specs/<branch>/intent.md                    "intent accepted"
    accept.py spec     specs/<branch>/spec.md + validation.md      "spec accepted"
    accept.py plan     specs/<branch>/plan.md                      "plan approved"

    accept.py <what> --check    run every refusal check and show what would
                                land on `main`; change nothing

Who runs it:
  the owner — by typing the approval sentence alone in the chat (the
  UserPromptSubmit hook then runs this script), or in his own terminal;
  small change, `intent` only — the agent; the hook turns that call into a
  prompt the owner approves with one click.
  `--check` changes nothing and may be run by anyone.

It refuses unless the files are committed on the working branch, have the
shape of their template, and (for `spec`) every R-ID is covered. It then
commits exactly those files onto `main` and merges `main` back into the
working branch, so the branch contains its own approval commits.

Project setup on the branch `setup` is different on purpose: everything
written at setup belongs to it (an inventory, a note the CLAUDE.md points
to), so `main` moves to the head of `setup` — the same mechanism as a merge —
and every file that lands is listed, the ones that are not project files
under their own heading. The checkout then switches to `main` and `setup` is
deleted.
"""

import os
import sys

import check_rid_coverage
import check_shape
import flowlib

SETUP_BRANCH = "setup"
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


def landing_files(root):
    """(status letter, path) for every file the `setup` branch would put on `main`."""
    if not flowlib.main_exists(root):
        return [("A", path) for path in flowlib.git_out(["ls-tree", "-r", "--name-only", "HEAD"], cwd=root).splitlines()]
    listing = flowlib.git_out(["diff", "--name-status", "--no-renames", "%s...HEAD" % flowlib.MAIN], cwd=root)
    return [tuple(line.split("\t", 1)) for line in listing.splitlines() if "\t" in line]


def print_landing(root, landing):
    """The list the owner approves: project files first, everything else under its own heading."""
    project = flowlib.SETUP_FILES + SETUP_EXTRAS
    head = flowlib.git_out(["rev-parse", "--short", "HEAD"], cwd=root)
    print("project setup — `main` moves to the head of `%s` (%s). Files that land on `main`:" % (SETUP_BRANCH, head))
    for status, path in landing:
        if path in project:
            print("  %s  %s" % (status, path))
    others = [(status, path) for status, path in landing if path not in project]
    if others:
        print("also carried (not project files — the owner looks at these):")
        for status, path in others:
            print("  %s  %s" % (status, path))
    untracked = flowlib.git_out(["ls-files", "--others", "--exclude-standard"], cwd=root)
    if untracked:
        print("NOTE: not committed on `%s`, so not carried:" % SETUP_BRANCH)
        for path in untracked.splitlines():
            print("  " + path)


def accept_setup_branch(root, check_only):
    """Project setup on the branch `setup`: the whole branch lands on `main`."""
    missing = [path for path in flowlib.SETUP_FILES if flowlib.read_worktree(root, path) is None]
    if missing:
        return fail("missing: " + ", ".join(missing))
    # Uncommitted: any change to a tracked file, and any project file not committed yet.
    dirty = flowlib.git_out(["status", "--porcelain", "--untracked-files=no"], cwd=root).splitlines()
    dirty += [line for line in flowlib.git_out(["status", "--porcelain", "--"] + files_for(root, "setup", None), cwd=root).splitlines() if line not in dirty]
    if dirty:
        return fail("commit these on `%s` first:\n%s" % (SETUP_BRANCH, "\n".join(dirty)))
    problems = shape_problems(root, "setup", flowlib.SETUP_FILES, None)
    if problems:
        return fail("\n  ".join(["the files are not ready:"] + problems))
    if check_only:
        print_landing(root, landing_files(root))
        if flowlib.has_origin(root):
            print("`main` is then pushed to origin.")
        print("accept setup --check: nothing refuses; nothing was changed")
        return 0
    try:
        if not flowlib.main_exists(root):
            # A new repository: `main` starts at the setup branch's commit.
            print_landing(root, landing_files(root))
            flowlib.git_must(["branch", flowlib.MAIN, "HEAD"], cwd=root)
            print("project setup accepted: `main` created at %s" % flowlib.git_out(["rev-parse", "--short", "HEAD"], cwd=root))
        else:
            note = flowlib.sync_main(root)
            if note:
                print(note)
            if not flowlib.is_ancestor(root, flowlib.MAIN, "HEAD"):
                merged = flowlib.git(["merge", "--no-edit", "-q", flowlib.MAIN], cwd=root)
                if merged.returncode != 0:
                    flowlib.git(["merge", "--abort"], cwd=root)
                    return fail("`main` does not merge cleanly into `%s`; resolve it on the branch, then accept again" % SETUP_BRANCH)
                print("merged `main` into `%s` first" % SETUP_BRANCH)
            print_landing(root, landing_files(root))
            flowlib.move_main(root, flowlib.git_must(["rev-parse", "HEAD"], cwd=root))
            print("project setup accepted: `main` is at %s" % flowlib.git_out(["rev-parse", "--short", flowlib.MAIN], cwd=root))
    except flowlib.FlowError as error:
        return fail(str(error))
    pushed, note = flowlib.push_main(root)
    if note:
        print(note)
    if not pushed:
        return 1
    for line in flowlib.leave_branch(root, SETUP_BRANCH):
        print(line)
    return 0


def main():
    arguments = sys.argv[1:]
    check_only = arguments[1:] == ["--check"]
    what = arguments[0] if arguments and (len(arguments) == 1 or check_only) else None
    if what not in ("setup", "intent", "spec", "plan"):
        print(__doc__.strip())
        return 2
    root = flowlib.repo_root()
    if not root:
        return fail("not a Git repository")
    branch = flowlib.current_branch(root)
    if not branch or branch == flowlib.MAIN:
        return fail("run this on the working branch (for setup: a branch named `%s`), not on `main`" % SETUP_BRANCH)
    if what == "setup" and branch == SETUP_BRANCH:
        return accept_setup_branch(root, check_only)
    if what == "setup" and not flowlib.main_exists(root):
        return fail("there is no `main` yet: do the project setup on a branch named `%s`" % SETUP_BRANCH)
    folder = flowlib.change_folder(root)
    tier = None
    if what != "setup":
        if not flowlib.is_setup(root):
            return fail("the project is not set up: mission.md, decisions.md and roadmap.md are not all on `main`")
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
    label = "project setup (amended)" if what == "setup" else "%s: %s" % (MESSAGES[what], folder.rsplit("/", 1)[-1])
    if check_only:
        print("%s — these would be committed on `main`:" % label)
        for path in files:
            print("  " + path)
        print("accept %s --check: nothing refuses; nothing was changed" % what)
        return 0

    try:
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
