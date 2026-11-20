"""Shared helpers for the flow plugin's scripts and hooks.

Standard library only, Python 3.9+. Every script in this directory imports
from here, so the rules that several of them need (where the approval record
is read, how the tier is found, how the plan approval is marked, how a commit
reaches `main`) exist once.
"""

import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime

# The reports and the refusals carry non-ASCII text (the owner's sentences, "·", "—").
# Say so explicitly instead of depending on the locale a hook happens to run under.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

MAIN = "main"
SPECS = "specs"
CONFIG_PATH = ".claude/flow.json"
SETUP_FILES = ["specs/mission.md", "specs/decisions.md", "specs/roadmap.md"]
ROADMAP = "specs/roadmap.md"
# Paths the presence check never guards, in every project.
BUILT_IN_NON_PRODUCT = ["specs/**", "CLAUDE.md"]
REQUIRED_CONFIG_KEYS = ["test_scope", "deploys", "pull_request"]
TIERS = ("small", "normal", "high-risk")
# Inside a change folder: the file that marks the plan as approved (written only
# by the plan approval — see record_plan_approval), and the folder the
# subagents' reports are written to.
PLAN_MARK = "plan-approved.txt"
REPORTS = "reports"
# Seconds a git command that talks to origin may take before it counts as failed.
# Basis: such a command normally answers within a few seconds; the approval hook
# gives a whole script 100 seconds (hook_user_prompt.py), and a merge makes up
# to four of these calls — so a hanging network must not use up more than 20 each.
NETWORK_TIMEOUT = 20

# The owner's approval sentences. Typed alone as a whole chat message, one of
# these makes the UserPromptSubmit hook run the matching script — no terminal.
# The first sentence of each list is the one the reports and the skills show.
# "intent" is a small change's sentence only: a normal or high-risk intent is
# accepted together with its spec and validation, by "spec". "plan" is the
# fallback for a plan approval that left no mark in plan mode.
OWNER_SENTENCES = {
    "setup": ["接受立项", "立项接受", "accept setup", "accept the setup"],
    "intent": ["接受 intent", "intent 接受", "accept intent", "accept the intent"],
    "spec": ["接受 spec", "spec 接受", "accept spec", "accept the spec"],
    "plan": ["批准 plan", "plan 批准", "approve plan", "approve the plan"],
    "merge": ["确认合并", "合并确认", "confirm merge", "confirm the merge"],
}


class FlowError(Exception):
    """A refusal with a sentence the person (or Claude) can act on."""


# ---------------------------------------------------------------- git basics


def git(args, cwd=None, env=None, stdin_text=None, timeout=None):
    """Run git and return the CompletedProcess; never raises on a non-zero exit or a timeout."""
    try:
        return subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            env=env,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 127, "", "git is not installed")
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 124, "", "git %s did not answer within %s seconds" % (args[0], timeout))


def git_out(args, cwd=None, env=None):
    """Stdout of a git command, stripped; an empty string when the command fails."""
    result = git(args, cwd=cwd, env=env)
    return result.stdout.strip() if result.returncode == 0 else ""


def git_must(args, cwd=None, env=None, stdin_text=None):
    """Stdout of a git command that has to succeed; raises FlowError otherwise."""
    result = git(args, cwd=cwd, env=env, stdin_text=stdin_text)
    if result.returncode != 0:
        raise FlowError("git %s failed: %s" % (" ".join(args), result.stderr.strip()))
    return result.stdout.strip()


def repo_root(start_dir=None):
    """Top level of the checkout that contains start_dir (a worktree counts as its own top level)."""
    start_dir = start_dir or os.getcwd()
    top = git_out(["rev-parse", "--show-toplevel"], cwd=start_dir)
    return top or None


def current_branch(root):
    return git_out(["symbolic-ref", "--short", "-q", "HEAD"], cwd=root) or None


def main_exists(root):
    return git(["rev-parse", "-q", "--verify", "refs/heads/" + MAIN], cwd=root).returncode == 0


def on_main(root, path):
    """True when the file exists in the committed tree of `main` — the approval record."""
    return git(["cat-file", "-e", "%s:%s" % (MAIN, path)], cwd=root).returncode == 0


def read_main(root, path):
    result = git(["show", "%s:%s" % (MAIN, path)], cwd=root)
    return result.stdout if result.returncode == 0 else None


