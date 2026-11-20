#!/usr/bin/env python3
"""Record: append one line to the change's Approval log, in the form the scripts read.

    record.py review --by reviewer|verifier|fresh-session --important <n> --nit <n> --report <path>
    record.py validation J1=pass J2=fail J3=not-judged ...
    record.py test-release <path> --why "<sentence>" [--row <T-ID>]     (--row: the §1 row; a small change has none)
    record.py ruling "<the owner's ruling>" --checked "<what it was checked against>"

Lines written (the script adds the date and time):
    - <stamp> · review (reviewer) · Important open: 1 · Nit: 2 · at 3f2a9c1 · report: specs/<folder>/reports/review-1.md
    - <stamp> · validation · J1 pass · J2 not judged
    - <stamp> · test-release: tests/test_app.py · sha256 0a1b2c3d4e5f — <why> — §1 row T1
    - <stamp> · ruling: <sentence> · checked against: §0 J2, §3, R8

The session gives the facts, the script the form. A review line needs its
report already written in the change folder and no uncommitted product
change; it records the commit reviewed (HEAD), and the close check refuses a
product change after it. A test-release line records the content the release
covers (sha256 of the file as it is now, or "deleted"); the close check
refuses a released file that changed again. A validation line carries every
answer given so far: answers not given now are taken from the latest line,
so the latest line alone says where the validation stands. A question has to
be one §0 asks (J1, J2, ...).

Limit, accepted 2026-11-19: the implementing session runs this script and can
record wrongly; the close check trusts the lines. The commit and the content
hash (ruled 2026-11-20) narrow this to recording a review or a release that
did not happen; a change after one is caught.

This module also holds the parsers of these lines (close_check.py and
state.py read the Approval log through them), so the form lives in one place.
"""

import argparse
import os
import re
import sys

import flowlib

REVIEW_KINDS = {"reviewer": "reviewer", "verifier": "verifier", "fresh-session": "fresh session"}
ANSWERS = {"pass": "pass", "fail": "fail", "not-judged": "not judged"}

# "review" may carry more words before the bracket ("review, re-check (reviewer)").
REVIEW_LINE = re.compile(
    r"\breview\b[^(\n]*\((reviewer|fresh session|verifier)\)[^\n]*?Important open:\s*(\d+)(?:[^\n]*?report:\s*(\S+))?",
    re.IGNORECASE,
)
REVIEWED_AT = re.compile(r"· at ([0-9a-f]{7,40})\b")
RELEASE_DIGEST = re.compile(r"· sha256 ([0-9a-f]{12}|deleted)\b")
DELETED = "deleted"
VALIDATION_LINE = re.compile(r"· validation · (.*)$")
ANSWER = re.compile(r"\b(J\d+) (pass|fail|not judged)\b")
QUESTION_ID = re.compile(r"\*{0,2}(J\d+)\b")


# ------------------------------------------------------------------ parsers


def latest_review(log_text):
    """{"kind", "important", "report", "at"} of the Approval log's latest review line, or None ("at": the commit reviewed)."""
    found = [REVIEW_LINE.search(line) for line in flowlib.bullets(log_text)]
    found = [match for match in found if match]
    if not found:
        return None
    kind, important, report = found[-1].groups()
    reviewed_at = REVIEWED_AT.search(found[-1].string)
    return {"kind": kind.lower(), "important": int(important), "report": report,
            "at": reviewed_at.group(1) if reviewed_at else None}


def latest_validation(log_text):
    """{question ID: "pass" | "fail" | "not judged"} of the latest validation line, or None when there is none."""
    lines = [VALIDATION_LINE.search(line) for line in flowlib.bullets(log_text)]
    lines = [match for match in lines if match]
    if not lines:
        return None
    return dict(ANSWER.findall(lines[-1].group(1)))


def release_digest(log_text, path):
    """The content hash of the path's latest test-release line: "" when the line has none, None when there is no line."""
    starts = "test-release: %s" % path
    lines = [line for line in flowlib.bullets(log_text)
             if re.search(r"%s(\s|$)" % re.escape(starts), line)]
    if not lines:
        return None
    found = RELEASE_DIGEST.search(lines[-1])
    return found.group(1) if found else ""


def content_digest(root, path):
    """What a test-release line records for a file: its hash now, or "deleted"."""
    text = flowlib.read_worktree(root, path)
    return DELETED if text is None else flowlib.digest(text)


def questions_asked(validation_text):
    """The judgment IDs (J1, J2, ...) that validation.md §0 asks, in order."""
    asked = []
    for line in flowlib.bullets(flowlib.section(validation_text, "§0")):
        found = QUESTION_ID.match(line[2:].strip())
        if found and found.group(1) not in asked:
            asked.append(found.group(1))
    return asked


# ------------------------------------------------------------------ writing


