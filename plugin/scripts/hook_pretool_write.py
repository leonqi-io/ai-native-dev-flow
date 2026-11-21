#!/usr/bin/env python3
"""PreToolUse hook for Edit / Write: presence checks, and the plan approval mark.

Presence checks (deny, the reason names the route) — they look only at
whether the earlier approval is recorded, never at its content:
  spec.md / validation.md   need intent.md with its 'Tier:' line (normal, high-risk)
  plan.md                   needs spec.md and validation.md on `main`
  product files             need the plan approval mark (small change: intent.md on `main`)
  plan-approved.txt         never written by a tool: only the plan approval writes it
  specs/roadmap.md          its "To do" lines are not removed, rewritten or added here
                            (ruled 2026-11-20/21): they move on `main`, through
                            roadmap_edit.py and todo_add.py. Not held while a merge
                            is being resolved — the close check reads the result.
Product file = anything outside specs/, CLAUDE.md and the project's
`non_product_paths`.

Test files are not held here: since 2026-11-19 a change to a locked test
file asks nobody; the session records a `test-release:` line and the close
check (check_test_scope.py) refuses a changed test file that has none.

Where the repository has no .claude/flow.json, or the project is not set up
yet, the hook does nothing.
"""

import json
import os
import re
import sys

import flowlib

CHAIN_FILE = re.compile(r"^specs/([^/]+)/(spec|validation|plan)\.md$")
MARK_FILE = re.compile(r"^specs/[^/]+/%s$" % re.escape(flowlib.PLAN_MARK))
PLAN_ROUTE = (
    "the plan is drafted in plan mode and the owner accepting it there approves it "
    "(an acceptance that left no mark: the owner types「%s」)" % flowlib.owner_sentence("plan")
)


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}, ensure_ascii=False))
    sys.exit(0)


def check_chain_file(root, name, part):
    folder = "%s/%s" % (flowlib.SPECS, name)
    tier = flowlib.tier_of(root, folder)
    if tier is None:
        decide("deny", "Write %s/intent.md first, with its 'Tier:' line." % folder)
    if tier == "small" and part in ("spec", "plan"):
        decide("deny", "A small change has no %s.md — only intent.md and validation.md." % part)
    if part == "plan" and not (flowlib.on_main(root, folder + "/spec.md") and flowlib.on_main(root, folder + "/validation.md")):
        decide("deny", "spec.md and validation.md are not on `main` yet ('spec accepted' comes first): %s." % flowlib.owner_route("spec"))


def check_product_file(root, path):
    branch = flowlib.current_branch(root)
    folder = flowlib.change_folder(root)
    if not folder or not flowlib.folder_exists(root, folder):
        decide(
            "deny",
            "%s is a product file and branch `%s` has no change folder. Product changes run on a working branch named "
            "after their folder specs/<date>-<slug>/: start with the intent, or handle it as a small change." % (path, branch or "(detached)"),
        )
    tier = flowlib.tier_of(root, folder)
    if tier is None:
        decide("deny", "%s/intent.md carries no 'Tier:' line." % folder)
    if tier == "small":
        if not flowlib.on_main(root, folder + "/intent.md"):
            decide("deny", "intent.md is not on `main` yet: ask for the one-click confirmation by running accept.py intent.")
        return
    if not flowlib.on_main(root, folder + "/spec.md"):
        decide("deny", "The spec is not accepted yet ('spec accepted', then the plan, come before code and tests): %s." % flowlib.owner_route("spec"))
    if not flowlib.plan_approved(root, folder):
        decide("deny", "The plan is not approved yet (it comes before code and tests): %s." % PLAN_ROUTE)


def text_after_call(tool_input, current):
    """The file's text once the Edit / Write / MultiEdit call has run, or None when it cannot be told."""
    if isinstance(tool_input.get("content"), str):
        return tool_input["content"]
    edits = tool_input.get("edits") or [tool_input]
    result = current
    for edit in edits:
        old, new = edit.get("old_string"), edit.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or old not in result:
            return None
        result = result.replace(old, new) if edit.get("replace_all") else result.replace(old, new, 1)
    return result


def check_roadmap(root, tool_input):
    current = flowlib.read_worktree(root, flowlib.ROADMAP)
    merging = flowlib.git(["rev-parse", "-q", "--verify", "MERGE_HEAD"], cwd=root).returncode == 0
    if current is None or merging:
        return
    after = text_after_call(tool_input, current)
    if after is None:
        return
    removed, added = flowlib.todo_difference(current, after)
    if removed or added:
        what = "; ".join(part for part in ("removes or rewrites: " + " | ".join(removed) if removed else "", "adds: " + " | ".join(added) if added else "") if part)
        decide("deny", "This edit changes the roadmap's To do section on a branch (%s). Leave the section as it is: %s." % (what, flowlib.todo_route()))


def main():
    data = json.load(sys.stdin)
    file_path = (data.get("tool_input") or {}).get("file_path") or (data.get("tool_input") or {}).get("notebook_path")
    if not file_path:
        return
    start = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR")
    if not os.path.isabs(file_path):
        file_path = os.path.join(start or os.getcwd(), file_path)
    root = flowlib.repo_root(os.path.dirname(file_path) if os.path.isdir(os.path.dirname(file_path)) else start)
    if not root:
        return
    path = os.path.relpath(os.path.realpath(file_path), os.path.realpath(root)).replace(os.sep, "/")
    if path.startswith(".."):
        return
    config = flowlib.load_config(root)
    if config is None or not flowlib.is_setup(root):
        return
    if path == flowlib.ROADMAP:
        check_roadmap(root, data.get("tool_input") or {})
    if MARK_FILE.match(path):
        decide("deny", "%s is the plan approval mark: only the plan approval writes it — %s." % (path, PLAN_ROUTE))
    chain = CHAIN_FILE.match(path)
    if chain:
        check_chain_file(root, chain.group(1), chain.group(2))
        return
    if flowlib.is_non_product(path, config):
        return
    check_product_file(root, path)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken hook must not block work: report and let the call through
        print("flow hook (Edit/Write) error: %s" % error, file=sys.stderr)
        sys.exit(1)