def read_head(root, path):
    result = git(["show", "HEAD:%s" % path], cwd=root)
    return result.stdout if result.returncode == 0 else None


def read_worktree(root, path):
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return None
    with open(full, encoding="utf-8") as handle:
        return handle.read()


def main_worktree(root):
    """Path of the checkout that has `main` checked out, or None."""
    listing = git_out(["worktree", "list", "--porcelain"], cwd=root)
    path = None
    for line in listing.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):]
        elif line == "branch refs/heads/" + MAIN:
            return path
    return None


def merge_base(root):
    return git_out(["merge-base", MAIN, "HEAD"], cwd=root) or None


def is_ancestor(root, older, newer):
    """True when the commit `older` is contained in `newer` (or is the same commit)."""
    return git(["merge-base", "--is-ancestor", older, newer], cwd=root).returncode == 0


# ------------------------------------------------- the owner's sentences


def squeeze(text):
    """Lower case, without spaces and punctuation — how a typed sentence is compared."""
    return re.sub(r"[\W_]+", "", (text or "").lower())


def owner_act(text):
    """The approval a text stands for — only when the whole text is one of the owner's sentences."""
    squeezed = squeeze(text)
    if not squeezed:
        return None
    for act, sentences in OWNER_SENTENCES.items():
        if squeezed in [squeeze(sentence) for sentence in sentences]:
            return act
    return None


def owner_sentence(act):
    return OWNER_SENTENCES[act][0]


def owner_route(act):
    """How the owner gives this approval: the sentence in the chat, or the line for his terminal."""
    line = script_line("merge") if act == "merge" else script_line("accept", act)
    return "the owner types「%s」in the chat as a message of its own (or runs `%s` in his own terminal)" % (owner_sentence(act), line)


# ------------------------------------------------------- `main` and origin
#
# Where the repository has an `origin`, local `main` and origin/main are kept
# the same: every script that moves `main` first takes in what origin has
# (a fast-forward only) and pushes afterwards. Without that, a pull request
# merged on GitHub and a line committed locally would leave two diverged
# `main`s that only a hand-made merge in a terminal could join.


def has_origin(root):
    return bool(git_out(["remote", "get-url", "origin"], cwd=root))


def origin_main(root):
    """The commit of origin/main as last fetched, or None."""
    return git_out(["rev-parse", "-q", "--verify", "refs/remotes/origin/" + MAIN], cwd=root) or None


def move_main(root, target):
    """Fast-forward local `main` to the commit `target`, wherever `main` is checked out."""
    old = git_must(["rev-parse", MAIN], cwd=root)
    if old == target:
        return
    if not is_ancestor(root, old, target):
        raise FlowError("`main` (%s) cannot be fast-forwarded to %s" % (old[:7], target[:7]))
    checkout = main_worktree(root)
    if checkout:
        if git_out(["status", "--porcelain", "--untracked-files=no"], cwd=checkout):
            raise FlowError("`main` is checked out at %s with uncommitted changes; commit or stash them first" % checkout)
        git_must(["merge", "--ff-only", "-q", target], cwd=checkout)
    else:
        git_must(["update-ref", "refs/heads/" + MAIN, target, old], cwd=root)


def sync_main(root):
    """Take into local `main` what origin/main has — a fast-forward, never a merge.

    Returns a sentence to print, or None when there was nothing to do (no
    origin, already the same, or local `main` is ahead and the next push
    carries it). Raises FlowError when the two have diverged.
    """
    if not has_origin(root) or not main_exists(root):
        return None
    fetched = git(["fetch", "-q", "origin", MAIN], cwd=root, timeout=NETWORK_TIMEOUT)
    remote = origin_main(root)
    if fetched.returncode != 0:
        if remote is None:
            return None  # origin has no `main` yet: the first push creates it
        reason = (fetched.stderr.strip().splitlines() or ["no reason given"])[-1]
        return "NOTE: could not fetch origin/main (%s); working from the local `main`" % reason
    local = git_must(["rev-parse", MAIN], cwd=root)
    if remote is None or remote == local or is_ancestor(root, remote, local):
        return None
    if is_ancestor(root, local, remote):
        move_main(root, remote)
        return "`main` fast-forwarded to origin/main (%s)" % remote[:7]
    raise FlowError(
        "local `main` and origin/main have diverged, and the flow only fast-forwards. "
        "In your own terminal: `git switch main && git pull --no-rebase && git push`, then repeat this step"
    )


