#!/usr/bin/env python3
"""Merge: bring the working branch into `main` after the close check passes.

Who runs it:
  small change — the agent; the hook turns the call into a prompt that shows
  the intent, the changed files and (where the project deploys) the line
  "Merging publishes to production"; the owner approves with one click;
  normal and high-risk tiers on a project without PRs — the owner, in his own
  terminal. On a project that merges through PRs the owner merges on GitHub
  and this script is not used for those tiers.

It refuses when: the close check fails; the working tree has uncommitted
changes; a small change touches a path the project declares as high risk.
`main` only moves forward to the branch's head (after `main` has been merged
into the branch), so what was checked is exactly what lands. Where the
project deploys, `main` is pushed to `origin` — the push is what triggers the
deploy.

Usage: merge.py            merge
       merge.py --check    run every refusal check and stop
"""

import sys

import close_check
import flowlib


def fail(sentence):
    print("REFUSED: " + sentence)
    return 1


def changed_files(root):
    base = flowlib.merge_base(root)
    return flowlib.git_out(["diff", "--name-only", base, "HEAD"], cwd=root).splitlines() if base else []


def main():
    check_only = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check_only:
        print(__doc__.strip())
        return 2
    root = flowlib.repo_root()
    if not root:
        return fail("not a Git repository")
    try:
        config = flowlib.load_config(root)
    except flowlib.FlowError as error:
        return fail(str(error))
    if config is None:
        return fail("%s is missing: this repository does not use the flow" % flowlib.CONFIG_PATH)
    branch = flowlib.current_branch(root)
    folder = flowlib.change_folder(root)
    if not folder or not flowlib.folder_exists(root, folder):
        return fail("run this on the working branch of a change")
    tier = flowlib.tier_of(root, folder)
    if tier != "small" and config["pull_request"]:
        return fail("this project merges the %s tier through a PR: push the branch, open the PR, and merge it on GitHub" % tier)
    if flowlib.git_out(["status", "--porcelain"], cwd=root):
        return fail("the working tree has uncommitted changes; commit them on the branch first")
    if tier == "small":
        risky = [path for path in changed_files(root) if flowlib.matches(path, config["high_risk_paths"])]
        if risky:
            return fail("a small change may not touch a high-risk path (%s); write a high-risk intent instead" % ", ".join(risky))
    try:
        if close_check.report(close_check.run(root, folder, config)):
            return fail("the close check did not pass (lines above)")
    except flowlib.FlowError as error:
        return fail(str(error))
    if check_only:
        print("merge --check: nothing refuses the merge")
        return 0

    # `main` may have moved (a to-do line, another change): take it into the branch first.
    if flowlib.git(["merge-base", "--is-ancestor", flowlib.MAIN, "HEAD"], cwd=root).returncode != 0:
        merged = flowlib.git(["merge", "--no-edit", "-q", flowlib.MAIN], cwd=root)
        if merged.returncode != 0:
            flowlib.git(["merge", "--abort"], cwd=root)
            return fail("`main` does not merge cleanly into %s; resolve it on the branch, re-run the verify command, then merge again" % branch)
        print("merged `main` into %s first; re-run the verify command if `main` brought product changes" % branch)
    try:
        checkout = flowlib.main_worktree(root)
        if checkout:
            if flowlib.git_out(["status", "--porcelain", "--untracked-files=no"], cwd=checkout):
                return fail("`main` is checked out at %s with uncommitted changes" % checkout)
            flowlib.git_must(["merge", "--ff-only", "-q", branch], cwd=checkout)
        else:
            old = flowlib.git_must(["rev-parse", flowlib.MAIN], cwd=root)
            flowlib.git_must(["update-ref", "refs/heads/" + flowlib.MAIN, "HEAD", old], cwd=root)
    except flowlib.FlowError as error:
        return fail(str(error))
    head = flowlib.git_out(["rev-parse", "--short", flowlib.MAIN], cwd=root)
    print("merged %s into `main` (%s)" % (branch, head))
    if config["deploys"]:
        if flowlib.git_out(["remote", "get-url", "origin"], cwd=root):
            pushed = flowlib.git(["push", "origin", flowlib.MAIN], cwd=root)
            if pushed.returncode != 0:
                print("NOTE: `git push origin main` failed — nothing is published yet:\n" + pushed.stderr.strip())
                return 1
            print("pushed `main` to origin — the deploy pipeline publishes it")
        else:
            print("NOTE: this project deploys but has no `origin` remote; nothing was pushed")
    else:
        print("`main` was not pushed (this project does not deploy on merge)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
