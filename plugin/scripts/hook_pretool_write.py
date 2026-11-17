#!/usr/bin/env python3
"""PreToolUse hook for Edit / Write: presence checks and the test-file lock.

Presence checks (deny, the reason names the route) — they look only at
whether the earlier approval file is on `main`, never at its content:
  spec.md / validation.md   need intent.md on `main`
  plan.md                   needs spec.md and validation.md on `main`
  product files             need plan.md on `main` (small change: intent.md)
Product file = anything outside specs/, CLAUDE.md and the project's
`non_product_paths`.

Test-file lock (ask): while the lock is on, an edit to a path in the
project's `test_scope` prompts the owner. The lock is on from the commit of
red-run.txt (normal, high-risk) or for the whole branch (small change).

Where the repository has no .claude/flow.json, or the project is not set up
yet, the hook does nothing.
"""

import json
import os
import re
import sys

import flowlib

CHAIN_FILE = re.compile(r"^specs/([^/]+)/(spec|validation|plan)\.md$")


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}, ensure_ascii=False))
    sys.exit(0)


def owner_line(what):
    return flowlib.owner_route(what)


def check_chain_file(root, name, part):
    folder = "%s/%s" % (flowlib.SPECS, name)
    tier = flowlib.tier_of(root, folder)
    if tier is None:
        decide("deny", "Write %s/intent.md first, with its 'Tier:' line." % folder)
    if tier == "small" and part in ("spec", "plan"):
        decide("deny", "A small change has no %s.md — only intent.md and validation.md." % part)
    if part in ("spec", "validation") and not flowlib.on_main(root, folder + "/intent.md"):
        route = "ask for the one-click confirmation by running accept.py intent" if tier == "small" else owner_line("intent")
        decide("deny", "intent.md is not on `main` yet ('intent accepted' comes first): %s." % route)
    if part == "plan" and not (flowlib.on_main(root, folder + "/spec.md") and flowlib.on_main(root, folder + "/validation.md")):
        decide("deny", "spec.md and validation.md are not on `main` yet ('spec accepted' comes first): %s." % owner_line("spec"))


def check_product_file(root, config, path):
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
    if not flowlib.on_main(root, folder + "/intent.md"):
        route = "ask for the one-click confirmation by running accept.py intent" if tier == "small" else owner_line("intent")
        decide("deny", "intent.md is not on `main` yet: %s." % route)
    if tier != "small" and not flowlib.on_main(root, folder + "/plan.md"):
        decide("deny", "plan.md is not on `main` yet ('plan approved' comes before code and tests): %s." % owner_line("plan"))
    if flowlib.matches(path, config["test_scope"]) and flowlib.test_lock_on(root, folder, tier):
        decide(
            "ask",
            "Test file in the locked scope: %s\nThe red run is committed (small change: the whole branch is locked). Approve only "
            "a legitimate test fix; the agent then records 'test-release: %s — why — which §1 row' in the Approval log." % (path, path),
        )


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
    chain = CHAIN_FILE.match(path)
    if chain:
        check_chain_file(root, chain.group(1), chain.group(2))
        return
    if flowlib.is_non_product(path, config):
        return
    check_product_file(root, config, path)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken hook must not block work: report and let the call through
        print("flow hook (Edit/Write) error: %s" % error, file=sys.stderr)
        sys.exit(1)
