#!/usr/bin/env python3
"""State script: where the work stands, read from the repository alone.

Nothing here is remembered between sessions — the stage is derived from the
repository: which change folder the current branch maps to, which of intent /
spec / validation are on `main` (the approval record), whether the plan
approval mark is there, whether the red run is committed, and the latest
review and validation lines of the Approval log (read through record.py).
The same facts are what the hooks and the close check read, so a new session
that says "continue" picks up at the step the last one stopped at.

Usage: state.py            report for a person
       state.py --hook     session-start hook: prints nothing where the flow is not in use
"""

import json
import os
import sys

import flowlib
import record


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
    info["stale_templates"] = flowlib.stale_template_copies(root)
    folder = flowlib.change_folder(root)
    if folder and flowlib.folder_exists(root, folder):
        info["folder"] = folder
        info["tier"] = flowlib.tier_of(root, folder)
        info["on_main"] = {
            name: flowlib.on_main(root, "%s/%s.md" % (folder, name))
            for name in ("intent", "spec", "validation")
        }
        info["spec_drafted"] = flowlib.read_worktree(root, folder + "/spec.md") is not None
        info["plan_approved"] = flowlib.plan_approved(root, folder)
        info["red"] = flowlib.red_committed(root, folder)
        info["handoff"] = flowlib.handoff_note(root, folder)
        log = flowlib.approval_log(root, folder)
        info["review"] = record.latest_review(log)
        info["validation"] = record.latest_validation(log)
        # The branch is already in `main`: merged, but the tidy-up did not run (or the PR was merged on the page).
        remote = flowlib.origin_main(root)
        info["merged"] = info["on_main"]["intent"] and (
            flowlib.is_ancestor(root, "HEAD", flowlib.MAIN) or bool(remote and flowlib.is_ancestor(root, "HEAD", remote))
        )
    remote = flowlib.origin_main(root)
    info["main_behind"] = bool(
        remote and flowlib.main_exists(root) and remote != flowlib.git_out(["rev-parse", flowlib.MAIN], cwd=root) and flowlib.is_ancestor(root, flowlib.MAIN, remote)
    )
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
    """(stage name, what is going on, next step, the approval that is the owner's to give — a key of OWNER_SENTENCES — or None)."""
    if info["missing_setup"]:
        return (
            "Project setup",
            "not on `main` yet: " + ", ".join(info["missing_setup"]),
            "write mission.md, decisions.md and roadmap.md on a branch named `setup` (skill: setup-project)",
            "setup",
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
    if info["tier"] is None:
        return ("Plan", "intent.md has no 'Tier:' line", "add the tier to the intent", None)
    if info["tier"] == "small":
        return small_change_stage(info)
    if not info["on_main"]["intent"]:
        return before_spec_accepted(info)
    if info["merged"]:
        return merged_stage()
    return after_spec_accepted(info)


def merged_stage():
    return (
        "Merged",
        "this branch is already in `main`",
        "tidy up — the approval below switches this checkout to `main` and deletes the branch (a small change: run merge.py)",
        "merge",
    )


def small_change_stage(info):
    if not info["on_main"]["intent"]:
        return ("Plan", "small-change intent drafted", "ask for the one-click confirmation: run accept.py intent", None)
    if info["merged"]:
        return merged_stage()
    return (
        "Small change",
        "intent is on `main`",
        "validation.md, the change, the verify command, code-reviewer and verifier, then the close check and the merge click",
        None,
    )


def before_spec_accepted(info):
    """Normal and high-risk: the intent, the spec and the validation are being written, in one session."""
    if not info["spec_drafted"]:
        return (
            "Plan",
            "intent.md drafted; spec.md and validation.md not started",
            "carry on in this session with the spec (skill: spec); the owner accepts intent, spec and validation together",
            None,
        )
    return (
        "Design",
        "intent, spec and validation are being written",
        "finish the question loop; the owner reads intent.md, validation.md §0 (and §3) and accepts the three",
        "spec",
    )


def after_spec_accepted(info):
    """Normal and high-risk, from「接受 spec」to the merge: one small step at a time."""
    if not info["plan_approved"]:
        return (
            "Build",
            "spec accepted; the plan is not approved yet",
            "draft the plan in plan mode (skill: plan); the owner accepting it there is the approval",
            "plan",
        )
    if not info["red"]:
        return (
            "Test",
            "plan approved; the red run is not committed yet",
            "write the tests of validation.md §1, run the formatter on them, commit them with red-run.txt",
            None,
        )
    review = info["review"]
    if review is None or review["kind"] == "verifier" or review["important"]:
        situation = "red run committed; no review entry yet"
        if review is not None:
            situation = "latest review (%s): %d Important open — report: %s" % (review["kind"], review["important"], review["report"] or "none")
        return (
            "Build / Test",
            situation,
            "implement to green; then code-reviewer → verifier → reviewer, until the reviewer reports 0 Important (skill: implement)",
            None,
        )
    answers = info["validation"]
    if answers is None:
        return ("Validation", "reviewed: 0 Important open", "the end screen: the session's inventory, the owner's judgments (skill: validate)", None)
    failed = sorted(question for question, answer in answers.items() if answer == "fail")
    if failed:
        return (
            "Validation",
            "%s failed" % ", ".join(failed),
            "fix it, run code-reviewer → verifier → reviewer again, then ask the failed judgments again (skill: validate)",
            None,
        )
    how = "the branch is pushed and the PR opened; the owner's approval merges it" if info["config"]["pull_request"] else "the owner's approval merges it"
    return ("Close", "validated", "leftovers, the roadmap, the close check (skill: close); then " + how, "merge")


def render(info):
    if not info["enabled"]:
        return "flow: not in use in this repository (%s is missing)" % flowlib.CONFIG_PATH
    stage, situation, next_step, act = stage_of(info)
    lines = ["flow state · %s" % flowlib.now_stamp()]
    lines.append("project: %s" % ("NOT SET UP" if info["missing_setup"] else "set up"))
    lines.append("branch: %s" % (info["branch"] or "(detached HEAD)"))
    if "folder" in info:
        lines.append("change: %s/ · tier: %s" % (info["folder"], info["tier"] or "missing"))
        marks = " · ".join("%s.md %s" % (name, "yes" if present else "no") for name, present in info["on_main"].items())
        lines.append("on main: " + marks)
        if info["tier"] != "small":
            lines.append("plan approved: %s" % ("yes" if info["plan_approved"] else "no"))
            lines.append("red-run.txt: %s" % ("committed (test lock on)" if info["red"] else "not committed"))
    lines.append("stage: %s — %s" % (stage, situation))
    lines.append("next: " + next_step)
    if info.get("handoff"):
        lines.append("handoff: %s — an earlier session paused here; read it before anything else" % info["handoff"])
    if act:
        line = flowlib.script_line("merge") if act == "merge" else flowlib.script_line("accept", act)
        lines.append("owner's approval: type「%s」in the chat, as a message of its own — or run in your own terminal: %s" % (flowlib.owner_sentence(act), line))
    if info["main_behind"]:
        lines.append("main: behind origin/main (as last fetched) — bring it up to date: " + flowlib.script_line("sync_main"))
    if info["todo_count"]:
        lines.append("to do: %d open line(s), oldest %s" % (info["todo_count"], info["todo_oldest"]))
    else:
        lines.append("to do: no open line")
    if info["unread_small"]:
        lines.append("small changes not yet read by a fresh session: %d (%s)" % (len(info["unread_small"]), ", ".join(info["unread_small"])))
    if info["stale_templates"]:
        copies = ", ".join("%s (%s; template %s)" % (path, mark or "no mark", current) for path, mark, current in info["stale_templates"])
        lines.append("templates: not in step with the plugin's — %s. Compare with %s; the owner decides whether to bring them in step" % (copies, flowlib.templates_dir()))
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
