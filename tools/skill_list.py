#!/usr/bin/env python3
"""Generate the "测试通过的说法" table of docs/skills.md from the eval cases.

A phrasing appears in that table only because a case with that prompt exists
and passed in the latest plugin-eval run — it is never typed by hand.

Reads   plugin/evals/<case>/prompt.md              the phrasing (the body)
        plugin/evals/<case>/graders/*.md           which skill the case checks
        plugin/evals/results/<latest>/aggregate-result.json   the scores
Writes  the block between the two markers in docs/skills.md

Usage (from the repository root, after `claude plugin eval plugin --ablation none`):
    python3 tools/skill_list.py
    python3 tools/skill_list.py --no-results     first generation, before any run: every row reads 未跑
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
EVALS = os.path.join(ROOT, "plugin", "evals")
SKILLS = os.path.join(ROOT, "plugin", "skills")
DOC = os.path.join(ROOT, "docs", "skills.md")
START, END = "<!-- generated:phrasings:start -->", "<!-- generated:phrasings:end -->"
SKILL_IN_GRADER = re.compile(r"\)\?([\w-]+)\"")


def body_of(path):
    """Text after the frontmatter of a Markdown file."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    if text.startswith("---\n"):
        text = text.split("---\n", 2)[2]
    return " ".join(text.split())


def cases():
    """[(case name, skill, phrasing)] for every case directory."""
    found = []
    for prompt in sorted(glob.glob(os.path.join(EVALS, "*", "prompt.md"))):
        directory = os.path.dirname(prompt)
        skill = None
        for grader in glob.glob(os.path.join(directory, "graders", "*.md")):
            with open(grader, encoding="utf-8") as handle:
                match = SKILL_IN_GRADER.search(handle.read())
            if match:
                skill = match.group(1)
        found.append((os.path.basename(directory), skill, body_of(prompt)))
    return found


def latest_results():
    """(run name, {case name: score}, Claude Code version) of the newest results folder, or None."""
    runs = sorted(glob.glob(os.path.join(EVALS, "results", "*", "aggregate-result.json")))
    if not runs:
        return None
    with open(runs[-1], encoding="utf-8") as handle:
        document = json.load(handle)
    scores = {case["name"]: case.get("aggregates", {}).get("score") for case in document.get("cases", [])}
    return os.path.basename(os.path.dirname(runs[-1])), scores, document.get("claudeVersion", "?")


def table(results):
    lines = ["| skill | 保底启动 | 测试通过的说法 | 用例 | 最近一次结果 |", "|---|---|---|---|---|"]
    by_skill = {}
    for name, skill, phrasing in cases():
        by_skill.setdefault(skill, []).append((name, phrasing))
    for skill in sorted(os.listdir(SKILLS)):
        if not os.path.isfile(os.path.join(SKILLS, skill, "SKILL.md")):
            continue
        passed, case_names, outcomes = [], [], []
        for name, phrasing in by_skill.get(skill, []):
            case_names.append("`plugin/evals/%s/`" % name)
            score = results[1].get(name) if results else None
            if score is None:
                outcomes.append("未跑")
            elif score >= 1.0:
                passed.append("「%s」" % phrasing)
                outcomes.append("通过")
            else:
                outcomes.append("未通过（%.2f）" % score)
        lines.append(
            "| %s | `/flow:%s` | %s | %s | %s |"
            % (skill, skill, "<br>".join(passed) or "（还没有通过的记录）", "<br>".join(case_names) or "（没有用例）", "<br>".join(outcomes) or "—")
        )
    if results:
        lines.append("")
        lines.append("生成依据：`plugin/evals/results/%s/`，Claude Code %s。" % (results[0], results[2]))
    else:
        lines.append("")
        lines.append("生成依据：还没有跑过插件测试。")
    return "\n".join(lines)


def main():
    results = latest_results()
    if results is None and "--no-results" not in sys.argv[1:]:
        print("no results under plugin/evals/results/ — run the plugin evals first, or pass --no-results")
        return 1
    with open(DOC, encoding="utf-8") as handle:
        text = handle.read()
    if START not in text or END not in text:
        print("docs/skills.md has no generated block markers")
        return 1
    head, rest = text.split(START, 1)
    tail = rest.split(END, 1)[1]
    with open(DOC, "w", encoding="utf-8") as handle:
        handle.write(head + START + "\n" + table(results) + "\n" + END + tail)
    print("docs/skills.md updated (%s)" % (results[0] if results else "no results yet"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
