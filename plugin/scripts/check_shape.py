#!/usr/bin/env python3
"""Shape check: does an artifact carry the headings its template defines?

A backstop for a skill that was skipped or half-followed — it says nothing
about the quality of the content, only that no part is missing.

Usage: check_shape.py <kind> <path>
Kinds: intent, intent-small, spec, validation, validation-small, plan,
       mission, decisions, roadmap
"""

import re
import sys

import flowlib

# kind -> headings (`## ` level, matched by how the title starts, case-insensitive)
HEADINGS = {
    "intent": ["Problem", "Proposed outcome", "Affected users and systems", "Constraints", "Open questions", "Source"],
    "intent-small": ["Problem", "Outcome", "Must not change", "Source"],
    "spec": ["Requirements", "Design", "Constraint trace", "Open-question trace", "Fact values", "Codebase facts", "Concerns"],
    "validation": ["§0", "§1", "Leftovers", "Approval log"],
    "validation-small": ["What changed", "Verify", "Review", "Leftovers", "Approval log"],
    "plan": ["For the owner", "Files that change", "Order of work", "Risks", "Proof", "Spec changed after acceptance", "Departures"],
    "mission": ["Who", "What they bring", "What they leave with", "What they do in between", "What this does not do"],
    "decisions": ["Decisions", "Cost of a bad release"],
    "roadmap": ["Planned stages", "To do", "Known limits"],
}


def problems_in(kind, text, tier=None):
    """List of sentences, empty when the shape is right."""
    if text is None:
        return ["the file does not exist"]
    found = []
    for heading in HEADINGS[kind]:
        if not flowlib.has_heading(text, heading):
            found.append("missing section '## %s'" % heading)
    if kind in ("intent", "intent-small"):
        declared = flowlib.read_tier(text)
        if declared is None:
            found.append("missing the line 'Tier: small | normal | high-risk'")
        elif kind == "intent-small" and declared != "small":
            found.append("the small-change intent must say 'Tier: small'")
        elif kind == "intent" and declared == "small":
            found.append("'Tier: small' uses the small-change intent form")
    if kind == "spec" and not re.search(r"^\s*[-*]\s*\*{0,2}R\d+\b", flowlib.section(text, "Requirements") or "", re.MULTILINE):
        found.append("the Requirements section defines no R-ID (a list item starting with R1, R2, ...)")
    if kind == "validation" and tier == "high-risk" and not flowlib.has_heading(text, "§3"):
        found.append("high-risk tier: '## §3 Expected changes' is mandatory")
    if kind == "roadmap" and not re.search(r"^Status:", text, re.MULTILINE):
        found.append("missing the 'Status:' line at the top")
    return found


def kind_of(path, tier):
    """Kind from the file name and the tier of its change."""
    name = path.replace("\\", "/").rsplit("/", 1)[-1]
    stem = name[:-3] if name.endswith(".md") else name
    if stem in ("intent", "validation") and tier == "small":
        return stem + "-small"
    return stem if stem in HEADINGS else None


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in HEADINGS:
        print(__doc__.strip())
        return 2
    kind, path = sys.argv[1], sys.argv[2]
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        text = None
    found = problems_in(kind, text)
    for sentence in found:
        print("FAIL %s: %s" % (path, sentence))
    if not found:
        print("PASS %s has the shape of '%s'" % (path, kind))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