def push_main(root):
    """Push `main` to origin where there is one. Returns (succeeded, sentence to print or None)."""
    if not has_origin(root):
        return True, None
    pushed = git(["push", "-q", "origin", MAIN], cwd=root, timeout=NETWORK_TIMEOUT)
    if pushed.returncode != 0:
        return False, "NOTE: `git push origin main` failed — origin does not have this yet; the next step that moves `main` pushes it again:\n%s" % pushed.stderr.strip()
    return True, "pushed `main` to origin"


def leave_branch(root, branch, force=False):
    """After a merge: switch this checkout to `main` and delete the working branch.

    Returns the sentences to print. Never raises — the merge has happened;
    a tidy-up that cannot finish says what is left to do by hand.
    The branch is deleted only when `main` contains it. force=True is for a
    branch GitHub merged by squash or rebase: Git cannot see that it is
    merged, the pull request's state says so.
    """
    by_hand = "when convenient: `git switch %s` and `git branch -D %s`" % (MAIN, branch)
    if not (force or is_ancestor(root, branch, MAIN)):
        return ["NOTE: `main` does not contain %s; the branch is left as it is" % branch]
    if current_branch(root) == branch:
        switched = git(["switch", "-q", MAIN], cwd=root)
        if switched.returncode != 0:
            reason = (switched.stderr.strip().splitlines() or ["no reason given"])[-1]
            return ["NOTE: this checkout stays on %s (%s); %s" % (branch, reason, by_hand)]
    # -D on purpose: "is it merged" was answered above against `main`; -d would ask the branch's upstream instead.
    deleted = git(["branch", "-D", branch], cwd=root)
    if deleted.returncode != 0:
        return ["NOTE: the branch %s was not deleted (%s); %s" % (branch, deleted.stderr.strip(), by_hand)]
    lines = ["this checkout is on `%s`; the branch %s is deleted" % (MAIN, branch)]
    if has_origin(root):
        listed = git(["ls-remote", "--exit-code", "--heads", "origin", branch], cwd=root, timeout=NETWORK_TIMEOUT)
        if listed.returncode == 0:
            removed = git(["push", "-q", "origin", "--delete", branch], cwd=root, timeout=NETWORK_TIMEOUT)
            if removed.returncode == 0:
                lines.append("origin/%s is deleted too" % branch)
            else:
                lines.append("NOTE: origin/%s was not deleted: %s" % (branch, removed.stderr.strip()))
    return lines


# ------------------------------------------------------------ project config


def load_config(root):
    """The project's .claude/flow.json, or None when the repository does not use the flow."""
    text = read_worktree(root, CONFIG_PATH) if root else None
    if text is None:
        return None
    try:
        config = json.loads(text)
    except ValueError as error:
        raise FlowError("%s is not valid JSON: %s" % (CONFIG_PATH, error))
    missing = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing:
        raise FlowError("%s is missing: %s" % (CONFIG_PATH, ", ".join(missing)))
    config.setdefault("high_risk_paths", [])
    config.setdefault("non_product_paths", [])
    return config


def literal_brackets(pattern):
    """The pattern with `[` and `]` made literal for fnmatch.

    Some frameworks put square brackets in file names (`pages/[slug].astro`);
    read as a character class, such a path would never match itself.
    """
    return re.sub(r"[\[\]]", lambda found: "[%s]" % found.group(0), pattern)


def matches(path, patterns):
    """Glob match on a repo-relative path; `*` and `**` both cross directory separators, brackets are literal."""
    path = path.replace(os.sep, "/")
    return any(fnmatch.fnmatch(path, literal_brackets(pattern)) for pattern in patterns)


def is_non_product(path, config):
    return matches(path, BUILT_IN_NON_PRODUCT + list(config.get("non_product_paths", [])))


def is_setup(root):
    return main_exists(root) and all(on_main(root, path) for path in SETUP_FILES)


# ------------------------------------------------------------- change folder


def change_folder(root, branch=None):
    """`specs/<branch>` — the working branch is named after its change folder."""
    branch = branch or current_branch(root)
    if not branch or branch == MAIN:
        return None
    return "%s/%s" % (SPECS, branch)


