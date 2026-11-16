#!/usr/bin/env python3
"""PreToolUse hook for Bash: `main` moves only by the owner's act.

Three kinds of answer:
  deny   a git command that would move `main` — the reason names the route;
  ask    the three fixed scripts whose run *is* the owner's act when he
         approves the prompt (accept.py intent for a small change, merge.py
         for a small change, roadmap_edit.py);
  allow  the plugin's read-only scripts and todo_add.py (append-only).
Everything else: no decision (the normal permission flow applies).

Where the repository has no .claude/flow.json the hook does nothing.
Limit, as in every pattern-matched block: it stops an agent stepping over an
approval, not a person going around it.
"""

import json
import os
import re
import shlex
import subprocess
import sys

import flowlib

READ_ONLY = {"state", "close_check", "check_shape", "check_rid_coverage", "check_test_scope", "check_leftovers", "check_plan_drift"}
OWNER_ACTS = {"accept", "merge", "roadmap_edit"}
OWN_CALL = re.compile(r"""^\s*python3?\s+(?:"([^"]+)"|'([^']+)'|(\S+))(?:\s+(.*))?$""", re.DOTALL)
SHELL_JOIN = re.compile(r"[;&|<>`\n]|\$\(")
ON_MAIN_VERBS = {"commit", "merge", "rebase", "reset", "revert", "cherry-pick", "am", "pull"}
OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))
    sys.exit(0)


def routes():
    return (
        "In this flow `main` moves only by the owner's act; do not look for another way to run this. Routes: "
        "an approval file (intent / spec + validation / plan) -> the owner runs `%s` in his own terminal; "
        "a merge -> `%s` (or the PR, where the project uses PRs); "
        "a finding to record -> `%s`."
        % (flowlib.script_line("accept", "<intent|spec|plan>"), flowlib.script_line("merge"), flowlib.script_line("todo_add", "--who", "<name>", '"<sentence>"'))
    )


def own_script(command):
    """(script name, argument string) when the command is one call of a script of this plugin."""
    found = OWN_CALL.match(command)
    if not found:
        return None, None
    path = found.group(1) or found.group(2) or found.group(3)
    if os.path.dirname(os.path.realpath(path)) != flowlib.scripts_dir() or not path.endswith(".py"):
        return None, None
    return os.path.basename(path)[:-3], (found.group(4) or "").strip()


def clip(text, limit):
    text = re.sub(r"<!--.*?-->\n?", "", text or "", flags=re.DOTALL).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + "\n… (cut; the full file is in the change folder)"


def handle_own(name, arguments, root, config):
    if name in READ_ONLY or name == "todo_add":
        decide("allow", "flow plugin script (%s)" % name)
    if name not in OWNER_ACTS:
        return
    folder = flowlib.change_folder(root)
    tier = flowlib.tier_of(root, folder) if folder else None
    if name == "roadmap_edit":
        import roadmap_edit

        try:
            parsed = roadmap_edit.parse(shlex.split(arguments))
            if not parsed:
                decide("deny", "roadmap_edit.py: wrong arguments. Usage: delete --match \"<text>\" --reason fix-now|dismissed, or move --match \"<text>\"")
            _, line = roadmap_edit.find_line(root, parsed[1])
        except (ValueError, flowlib.FlowError) as error:
            decide("deny", "roadmap_edit.py: %s" % error)
        action = "move to Planned stages" if parsed[0] == "move" else "delete (%s)" % parsed[2]
        decide("ask", "Roadmap To do — %s:\n%s" % (action, line))
    if name == "merge" and arguments == "--check":
        decide("allow", "merge.py --check changes nothing")
    if tier != "small":
        decide("deny", "%s.py is the owner's act for the %s tier — he runs it in his own terminal. %s" % (name, tier or "unknown", routes()))
    intent = flowlib.read_worktree(root, folder + "/intent.md")
    if name == "accept":
        if arguments != "intent":
            decide("deny", "a small change accepts only its intent: accept.py intent")
        decide(
            "ask",
            "Small change — approve to accept this intent. It is committed to `main`; the work then runs without "
            "another stop until the merge prompt.\n\n" + clip(intent, 1800),
        )
    if arguments:
        decide("deny", "merge.py takes no argument (or --check)")
    # Do not spend the owner's click on a merge the script would refuse anyway.
    precheck = subprocess.run(
        [sys.executable, os.path.join(flowlib.scripts_dir(), "merge.py"), "--check"], cwd=root, capture_output=True, text=True
    )
    if precheck.returncode != 0:
        refusals = [line for line in precheck.stdout.splitlines() if line.startswith(("FAIL", "REFUSED"))]
        decide("deny", "merge.py would refuse this merge — fix these first:\n" + "\n".join(refusals))
    base = flowlib.merge_base(root)
    stat =flowlib.git_out(["diff", "--stat", base, "HEAD"], cwd=root) if base else "(no merge base with main)"
    publishes = "Merging publishes to production.\n\n" if config["deploys"] else ""
    decide(
        "ask",
        "Merge this small change into `main`?\n\n%sIntent:\n%s\n\nChanged files:\n%s" % (publishes, clip(intent, 900), clip(stat, 1200)),
    )


