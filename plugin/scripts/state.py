#!/usr/bin/env python3
"""State script: where the work stands, read from the repository alone.

Nothing here is remembered between sessions — the stage is derived from Git:
which change folder the current branch maps to, which of intent / spec /
validation / plan are on `main` (the approval record), whether the red run is
committed. The same facts are what the hooks check.

Usage: state.py            report for a person
       state.py --hook     session-start hook: prints nothing where the flow is not in use
"""

import json
import os
import sys

import flowlib


def gather(root):
    """Facts about the repository, as a dict. Raises FlowError on a broken config."""
    info = {"root": root, "enabled": False}
    config = flowlib.load_config(root)
    if config is None:
        return info
    info["enabled"] = True
    info["config"] = config
    info["branch"] = flowlib.current_branch(root)
    info["missing_setup"] = [path for path in flowlib.SETUP_FILES if not flowlib.on_main(root, path)]
    roadmap = flowlib.roadmap_on_main(root)
    todo = flowlib.todo_lines(roadmap)
    info["todo_count"] = len(todo)
    info["todo_oldest"] = min((line[2:12] for line in todo), default=None)
    info["unread_small"] = unread_small_changes(root)
    folder = flowlib.change_folder(root)
    if folder and flowlib.folder_exists(root, folder):
        info["folder"] = folder
        info["tier"] = flowlib.tier_of(root, folder)
        info["on_main"] = {
            name: flowlib.on_main(root, "%s/%s.md" % (folder, name))
            for name in ("intent", "spec", "validation", "plan")
        }
        info["red"] = flowlib.red_committed(root, folder)
    return info


def unread_small_changes(root):
    """Small changes merged into `main` that no fresh-session review has read yet."""
    listing = flowlib.git_out(["ls-tree", "-d", "--name-only", flowlib.MAIN, flowlib.SPECS + "/"], cwd=root)
    unread = []
    for folder in listing.splitlines():
        if flowlib.read_tier(flowlib.read_main(root, folder + "/intent.md")) != "small":
            continue
        log = flowlib.section(flowlib.read_main(root, folder + "/validation.md"), "Approval log")
        if log is not None and "small-change read" not in log:
            unread.append(folder)
    return unread


def stage_of(info):
    """(stage name, what is going on, next step, the owner's pasteable line or None)."""
    if info["missing_setup"]:
        return (
            "Project setup",
            "not on `main` yet: " + ", ".join(info["missing_setup"]),
            "write mission.md, tech-stack.md and roadmap.md on a branch named `setup` (skill: setup-project)",
            flowlib.script_line("accept", "setup"),
        )
    if "folder" not in info:
        if info["branch"] == flowlib.MAIN:
            return ("No change in progress", "this checkout is on `main`", "start a change (skill: intent, or small-change)", None)
        return (
            "No change folder",
            "branch `%s` has no folder %s/%s/" % (info["branch"], flowlib.SPECS, info["branch"]),
            "a working branch is named after its change folder; start with the intent",
            None,
        )
    tier, accepted = info["tier"], info["on_main"]
    if tier is None:
        return ("Plan", "intent.md has no 'Tier:' line", "add the tier to the intent", None)
    if not accepted["intent"]:
        if tier == "small":
            return ("Plan", "small-change intent drafted", "ask for the one-click confirmation: run accept.py intent", None)
        return ("Plan", "intent drafted, waiting for 'intent accepted'", "the owner reads intent.md and commits it", flowlib.script_line("accept", "intent"))
    if tier == "small":
        return (
            "Small change",
            "intent is on `main`; the test files are locked for the whole branch",
            "validation.md, the change, the verify command, code-reviewer and verifier, then the close check and the merge click",
            None,
        )
    if not (accepted["spec"] and accepted["validation"]):
        return (
            "Design",
            "intent accepted; spec.md and validation.md are being written",
            "finish the question loop; the owner reads validation.md §0 (and §3) and commits the pair",
            flowlib.script_line("accept", "spec"),
        )
    if not accepted["plan"]:
        extra = " A fresh session reads the plan once more before the owner commits it (high-risk tier)." if tier == "high-risk" else ""
        return (
            "Build",
            "spec accepted; plan.md is being written",
            "draft plan.md in plan mode; the owner rules its points and commits it." + extra,
            flowlib.script_line("accept", "plan"),
        )
    if not info["red"]:
        return (
            "Test",
            "plan approved; the red run is not committed yet",
            "write the tests of validation.md §1, run the formatter on them, commit them with red-run.txt",
            None,
        )
    merge_line = None if info["config"]["pull_request"] else flowlib.script_line("merge")
    how = "open the PR; the owner merges it there" if info["config"]["pull_request"] else "the owner merges"
    return (
        "Build / Test / Deploy",
        "red run committed; the test files are locked",
        "implement to green, code-reviewer and verifier, review in a fresh session, the owner's validation, the close check, then " + how,
        merge_line,
    )


def render(info):
    if not info["enabled"]:
        return "flow: not in use in this repository (%s is missing)" % flowlib.CONFIG_PATH
    stage, situation, next_step, owner_line = stage_of(info)
    lines = ["flow state · %s" % flowlib.now_stamp()]
    lines.append("project: %s" % ("NOT SET UP" if info["missing_setup"] else "set up"))
    lines.append("branch: %s" % (info["branch"] or "(detached HEAD)"))
    if "folder" in info:
        lines.append("change: %s/ · tier: %s" % (info["folder"], info["tier"] or "missing"))
        marks = " · ".join("%s.md %s" % (name, "yes" if present else "no") for name, present in info["on_main"].items())
        lines.append("on main: " + marks)
        lines.append("red-run.txt: %s" % ("committed (test lock on)" if info["red"] else "not committed"))
    lines.append("stage: %s — %s" % (stage, situation))
    lines.append("next: " + next_step)
    if owner_line:
        lines.append("owner's line (run in your own terminal): " + owner_line)
    if info["todo_count"]:
        lines.append("to do: %d open line(s), oldest %s" % (info["todo_count"], info["todo_oldest"]))
    else:
        lines.append("to do: no open line")
    if info["unread_small"]:
        lines.append("small changes not yet read by a fresh session: %d (%s)" % (len(info["unread_small"]), ", ".join(info["unread_small"])))
    return "\n".join(lines)


def main():
    hook = "--hook" in sys.argv[1:]
    start_dir = None
    if hook:
        try:
            start_dir = json.load(sys.stdin).get("cwd")
        except ValueError:
            start_dir = None
        start_dir = start_dir or os.environ.get("CLAUDE_PROJECT_DIR")
    root = flowlib.repo_root(start_dir)
    if not root:
        if not hook:
            print("flow: not a Git repository")
        return 0
    try:
        info = gather(root)
    except flowlib.FlowError as error:
        print("flow: %s" % error)
        return 0 if hook else 1
    if hook and not info["enabled"]:
        return 0
    print(render(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