def folder_exists(root, folder):
    return bool(folder) and (
        os.path.isdir(os.path.join(root, folder)) or on_main(root, folder + "/intent.md")
    )


def read_tier(text):
    if not text:
        return None
    found = re.search(r"^Tier:\s*(small|normal|high-risk)\b", text, re.IGNORECASE | re.MULTILINE)
    return found.group(1).lower() if found else None


def tier_of(root, folder):
    """Tier of a change: the accepted intent on `main` wins over the draft in the working tree."""
    text = read_main(root, folder + "/intent.md")
    if text is None:
        text = read_worktree(root, folder + "/intent.md")
    return read_tier(text)


def red_committed(root, folder):
    """The red run is committed when red-run.txt is in the branch's HEAD — no flag file."""
    return git(["cat-file", "-e", "HEAD:%s/red-run.txt" % folder], cwd=root).returncode == 0


def red_commit(root, folder):
    """The commit that added red-run.txt (the start of the test-file lock)."""
    return git_out(
        ["log", "--diff-filter=A", "--format=%H", "-1", "--", folder + "/red-run.txt"], cwd=root
    ) or None


# ------------------------------------------------------------ plan approval
#
# The plan is approved when the owner accepts it in plan mode (the PostToolUse
# hook of ExitPlanMode), or, as a fallback, by「批准 plan」. Either way the
# approval is a mark file in the change folder, committed on the working
# branch; `main` does not move. The Edit/Write hook refuses to write the mark,
# so only these two routes create it.


def plan_mark(folder):
    return "%s/%s" % (folder, PLAN_MARK)


def plan_approved(root, folder):
    return read_worktree(root, plan_mark(folder)) is not None


def plan_approval_refusal(root, folder):
    """Why a plan cannot be approved for this folder now, or None when it can."""
    if not folder or not folder_exists(root, folder):
        return "this branch has no change folder"
    tier = tier_of(root, folder)
    if tier not in ("normal", "high-risk"):
        return "%s/intent.md is not a normal or high-risk intent (a small change has no plan)" % folder
    if not (on_main(root, folder + "/spec.md") and on_main(root, folder + "/validation.md")):
        return "the spec is not accepted yet — 「%s」 comes before the plan" % owner_sentence("spec")
    if plan_approved(root, folder):
        return "the plan is already approved (%s)" % read_worktree(root, plan_mark(folder)).strip()
    return None


def record_plan_approval(root, folder, how, plan_text=None):
    """Write the mark (and plan.md, when the approved text is given) and commit the two on the branch.

    Returns the sentences to print. The mark counts once it is in the working
    tree; a commit that fails is reported, not raised.
    """
    plan_path = folder + "/plan.md"
    if plan_text is not None:
        with open(os.path.join(root, plan_path), "w", encoding="utf-8") as handle:
            handle.write(plan_text if plan_text.endswith("\n") else plan_text + "\n")
    with open(os.path.join(root, plan_mark(folder)), "w", encoding="utf-8") as handle:
        handle.write("plan approved · %s · %s · plan.md sha256 %s\n" % (how, now_stamp(), digest(read_worktree(root, plan_path) or "")))
    paths = [plan_path, plan_mark(folder)]
    git(["add", "--"] + paths, cwd=root)
    committed = git(["commit", "-q", "-m", "plan approved: %s" % folder.rsplit("/", 1)[-1], "--"] + paths, cwd=root)
    lines = ["plan approved (%s): %s and %s" % (how, plan_path, plan_mark(folder))]
    if committed.returncode == 0:
        lines.append("committed on the working branch (%s); `main` does not move" % git_out(["rev-parse", "--short", "HEAD"], cwd=root))
    else:
        lines.append("NOTE: written but not committed (%s); commit the two files with the next commit" % committed.stderr.strip())
    return lines


# ------------------------------------------------------------ markdown parts


