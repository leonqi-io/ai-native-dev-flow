#!/usr/bin/env python3
"""Merge: bring the working branch into `main` after the close check passes.

Who runs it:
  the owner — by typing「确认合并」alone in the chat (the UserPromptSubmit hook
  then runs this script), or in his own terminal;
  small change — the agent; the hook turns the call into a prompt that shows
  the intent, the changed files and (where a merge publishes) the line
  "Merging publishes to production"; the owner approves with one click.

Two ways the merge happens, by project and tier:
  locally — every small change, and every tier of a project without pull
    requests: `main` only moves forward to the branch's head (after `main`
    has been merged into the branch), so what was checked is exactly what
    lands; `main` is pushed to origin where there is one.
  through the pull request — the normal and high-risk tiers of a project
    with `pull_request: true`: the branch's open PR is merged with
    `gh pr merge --merge`, then local `main` takes in origin/main. A PR the
    owner already merged on GitHub is recognised, and only the tidy-up runs.

It refuses when: the close check fails; the working tree has uncommitted
changes; a small change touches a path the project declares as high risk;
(PR) there is no open pull request, or it is not at this branch's head.

After the merge the checkout switches to `main` and the working branch is
deleted, here and on origin. A branch that is already in `main` (a merge
whose tidy-up did not finish, a PR merged on the page) is only tidied up.

Usage: merge.py            merge
       merge.py --check    run every refusal check and stop
"""

import json
import subprocess
import sys

import close_check
import flowlib

GH_TIMEOUT = 30  # seconds per `gh` call; same reasoning as flowlib.NETWORK_TIMEOUT


def fail(sentence):
    print("REFUSED: " + sentence)
    return 1


def changed_files(root):
    base = flowlib.merge_base(root)
    return flowlib.git_out(["diff", "--name-only", base, "HEAD"], cwd=root).splitlines() if base else []


def in_main(root, folder):
    """True when this change's branch is already contained in `main` (local, or origin's as last fetched)."""
    if not flowlib.on_main(root, folder + "/intent.md"):
        return False
    if flowlib.is_ancestor(root, "HEAD", flowlib.MAIN):
        return True
    remote = flowlib.origin_main(root)
    return bool(remote) and flowlib.is_ancestor(root, "HEAD", remote)


def tidy(root, branch, force=False):
    for line in flowlib.leave_branch(root, branch, force):
        print(line)
    return 0


def gh(arguments, root):
    """Run the GitHub CLI; None when it is not installed."""
    try:
        return subprocess.run(["gh"] + arguments, cwd=root, capture_output=True, text=True, timeout=GH_TIMEOUT)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(arguments, 124, "", "gh did not answer within %d seconds" % GH_TIMEOUT)


def pull_request(root, branch):
    """(the branch's pull request as a dict, None) or (None, a sentence saying why there is none)."""
    result = gh(["pr", "view", branch, "--json", "state,number,url,headRefOid"], root)
    if result is None:
        return None, "the GitHub CLI `gh` is not installed"
    if result.returncode != 0:
        reason = (result.stderr.strip().splitlines() or ["no reason given"])[-1]
        return None, "no pull request found for %s (%s)" % (branch, reason)
    try:
        return json.loads(result.stdout), None
    except ValueError:
        return None, "the answer of `gh pr view` could not be read"


