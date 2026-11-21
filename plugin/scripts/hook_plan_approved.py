#!/usr/bin/env python3
"""PostToolUse hook for ExitPlanMode: the owner accepting the plan is the plan approval.

When the owner accepts the plan Claude Code shows on leaving plan mode, this
hook writes the accepted text, unchanged, as specs/<folder>/plan.md, writes
the approval mark (flowlib.PLAN_MARK) next to it and commits the two on the
working branch. The Edit/Write hook lets product files through only once the
mark is there. `main` does not move.

Recorded only when the branch's change is of the normal or high-risk tier,
its spec is accepted (on `main`) and no plan is approved yet; otherwise the
hook says why nothing was recorded. A plan accepted after the approval (a
fix round planned in plan mode) leaves plan.md alone: a departure from the
approved plan is written into plan.md's Departures section.

The text comes from the tool's response (`plan`), else its input (`plan`),
else the file the response names (`filePath`).

A plan without the template's shape (the "For the owner" section and the
rest, check_shape.py) is not recorded (ruled 2026-11-20), as「批准 plan」
refuses it: the owner's review rests on that section, and a plan accepted
in plan mode for something else — before the real plan is drafted — must not
become the plan approval. The session is told to go back to plan mode.

Fired inside a subagent (the input carries `agent_id`), the hook does
nothing: only the main session's plan is the owner's to accept.

Seen in use (2026-11-20): the hook does not fire when the owner sends the
plan back. Not yet seen: an approval that carries feedback (text typed at
the third option, then shift+tab).

Where the repository has no .claude/flow.json the hook does nothing.
"""

import json
import os
import sys

import check_shape
import flowlib


# What the session does next is the owner's choice, made at the question the plan skill asks before the
# hand-over (ruled 2026-11-21): the default is to go on; a stop lets him clear the context first.
AFTER_APPROVAL = (
    "The plan is approved. Do what the owner chose at the question before the hand-over. "
    "He chose to stop: reply with one line — the plan is committed, with its hash, and after /clear he says「继续」 — and stop there. "
    "He chose to go on, or was not asked: carry on in this session with the implementation (skill: implement)."
)


def accepted_text(data):
    """The plan text the owner accepted, or None when the hook input does not carry it."""
    response = data.get("tool_response") if isinstance(data.get("tool_response"), dict) else {}
    for source in (response, data.get("tool_input") or {}):
        if isinstance(source.get("plan"), str) and source["plan"].strip():
            return source["plan"]
    plan_file = response.get("filePath")
    if plan_file and os.path.isfile(plan_file):
        with open(plan_file, encoding="utf-8") as handle:
            return handle.read()
    return None


def say(to_owner, to_model):
    print(json.dumps({
        "systemMessage": to_owner,
        "hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": to_model},
    }, ensure_ascii=False))


def main():
    data = json.load(sys.stdin)
    if data.get("agent_id"):
        return  # fired inside a subagent: not the plan the owner accepted
    root = flowlib.repo_root(data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR"))
    if not root or flowlib.load_config(root) is None or not flowlib.is_setup(root):
        return
    folder = flowlib.change_folder(root)
    refusal = flowlib.plan_approval_refusal(root, folder)
    if refusal:
        say("flow · plan accepted in plan mode — not recorded as the plan approval: %s" % refusal,
            "The plan approval was not recorded: %s. If this plan is a departure from an approved plan, "
            "write it into plan.md's Departures section." % refusal)
        return
    text = accepted_text(data)
    if text is None:
        say("flow · plan accepted in plan mode — not recorded: the hook did not receive the plan text",
            "The plan approval was not recorded because the hook did not receive the plan text. Write the accepted plan "
            "to %s/plan.md unchanged, commit it, and ask the owner to type「%s」." % (folder, flowlib.owner_sentence("plan")))
        return
    problems = check_shape.problems_in("plan", text)
    if problems:
        say("flow · plan accepted in plan mode — not recorded as the plan approval: it lacks the template's shape (%s)" % "; ".join(problems),
            "The plan approval was not recorded: the accepted plan lacks the template's shape (%s). Go back into plan mode, "
            "complete the plan from the template (\"For the owner\" first) and hand it to the owner again." % "; ".join(problems))
        return
    lines = flowlib.record_plan_approval(root, folder, "accepted in plan mode", text)
    say("flow · " + "\n".join(lines),
        "\n".join(lines) + "\n" + AFTER_APPROVAL)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as error:  # a broken hook must not block work: report and let the session go on
        print("flow hook (ExitPlanMode) error: %s" % error, file=sys.stderr)
        sys.exit(1)
