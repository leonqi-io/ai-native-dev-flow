#!/usr/bin/env python3
"""Set the `flow-template` mark of the project templates a project copies.

The mark is a date and a short hash of the template's content
(`flow-template: 2026-11-21 3fa9c1e`). A project's copy carries the mark of
the template it was last brought in step with, and the state report names
every copy whose mark differs from the template's. The hash is what tells
two versions of one day apart; the date is for the person reading it.

The mark is never typed by hand: this script writes it, and the self-test
refuses a template whose mark does not match its content.

Usage (from the repository root, after changing a file under plugin/templates/project/):
    python3 tools/template_marks.py            rewrite the mark of every template whose content changed
    python3 tools/template_marks.py --check    change nothing; exit 1 when a mark does not match its content
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plugin", "scripts"))

import flowlib  # noqa: E402  (the path above has to be set first)


def template_paths():
    return [os.path.join(flowlib.templates_dir(), name) for name in sorted(set(flowlib.MARKED_TEMPLATES.values()))]


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def mark_is_current(text):
    """True when the template's mark carries the hash of the template's present content."""
    mark = flowlib.template_mark(text)
    return mark is not None and mark.endswith(" " + flowlib.template_content_hash(text))


def with_new_mark(text):
    """The template with today's date and the hash of its content in its mark; None when it has no mark to rewrite."""
    if not flowlib.TEMPLATE_MARK.search(text):
        return None
    new_mark = "%s %s" % (flowlib.today(), flowlib.template_content_hash(text))
    return flowlib.TEMPLATE_MARK.sub(lambda found: found.group("label") + new_mark, text, count=1)


def main():
    check_only = sys.argv[1:] == ["--check"]
    if sys.argv[1:] and not check_only:
        print(__doc__.strip())
        return 2
    stale = [path for path in template_paths() if not mark_is_current(read(path))]
    for path in stale:
        relative = os.path.relpath(path, ROOT)
        if check_only:
            print("FAIL %s: its flow-template mark does not match its content — run python3 tools/template_marks.py" % relative)
            continue
        rewritten = with_new_mark(read(path))
        if rewritten is None:
            print("FAIL %s: it has no flow-template mark to rewrite" % relative)
            return 1
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(rewritten)
        print("marked %s: %s" % (relative, flowlib.template_mark(rewritten)))
    if not stale:
        print("template marks: every mark matches its content")
    return 1 if (check_only and stale) else 0


if __name__ == "__main__":
    sys.exit(main())