def section(text, heading_start):
    """Body of the `## ` section whose title starts with heading_start (case-insensitive)."""
    if not text:
        return None
    # Template comments carry example lines; they are never content.
    lines = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).splitlines()
    body, inside = [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            title = line[3:].strip().lower()
            inside = title.startswith(heading_start.lower())
            continue
        if inside:
            body.append(line)
    return "\n".join(body) if inside or body else None


def has_heading(text, heading_start, level="## "):
    for line in (text or "").splitlines():
        if line.startswith(level) and line[len(level):].strip().lower().startswith(heading_start.lower()):
            return True
    return False


def approval_log(root, folder):
    """Approval log of the change as it stands in the working tree."""
    return section(read_worktree(root, folder + "/validation.md"), "Approval log") or ""


def bullets(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip().startswith("- ")]


# ------------------------------------------------------------------- roadmap


TODO_LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · ")


def roadmap_on_main(root):
    return read_main(root, ROADMAP)


def todo_lines(roadmap_text):
    return [line for line in bullets(section(roadmap_text, "To do")) if TODO_LINE.match(line)]


def edit_section(text, heading_start, edit, file_label=ROADMAP):
    """Apply edit(list_of_lines) -> list_of_lines to one `## ` section and return the new text."""
    lines = text.splitlines()
    start = end = None
    for index, line in enumerate(lines):
        if line.startswith("## "):
            if start is not None:
                end = index
                break
            if line[3:].strip().lower().startswith(heading_start.lower()):
                start = index + 1
    if start is None:
        raise FlowError("%s has no '## %s' section" % (file_label, heading_start))
    if end is None:
        end = len(lines)
    body = edit(lines[start:end])
    return "\n".join(lines[:start] + body + lines[end:]) + "\n"


# ------------------------------------------------------- committing to main


def commit_to_main(root, changes, message):
    """Commit {path: text} onto `main` without checking it out.

    This is the one mechanism by which a script moves `main` for a file-level
    commit (an approval record, a to-do line). It builds the new tree in a
    temporary index, so the working tree of the current branch is untouched.
    If `main` is checked out in some worktree, that worktree has to be clean
    and is brought to the new commit afterwards. Where there is an origin,
    `main` first takes in what origin has and is pushed afterwards (the
    sentences about that are printed here).
    """
    note = sync_main(root)
    if note:
        print(note)
    parent = git_out(["rev-parse", "-q", "--verify", "refs/heads/" + MAIN], cwd=root) or None
    checkout = main_worktree(root)
    if checkout and git_out(["status", "--porcelain", "--untracked-files=no"], cwd=checkout):
        raise FlowError(
            "`main` is checked out at %s with uncommitted changes; commit or stash them first" % checkout
        )
    handle, index_path = tempfile.mkstemp(prefix="flow-index-")
    os.close(handle)
    os.remove(index_path)
    env = dict(os.environ, GIT_INDEX_FILE=index_path)
    try:
        if parent:
            git_must(["read-tree", parent], cwd=root, env=env)
        for path, text in changes.items():
            blob = git_must(["hash-object", "-w", "--stdin"], cwd=root, stdin_text=text)
            git_must(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, path)], cwd=root, env=env)
        tree = git_must(["write-tree"], cwd=root, env=env)
    finally:
        if os.path.exists(index_path):
            os.remove(index_path)
    if parent and tree == git_out(["rev-parse", parent + "^{tree}"], cwd=root):
        return None  # nothing differs from main
    commit_args = ["commit-tree", tree, "-m", message]
    if parent:
        commit_args += ["-p", parent]
    commit = git_must(commit_args, cwd=root)
    update_args = ["update-ref", "refs/heads/" + MAIN, commit]
    if parent:
        update_args.append(parent)
    git_must(update_args, cwd=root)
    if checkout:
        git_must(["reset", "--hard", "-q", MAIN], cwd=checkout)
    note = push_main(root)[1]
    if note:
        print(note)
    return commit


# --------------------------------------------------------------------- misc


def digest(text):
    """First 12 hex digits of the text's sha256: enough to tell two versions of a file apart."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def uncommitted_product_paths(root, config):
    """Product files with changes not committed yet (tracked or untracked)."""
    paths = []
    # Not git_out: its strip would eat the status column of the first line.
    for line in git(["status", "--porcelain", "--untracked-files=all"], cwd=root).stdout.splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        if path and not is_non_product(path, config):
            paths.append(path)
    return paths


def now_stamp():
    """Local date and time with the zone name, e.g. `2026-11-15 21:40 EST`."""
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def today():
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def scripts_dir():
    return os.path.dirname(os.path.realpath(__file__))


def script_line(name, *arguments):
    """One pasteable line that runs a script of this plugin."""
    parts = ['python3 "%s"' % os.path.join(scripts_dir(), name + ".py")] + list(arguments)
    return " ".join(parts)