def git_segments(command):
    """Yield (verb, arguments, -C path) for every git call in a shell command."""
    for piece in re.split(r"&&|\|\||[;|\n]", command):
        try:
            tokens = shlex.split(piece)
        except ValueError:
            tokens = piece.split()
        positions = [index for index, token in enumerate(tokens) if token == "git" or token.endswith("/git")]
        if not positions:
            continue
        index, directory = positions[0] + 1, None
        while index < len(tokens) and tokens[index].startswith("-"):
            if tokens[index] in OPTIONS_WITH_VALUE and index + 1 < len(tokens):
                if tokens[index] == "-C":
                    directory = tokens[index + 1]
                index += 2
            else:
                index += 1
        if index < len(tokens):
            yield tokens[index], tokens[index + 1:], directory


def names_main(argument):
    """True for a push / fetch refspec whose destination is main."""
    destination = argument.lstrip("+").split(":")[-1]
    return destination in (flowlib.MAIN, "refs/heads/" + flowlib.MAIN)


def moves_main(command, root):
    """A sentence saying how the command would move `main`, or None."""
    effective = flowlib.current_branch(root)
    for verb, arguments, directory in git_segments(command):
        branch = effective
        if directory:
            branch = flowlib.current_branch(os.path.join(root, directory)) or effective
        plain = [argument for argument in arguments if not argument.startswith("-")]
        if verb in ("checkout", "switch") and "--" not in arguments and flowlib.MAIN in plain:
            if "-B" in arguments or "-C" in arguments:
                if plain and plain[0] == flowlib.MAIN:
                    return "`git %s` would reset the branch `main`" % verb
            elif not ("-b" in arguments or "-c" in arguments):
                effective = branch = flowlib.MAIN  # later segments run on main
            continue
        if verb in ON_MAIN_VERBS and branch == flowlib.MAIN:
            return "`git %s` on `main`" % verb
        if verb == "push":
            if "--all" in arguments or "--mirror" in arguments or any(names_main(argument) for argument in plain[1:]):
                return "`git push` to `main`"
            if branch == flowlib.MAIN and len(plain) <= 1:
                return "`git push` of the current branch, which is `main`"
        if verb == "fetch" and any(":" in argument and names_main(argument) for argument in plain):
            return "`git fetch` into `main`"
        if verb == "branch" and flowlib.MAIN in plain and any(flag in arguments for flag in ("-f", "--force", "-M", "-m", "--move", "-D", "-d", "--delete", "-C", "-c", "--copy")):
            return "`git branch` changing `main`"
        if verb in ("update-ref", "symbolic-ref") and any("refs/heads/" + flowlib.MAIN in argument for argument in arguments):
            return "`git %s` on refs/heads/main" % verb
    return None


def main():
    data = json.load(sys.stdin)
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command") or ""
    root = flowlib.repo_root(data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR"))
    if not root:
        return
    config = flowlib.load_config(root)
    if config is None:
        return
    if not SHELL_JOIN.search(command):
        name, arguments = own_script(command)
        if name:
            handle_own(name, arguments, root, config)
            return
    elif any(("scripts/%s.py" % name) in command for name in OWNER_ACTS):
        decide("deny", "run accept.py, merge.py or roadmap_edit.py alone, as one command with nothing chained to it")
    reason = moves_main(command, root)
    if reason:
        decide("deny", "Blocked: %s. %s" % (reason, routes()))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken hook must not block work: report and let the call through
        print("flow hook (Bash) error: %s" % error, file=sys.stderr)
        sys.exit(1)