def append_to_log(root, folder, entry):
    """Append `- <stamp> · <entry>` to the Approval log of the folder's validation.md; returns the line."""
    path = folder + "/validation.md"
    text = flowlib.read_worktree(root, path)
    if text is None:
        raise flowlib.FlowError("%s does not exist" % path)
    line = "- %s · %s" % (flowlib.now_stamp(), entry)

    def append(body):
        while body and not body[-1].strip():
            body.pop()
        return body + [line, ""]

    new_text = flowlib.edit_section(text, "Approval log", append, file_label=path)
    with open(os.path.join(root, path), "w", encoding="utf-8") as handle:
        handle.write(new_text)
    return line


def repo_path(root, given):
    """A path given on the command line, relative to the repository root."""
    absolute = given if os.path.isabs(given) else os.path.join(os.getcwd(), given)
    return os.path.relpath(os.path.realpath(absolute), os.path.realpath(root)).replace(os.sep, "/")


def review_entry(root, folder, arguments):
    report = repo_path(root, arguments.report)
    if not report.startswith(folder + "/"):
        raise flowlib.FlowError("the report has to be in the change folder (%s/%s/), not at %s" % (folder, flowlib.REPORTS, report))
    if not (flowlib.read_worktree(root, report) or "").strip():
        raise flowlib.FlowError("write the report to %s first; the line points to it" % report)
    uncommitted = flowlib.uncommitted_product_paths(root, flowlib.load_config(root))
    if uncommitted:
        raise flowlib.FlowError("commit the product changes first; the line records the commit reviewed (uncommitted: %s)"
                                % ", ".join(uncommitted[:5]))
    head = flowlib.git_out(["rev-parse", "--short", "HEAD"], cwd=root)
    return "review (%s) · Important open: %d · Nit: %d · at %s · report: %s" % (
        REVIEW_KINDS[arguments.by], arguments.important, arguments.nit, head, report)


def validation_entry(root, folder, arguments):
    asked = questions_asked(flowlib.read_worktree(root, folder + "/validation.md"))
    answers = dict(latest_validation(flowlib.approval_log(root, folder)) or {})
    for given in arguments.answers:
        question, _, answer = given.partition("=")
        if question not in asked:
            raise flowlib.FlowError("%s is not a question of validation.md §0 (it asks: %s)" % (question, ", ".join(asked) or "none"))
        if answer not in ANSWERS:
            raise flowlib.FlowError("%s: the answer is pass, fail or not-judged, not '%s'" % (question, answer))
        answers[question] = ANSWERS[answer]
    if not answers:
        return "validation · no judgment question"
    ordered = sorted(answers, key=lambda question: int(question[1:]))
    return "validation · " + " · ".join("%s %s" % (question, answers[question]) for question in ordered)


def test_release_entry(root, folder, arguments):
    path = repo_path(root, arguments.path)
    if not flowlib.matches(path, flowlib.load_config(root)["test_scope"]):
        raise flowlib.FlowError("%s is not in the project's test_scope; only a test file needs a release" % path)
    entry = "test-release: %s · sha256 %s — %s" % (path, content_digest(root, path), " ".join(arguments.why.split()))
    return entry + (" — §1 row %s" % arguments.row if arguments.row else "")


def ruling_entry(root, folder, arguments):
    return "ruling: %s · checked against: %s" % (" ".join(arguments.sentence.split()), " ".join(arguments.checked.split()))


ENTRY_BUILDERS = {"review": review_entry, "validation": validation_entry, "test-release": test_release_entry, "ruling": ruling_entry}


def parser():
    top = argparse.ArgumentParser(prog="record.py", description="Append one line to the change's Approval log.")
    kinds = top.add_subparsers(dest="kind")
    kinds.required = True
    review = kinds.add_parser("review")
    review.add_argument("--by", required=True, choices=sorted(REVIEW_KINDS))
    review.add_argument("--important", required=True, type=int)
    review.add_argument("--nit", required=True, type=int)
    review.add_argument("--report", required=True)
    validation = kinds.add_parser("validation")
    validation.add_argument("answers", nargs="*", metavar="J<n>=pass|fail|not-judged")
    release = kinds.add_parser("test-release")
    release.add_argument("path")
    release.add_argument("--why", required=True)
    release.add_argument("--row")
    ruling = kinds.add_parser("ruling")
    ruling.add_argument("sentence")
    ruling.add_argument("--checked", required=True)
    return top


def main():
    arguments = parser().parse_args()
    root = flowlib.repo_root()
    folder = flowlib.change_folder(root) if root else None
    if not folder or not flowlib.folder_exists(root, folder):
        print("REFUSED: run this on the working branch of a change")
        return 1
    try:
        line = append_to_log(root, folder, ENTRY_BUILDERS[arguments.kind](root, folder, arguments))
    except flowlib.FlowError as error:
        print("REFUSED: %s" % error)
        return 1
    print("recorded in %s/validation.md:\n%s" % (folder, line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