def merge_through_pr(root, branch, config, check_only):
    """Normal and high-risk tiers of a project with pull requests. The close check has passed."""
    if not flowlib.has_origin(root):
        return fail("this project merges through pull requests but has no `origin` remote")
    request, why_not = pull_request(root, branch)
    if request is None:
        return fail(
            "%s. Push the branch and open the pull request first (the close skill does both); "
            "or merge it on GitHub and give the approval again — the script then only tidies up" % why_not
        )
    label = "pull request #%s" % request.get("number")
    state = str(request.get("state", "")).upper()
    if state == "MERGED":
        # Merged on GitHub by squash or rebase: Git does not see the branch in `main`, the PR says it is.
        if check_only:
            print("merge --check: %s is already merged; the merge would only tidy up" % label)
            return 0
        print("%s is already merged on GitHub — tidying up" % label)
        return tidy(root, branch, force=True)
    if state != "OPEN":
        return fail("%s is %s, not open" % (label, state.lower() or "in an unknown state"))
    head = flowlib.git_out(["rev-parse", "HEAD"], cwd=root)
    if request.get("headRefOid") != head:
        return fail("%s is not at this branch's head (%s): push the branch first — `git push origin %s`" % (label, head[:7], branch))
    if check_only:
        print("merge --check: nothing refuses the merge of %s" % label)
        return 0
    merged = gh(["pr", "merge", branch, "--merge"], root)
    if merged is None or merged.returncode != 0:
        return fail("`gh pr merge` did not succeed — nothing is merged:\n%s" % (merged.stderr.strip() if merged else "gh is not installed"))
    print("merged %s on GitHub (%s)" % (label, request.get("url", "")))
    if config["deploys"]:
        print("the merge publishes: the deploy pipeline runs now")
    try:
        note = flowlib.sync_main(root)
    except flowlib.FlowError as error:
        print("NOTE: %s" % error)
        return 1
    if note:
        print(note)
    if not flowlib.is_ancestor(root, "HEAD", flowlib.MAIN):
        print("NOTE: local `main` does not have the merge yet. Run sync_main.py, then give the approval again to tidy up.")
        return 1
    return tidy(root, branch)


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
    if flowlib.git_out(["status", "--porcelain"], cwd=root):
        return fail("the working tree has uncommitted changes; commit them on the branch first")
    try:
        if not check_only:
            note = flowlib.sync_main(root)
            if note:
                print(note)
        # A merge whose tidy-up did not finish, or a pull request merged on the page: nothing to check again.
        if in_main(root, folder):
            if check_only:
                print("merge --check: %s is already in `main`; the merge would only tidy up" % branch)
                return 0
            if not flowlib.is_ancestor(root, "HEAD", flowlib.MAIN):
                return fail("origin/main has this branch but local `main` could not take it in; run sync_main.py first")
            print("%s is already in `main` — tidying up" % branch)
            if flowlib.has_origin(root) and flowlib.origin_main(root) != flowlib.git_out(["rev-parse", flowlib.MAIN], cwd=root):
                pushed, note = flowlib.push_main(root)  # an earlier push that did not get through
                if note:
                    print(note)
                if not pushed:
                    return 1
            return tidy(root, branch)
        if tier == "small":
            risky = [path for path in changed_files(root) if flowlib.matches(path, config["high_risk_paths"])]
            if risky:
                return fail("a small change may not touch a high-risk path (%s); write a high-risk intent instead" % ", ".join(risky))
        if close_check.report(close_check.run(root, folder, config)):
            return fail("the close check did not pass (lines above)")
    except flowlib.FlowError as error:
        return fail(str(error))
    if tier != "small" and config["pull_request"]:
        return merge_through_pr(root, branch, config, check_only)
    if check_only:
        print("merge --check: nothing refuses the merge")
        return 0

    # `main` may have moved (a to-do line, another change): take it into the branch first.
    if not flowlib.is_ancestor(root, flowlib.MAIN, "HEAD"):
        merged = flowlib.git(["merge", "--no-edit", "-q", flowlib.MAIN], cwd=root)
        if merged.returncode != 0:
            flowlib.git(["merge", "--abort"], cwd=root)
            return fail("`main` does not merge cleanly into %s; resolve it on the branch, re-run the verify command, then merge again" % branch)
        print("merged `main` into %s first; re-run the verify command if `main` brought product changes" % branch)
    try:
        flowlib.move_main(root, flowlib.git_must(["rev-parse", "HEAD"], cwd=root))
    except flowlib.FlowError as error:
        return fail(str(error))
    print("merged %s into `main` (%s)" % (branch, flowlib.git_out(["rev-parse", "--short", flowlib.MAIN], cwd=root)))
    pushed, note = flowlib.push_main(root)
    if note:
        print(note)
    if not pushed:
        print("The branch is left in place; give the approval again to push and tidy up.")
        return 1
    if config["deploys"]:
        if flowlib.has_origin(root):
            print("the merge publishes: the deploy pipeline runs now")
        else:
            print("NOTE: this project's merge is meant to publish, but there is no `origin` remote; nothing was pushed")
    return tidy(root, branch)


if __name__ == "__main__":
    sys.exit(main())
