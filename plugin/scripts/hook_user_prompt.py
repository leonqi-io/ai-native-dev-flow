#!/usr/bin/env python3
"""UserPromptSubmit hook: the owner's approval sentence runs the approval.

When the whole message the owner submits is one of the approval sentences
(flowlib.OWNER_SENTENCES — 「接受立项」「接受 intent」「接受 spec」「批准 plan」
「确认合并」), this hook runs accept.py or merge.py itself, before the model
sees the message, and hands the script's output to the model as context and
to the owner as a one-block message. The model takes no part in deciding
whether an approval was given: a message with anything else in it is an
ordinary message, and the agent's own calls of those scripts stay refused by
the Bash hook.

The scripts are the ones the owner could run in his terminal, with the same
refusals; a refused approval changes nothing and says what is missing.

Second use, as a PreToolUse hook (see hooks.json): the event also fires for
prompts a session gives itself — a scheduled wake-up, a message from another
session — and its input does not say where a prompt came from. So a call of
one of those tools whose text is an approval sentence is denied.

Limit: a sentence reaching the session by a route this guard does not see
would be taken for the owner's. As in every pattern-matched block: it stops
an agent stepping over an approval, not one set on going around it.

Where the repository has no .claude/flow.json the hook does nothing.
"""

import json
import os
import subprocess
import sys

import flowlib

# After an approval the session carries on without waiting (ruled 2026-11-19); the owner can interrupt.
NEXT_STEP = {
    "setup": "carry on with the next step of the flow",
    "intent": "carry on with the small change without another stop, up to the merge prompt",
    "spec": "carry on in this session with the plan: enter plan mode and draft plan.md (skill: plan); the owner accepting the plan there approves it",
    "plan": "carry on in this session with the implementation (skill: implement)",
    "merge": "the change is merged; nothing follows in this change",
}
RUN_TIMEOUT = 100  # seconds for the script; hooks.json gives this hook 120 (the event's default of 30 is too short for a merge that pushes)
SHOWN_TO_OWNER = 700  # characters of the script's output in the message the owner sees: enough for a setup's file list, short enough to read at a glance


def flow_root(data):
    """The repository root when the flow is in use there, else None."""
    root = flowlib.repo_root(data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR"))
    if not root or flowlib.load_config(root) is None:
        return None
    return root


def strings_in(value):
    """Every string inside a tool input, however nested."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            for text in strings_in(item):
                yield text
    elif isinstance(value, list):
        for item in value:
            for text in strings_in(item):
                yield text


def guard_self_prompt(data):
    """PreToolUse: a session may not hand itself (or another session) an approval sentence."""
    if not any(flowlib.owner_act(text) for text in strings_in(data.get("tool_input"))):
        return
    if not flow_root(data):
        return
    reason = (
        "This text is one of the owner's approval sentences. Only the owner types it; "
        "a scheduled prompt or a message between sessions may not carry it."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}, ensure_ascii=False))


def run_approval(data):
    if data.get("agent_id"):
        return  # fired inside a subagent: not the owner's message
    act = flowlib.owner_act(data.get("prompt"))
    if not act:
        return
    root = flow_root(data)
    if not root:
        return
    script, arguments = ("merge", []) if act == "merge" else ("accept", [act])
    branch = flowlib.current_branch(root) or "(detached HEAD)"
    command = "%s.py %s" % (script, " ".join(arguments))
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(flowlib.scripts_dir(), script + ".py")] + arguments,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )
        code, output = result.returncode, (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        code, output = 124, "the script did not finish within %d seconds; run the state script to see what was done" % RUN_TIMEOUT
    sentence = flowlib.owner_sentence(act)
    verdict = "done" if code == 0 else "REFUSED — nothing was approved"
    headline = "flow ·「%s」→ %s on %s: %s" % (sentence, command.strip(), branch, verdict)
    if code == 0:
        instruction = (
            "This approval is given and recorded. Do not run accept.py or merge.py yourself. "
            "Tell the owner the result in one line; then %s." % NEXT_STEP[act]
        )
    else:
        instruction = (
            "Nothing was approved and `main` did not move. Do not run accept.py or merge.py yourself and do not look for "
            "another way. Fix what the output names if it is yours to fix (an uncommitted file, a failed check), tell the "
            "owner in one line what was missing, and ask him to type the sentence again."
        )
    context = "The owner typed the approval sentence「%s」. The flow hook ran `%s` on branch `%s` (exit code %d). Its output:\n%s\n\n%s" % (
        sentence,
        command.strip(),
        branch,
        code,
        output or "(no output)",
        instruction,
    )
    shown = output if len(output) <= SHOWN_TO_OWNER else output[:SHOWN_TO_OWNER].rstrip() + "\n…"
    print(
        json.dumps(
            {
                "systemMessage": headline + ("\n" + shown if shown else ""),
                "hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context},
            },
            ensure_ascii=False,
        )
    )


def main():
    data = json.load(sys.stdin)
    if data.get("hook_event_name") == "PreToolUse":
        guard_self_prompt(data)
    else:
        run_approval(data)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken hook must not block work: report and let the message through
        print("flow hook (UserPromptSubmit) error: %s" % error, file=sys.stderr)
        sys.exit(1)
