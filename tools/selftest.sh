#!/usr/bin/env bash
# Self-test of the plugin's scripts and hooks: walks a project setup, one
# normal change and one small change through a throw-away Git repository, then
# a project with an origin and pull requests (a bare repository and a stand-in
# for the GitHub CLI), and checks every refusal, prompt and pass on the way.
# No model is called and nothing leaves this machine.
#
# Usage: bash tools/selftest.sh        (from the repository root; needs git and python3)
set -u
export PYTHONDONTWRITEBYTECODE=1   # leave no __pycache__ in the plugin
HERE="$(cd "$(dirname "$0")/.." && pwd)"
S="$HERE/plugin/scripts"
T="$HERE/plugin/templates"
WORK="$(mktemp -d)"
PASS=0; FAIL=0

ok()   { PASS=$((PASS+1)); echo "  ok   $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  FAIL $1"; echo "       got: $2"; }
# expect <label> <text> <substring that must be in it ("" = text must be empty)>
expect() {
  if [ -z "$3" ]; then [ -z "$2" ] && ok "$1" || bad "$1" "$2"
  else case "$2" in *"$3"*) ok "$1";; *) bad "$1" "$2";; esac; fi
}
hook_bash()  { python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]},"cwd":sys.argv[2]}))' "$1" "$PWD" | python3 "$S/hook_pretool_bash.py" 2>&1; }
hook_write() { python3 -c 'import json,sys; print(json.dumps({"tool_name":"Write","tool_input":{"file_path":sys.argv[1]},"cwd":sys.argv[2]}))' "$PWD/$1" "$PWD" | python3 "$S/hook_pretool_write.py" 2>&1; }
# hook_prompt <message> [agent id]: the owner (or, with an agent id, a subagent) submits a chat message
hook_prompt() { python3 -c 'import json,sys; d={"hook_event_name":"UserPromptSubmit","prompt":sys.argv[1],"cwd":sys.argv[2]}; d.update({"agent_id":sys.argv[3]} if len(sys.argv)>3 else {}); print(json.dumps(d))' "$1" "$PWD" ${2:+"$2"} | python3 "$S/hook_user_prompt.py" 2>&1; }
# hook_wakeup <prompt>: the session tries to schedule a prompt for itself
hook_wakeup() { python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PreToolUse","tool_name":"ScheduleWakeup","tool_input":{"delaySeconds":60,"prompt":sys.argv[1]},"cwd":sys.argv[2]}))' "$1" "$PWD" | python3 "$S/hook_user_prompt.py" 2>&1; }
commit() { git add -A >/dev/null && git commit -qm "$1"; }
log_line() { printf -- '- 2026-01-01 10:00 · %s\n' "$1" >> "$2"; }
on_branch() { git symbolic-ref --short -q HEAD; }
# quick_change <folder name> <product file>: a normal change taken to the point where it may be merged
quick_change() {
  local folder="specs/$1"
  git switch -q -c "$1" main && mkdir -p "$folder"
  sed 's/<title>/Quick change/' "$T/change/intent.md" > "$folder/intent.md" && commit "intent" && python3 "$S/accept.py" intent >/dev/null
  cp "$T/change/spec.md" "$T/change/validation.md" "$folder/" && commit "spec" && python3 "$S/accept.py" spec >/dev/null
  sed "s#\`<path>\`#\`src/$2.py\` \`tests/test_$2.py\`#" "$T/change/plan.md" > "$folder/plan.md" && commit "plan" && python3 "$S/accept.py" plan >/dev/null
  echo "def test_$2(): assert False" > "tests/test_$2.py" && echo "1 failed" > "$folder/red-run.txt" && commit "red tests"
  echo "$2 = 1" > "src/$2.py" && commit "implementation"
  log_line "review (fresh session) · Important open: 0 · Nit: 0" "$folder/validation.md" && commit "review"
}

echo "1. a directory that does not use the flow"
mkdir "$WORK/plain" && cd "$WORK/plain"
expect "bash hook silent outside a repository" "$(hook_bash 'git commit -m x')" ""
expect "write hook silent outside a repository" "$(hook_write 'a.py')" ""
expect "prompt hook silent outside a repository" "$(hook_prompt '接受 intent')" ""
expect "state --hook silent" "$(echo '{}' | python3 "$S/state.py" --hook)" ""

echo "2. project setup in a new repository"
mkdir "$WORK/repo" && cd "$WORK/repo"
git init -q -b main . && git config user.email t@example.com && git config user.name tester
git switch -q -c first-steps
expect "setup in a new repository needs the branch named setup" "$(python3 "$S/accept.py" setup)" "on a branch named \`setup\`"
git switch -q -c setup
mkdir -p specs .claude src tests references
cp "$T/project/mission.md" "$T/project/decisions.md" "$T/project/roadmap.md" specs/
cp "$T/project/CLAUDE.md" "$T/project/REVIEW.md" .
echo "what still holds of each mockup" > references/inventory.md
python3 - <<'EOF'
import json
json.dump({"test_scope": ["tests/**"], "deploys": False, "pull_request": False,
           "high_risk_paths": ["deploy/**"], "non_product_paths": ["notes/**", "references/**"]}, open(".claude/flow.json", "w"))
EOF
STATE="$(python3 "$S/state.py")"
expect "state: not set up" "$STATE" "NOT SET UP"
expect "state names the approval sentence" "$STATE" "接受立项"
expect "write hook does nothing before setup" "$(hook_write 'src/app.py')" ""
expect "accept refuses uncommitted setup files" "$(python3 "$S/accept.py" setup)" "commit these"
commit "setup files"
echo "scratch" > not-committed.txt
CHECK="$(python3 "$S/accept.py" setup --check)"
expect "setup --check lists a file that is not a project file" "$CHECK" "A  references/inventory.md"
expect "setup --check names what is not committed" "$CHECK" "not-committed.txt"
expect "setup --check changes nothing" "$(git rev-parse -q --verify refs/heads/main)" ""
rm not-committed.txt
expect "agent may not accept the setup" "$(hook_bash "python3 \"$S/accept.py\" setup")" "接受立项"
expect "agent may run accept --check" "$(hook_bash "python3 \"$S/accept.py\" setup --check")" '"allow"'
expect "a sentence with more words is an ordinary message" "$(hook_prompt '接受立项，但 mission 再改一句')" ""
expect "a sentence inside a subagent is not the owner's" "$(hook_prompt '接受立项' agent-1)" ""
expect "「接受立项」 creates main" "$(hook_prompt '接受立项。')" "main\` created"
expect "the checkout is on main" "$(on_branch)" "main"
expect "the setup branch is deleted" "$(git branch --list setup)" ""
expect "main carries the other file of the setup branch" "$(git show main:references/inventory.md)" "what still holds"
expect "state: set up" "$(python3 "$S/state.py")" "project: set up"

echo "2b. project setup where main already exists"
mkdir "$WORK/repo2" && cd "$WORK/repo2"
git init -q -b main . && git config user.email t@example.com && git config user.name tester
echo "old settings" > README.md && commit "repository init"
git switch -q -c setup
mkdir -p specs .claude references
cp "$T/project/mission.md" "$T/project/decisions.md" "$T/project/roadmap.md" specs/
cp "$T/project/flow.json" .claude/flow.json
echo "inventory" > references/inventory.md && commit "setup files"
OUT="$(python3 "$S/accept.py" setup)"
expect "accept setup moves main to the head of setup" "$OUT" "project setup accepted: \`main\` is at"
expect "…and lists the file that is not a project file" "$OUT" "A  references/inventory.md"
expect "main has the whole branch" "$(git show main:references/inventory.md)" "inventory"
expect "setup is deleted, checkout on main" "$(on_branch) $(git branch --list setup)" "main "
cd "$WORK/repo"

echo "3. a normal change"
F=specs/2026-01-01-contact
git switch -q -c 2026-01-01-contact main && mkdir -p $F
expect "product file denied without an intent" "$(hook_write 'src/app.py')" '"deny"'
sed 's/<title>/Contact phone/' "$T/change/intent.md" > $F/intent.md
expect "spec denied before intent accepted" "$(hook_write "$F/spec.md")" '"deny"'
DENY="$(hook_bash "python3 \"$S/accept.py\" intent")"
expect "agent may not run accept for a normal change" "$DENY" '"deny"'
expect "…the refusal names the owner's sentence" "$DENY" "接受 intent"
expect "「接受 intent」 refused while the draft is not committed" "$(hook_prompt '接受 intent')" "REFUSED"
commit "intent draft"
expect "state names the sentence for the intent" "$(python3 "$S/state.py")" "接受 intent"
expect "「接受 intent」 accepts the intent" "$(hook_prompt 'intent 接受')" "intent accepted"
expect "spec allowed after intent accepted" "$(hook_write "$F/spec.md")" ""
expect "plan denied before spec accepted" "$(hook_write "$F/plan.md")" '"deny"'
cp "$T/change/spec.md" $F/spec.md
sed 's/(R2)//' "$T/change/validation.md" > $F/validation.md
commit "spec draft"
expect "accept spec refused: R2 not covered" "$(hook_prompt '接受 spec')" "R2 is not cited"
cp "$T/change/validation.md" $F/validation.md && commit "validation covers R2"
expect "accept spec --check changes nothing" "$(python3 "$S/accept.py" spec --check)" "nothing was changed"
expect "accept spec" "$(python3 "$S/accept.py" spec)" "spec accepted"
expect "product file denied before plan approved" "$(hook_write 'src/app.py')" '"deny"'
sed 's#`<path>`#`src/app.py` `tests/test_app.py`#' "$T/change/plan.md" > $F/plan.md && commit "plan draft"
expect "「批准 plan」 approves the plan" "$(hook_prompt '批准 plan')" "plan approved"
expect "state: red run not committed" "$(python3 "$S/state.py")" "red run is not committed"
expect "test file free before the red commit" "$(hook_write 'tests/test_app.py')" ""
echo "def test_phone(): assert False" > tests/test_app.py && echo "1 failed" > $F/red-run.txt && commit "red tests"
expect "test file asks after the red commit" "$(hook_write 'tests/test_app.py')" '"ask"'
expect "product file allowed" "$(hook_write 'src/app.py')" ""
expect "non-product path allowed" "$(hook_write 'notes/today.md')" ""
echo "phone = '555'" > src/app.py && commit "implementation"
expect "close check: no review entry" "$(python3 "$S/close_check.py")" "no review entry"
log_line "review (fresh session) · Important open: 1 · Nit: 0" $F/validation.md
expect "close check: Important still open" "$(python3 "$S/close_check.py")" "still open"
log_line "review (fresh session) · Important open: 0 · Nit: 0" $F/validation.md
echo "def test_phone(): assert True" > tests/test_app.py
expect "close check: unreleased test change" "$(python3 "$S/close_check.py")" "has no 'test-release: tests/test_app.py'"
log_line "test-release: tests/test_app.py — the assertion was wrong — §1 row T1" $F/validation.md
echo "x = 1" > src/extra.py
expect "close check: file outside the plan" "$(python3 "$S/close_check.py")" "src/extra.py changed but is not in plan.md"
rm src/extra.py
sed -i.bak 's/^- None\.$/- **L1** footer year → roadmap: to do/' $F/validation.md && rm $F/validation.md.bak
expect "close check: leftover not in the roadmap" "$(python3 "$S/close_check.py")" "(2026-01-01-contact L1)"
expect "bash hook allows todo_add" "$(hook_bash "python3 \"$S/todo_add.py\" --who Leon \"footer year is wrong (2026-01-01-contact L1)\"")" '"allow"'
expect "todo_add commits to main" "$(python3 "$S/todo_add.py" --who Leon "footer year is wrong (2026-01-01-contact L1)")" "added to the roadmap"
expect "「确认合并」 refused while changes are uncommitted" "$(hook_prompt '确认合并')" "uncommitted changes"
commit "close"
expect "close check passes" "$(python3 "$S/close_check.py")" "all checks passed"
expect "state names the sentence for the merge" "$(python3 "$S/state.py")" "确认合并"
expect "agent may not merge a normal change" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
expect "agent may run merge --check" "$(hook_bash "python3 \"$S/merge.py\" --check")" '"allow"'
expect "「确认合并」 merges" "$(hook_prompt '确认合并')" "merged 2026-01-01-contact into \`main\`"
expect "main has the implementation" "$(git show main:src/app.py)" "555"
expect "after the merge the checkout is on main" "$(on_branch)" "main"
expect "after the merge the working branch is deleted" "$(git branch --list 2026-01-01-contact)" ""
expect "state: one to-do line" "$(python3 "$S/state.py")" "to do: 1 open line"
git switch -q -c 2026-01-01-contact main   # someone ends up on a branch that is already merged
expect "state: the branch is already merged" "$(python3 "$S/state.py")" "stage: Merged"
expect "merge --check on a merged branch" "$(python3 "$S/merge.py" --check)" "would only tidy up"
expect "merge on a merged branch only tidies up" "$(python3 "$S/merge.py")" "already in \`main\`"
expect "…and leaves the checkout on main" "$(on_branch) $(git branch --list 2026-01-01-contact)" "main "

echo "4. commands that move main, and prompts a session gives itself"
git switch -q -c scratch main
expect "commit on a branch: no decision" "$(hook_bash 'git commit -m x')" ""
expect "push a branch: no decision" "$(hook_bash 'git push origin 2026-01-01-contact')" ""
expect "new branch from main: no decision" "$(hook_bash 'git switch -c next main')" ""
expect "push main denied" "$(hook_bash 'git push origin main')" '"deny"'
expect "checkout main && merge denied" "$(hook_bash 'git checkout main && git merge next')" '"deny"'
expect "update-ref denied" "$(hook_bash 'git update-ref refs/heads/main HEAD')" '"deny"'
expect "branch -f main denied" "$(hook_bash 'git branch -f main HEAD')" '"deny"'
expect "chained owner script denied" "$(hook_bash "python3 \"$S/merge.py\" && echo done")" '"deny"'
expect "gh pr merge denied" "$(hook_bash 'gh pr merge 7 --merge')" '"deny"'
expect "gh pr view: no decision" "$(hook_bash 'gh pr view 7')" ""
expect "bash hook allows sync_main" "$(hook_bash "python3 \"$S/sync_main.py\"")" '"allow"'
expect "a scheduled prompt may not be an approval sentence" "$(hook_wakeup '确认合并')" '"deny"'
expect "an ordinary scheduled prompt: no decision" "$(hook_wakeup 'check the build')" ""
git switch -q main && git branch -q -D scratch
expect "commit on main denied" "$(hook_bash 'git commit -m x')" '"deny"'
expect "product file on main denied" "$(hook_write 'src/app.py')" '"deny"'

echo "5. a small change"
F=specs/2026-01-02-footer
git switch -q -c 2026-01-02-footer main && mkdir -p $F
sed 's/<title>/Footer year/' "$T/change/intent-small.md" > $F/intent.md && commit "small intent"
expect "product file denied before the click" "$(hook_write 'src/app.py')" '"deny"'
expect "accept intent asks" "$(hook_bash "python3 \"$S/accept.py\" intent")" '"ask"'
expect "accept intent (after the click)" "$(python3 "$S/accept.py" intent)" "intent accepted"
expect "product file allowed after the click" "$(hook_write 'src/app.py')" ""
expect "test file asks for the whole branch" "$(hook_write 'tests/test_app.py')" '"ask"'
expect "spec refused for a small change" "$(hook_write "$F/spec.md")" '"deny"'
cp "$T/change/validation-small.md" $F/validation.md
echo "year = 2026" >> src/app.py && mkdir -p deploy && echo "x" > deploy/site.yml && commit "small change"
log_line "review (verifier) · Important open: 0" $F/validation.md && commit "review"
expect "merge refused: high-risk path" "$(python3 "$S/merge.py")" "high-risk path"
expect "no merge prompt while the merge would be refused" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
git rm -q deploy/site.yml && commit "drop deploy change"
ASK="$(hook_bash "python3 \"$S/merge.py\"")"
expect "merge asks" "$ASK" '"ask"'
expect "merge prompt lists the changed files" "$ASK" "src/app.py"
expect "merge (after the click)" "$(python3 "$S/merge.py")" "merged 2026-01-02-footer"
expect "after the click the checkout is on main" "$(on_branch)" "main"
expect "state: small change not yet read" "$(python3 "$S/state.py")" "not yet read by a fresh session: 1"

echo "6. disposing of a to-do line"
expect "roadmap_edit asks and shows the line" "$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"footer year\" --reason dismissed")" "footer year is wrong"
expect "roadmap_edit deletes" "$(python3 "$S/roadmap_edit.py" delete --match "footer year" --reason dismissed)" "deleted (dismissed)"
expect "state: no open line" "$(python3 "$S/state.py")" "to do: no open line"

echo "7. a project with an origin: main is pushed and kept in step"
ORIGIN="$WORK/origin.git"
git init -q --bare -b main "$ORIGIN" && git remote add origin "$ORIGIN"
origin_main() { git --git-dir="$ORIGIN" rev-parse main; }
expect "sync_main pushes a main that origin does not have" "$(python3 "$S/sync_main.py")" "pushed \`main\` to origin"
expect "origin and local main are the same" "$(origin_main)" "$(git rev-parse main)"
git clone -q "$ORIGIN" "$WORK/other" && git -C "$WORK/other" config user.email k@example.com && git -C "$WORK/other" config user.name other
# a pull request merged on GitHub outside the flow (routine content): origin/main moves
(cd "$WORK/other" && mkdir -p content && echo "page" > content/page.md && git add -A && git commit -qm "content page" && git push -q origin main)
git fetch -q origin
expect "state: main is behind origin" "$(python3 "$S/state.py")" "behind origin/main"
expect "sync_main fast-forwards local main" "$(python3 "$S/sync_main.py")" "fast-forwarded to origin/main"
expect "local main has the content" "$(git show main:content/page.md)" "page"
expect "todo_add pushes main" "$(python3 "$S/todo_add.py" --who Leon "first line with an origin")" "pushed \`main\` to origin"
expect "origin has the to-do line" "$(git --git-dir="$ORIGIN" show main:specs/roadmap.md)" "first line with an origin"
# origin unreachable: the line is committed locally and said not to be pushed
git remote set-url origin "$WORK/nowhere.git"
expect "a failed push is reported, the commit stays" "$(python3 "$S/todo_add.py" --who Leon "line while offline")" "failed"
git remote set-url origin "$ORIGIN"
(cd "$WORK/other" && git pull -q origin main && echo "page 2" > content/page2.md && git add -A && git commit -qm "content page 2" && git push -q origin main)
expect "diverged mains are refused, not merged" "$(python3 "$S/sync_main.py")" "have diverged"
git pull -q --no-rebase origin main && git push -q origin main   # the owner, by hand, as the refusal says
expect "after the owner's pull the two are the same" "$(python3 "$S/sync_main.py")" "are both at"

echo "8. pull requests"
git switch -q -c pr-config main
python3 - <<'EOF'
import json
config = json.load(open(".claude/flow.json"))
config.update({"pull_request": True, "deploys": True})
json.dump(config, open(".claude/flow.json", "w"))
EOF
commit "merges go through pull requests; a merge publishes"
expect "accept setup on another branch commits the project files only" "$(python3 "$S/accept.py" setup)" "project setup (amended)"
git switch -q main && git branch -q -D pr-config
mkdir "$WORK/bin"
cat > "$WORK/bin/gh" <<'EOF'
#!/usr/bin/env bash
# Stand-in for the GitHub CLI. The "pull request" is a file holding its state;
# merging it merges the branch into main inside the bare origin, as GitHub would.
if [ "$1 $2" = "pr view" ]; then
  [ -f "$FAKE_PR" ] || { echo "no pull requests found for branch \"$3\"" >&2; exit 1; }
  printf '{"state":"%s","number":7,"url":"https://example.com/pull/7","headRefOid":"%s"}\n' "$(cat "$FAKE_PR")" "$(git --git-dir="$FAKE_ORIGIN" rev-parse "refs/heads/$3" 2>/dev/null)"
  exit 0
fi
if [ "$1 $2" = "pr merge" ]; then
  work="$(mktemp -d)" && git clone -q "$FAKE_ORIGIN" "$work/clone" && cd "$work/clone" || exit 1
  git config user.email g@example.com && git config user.name github
  git merge -q --no-ff "origin/$3" -m "Merge pull request #7" && git push -q origin main && echo MERGED > "$FAKE_PR"
  exit $?
fi
exit 2
EOF
chmod +x "$WORK/bin/gh"
export PATH="$WORK/bin:$PATH" FAKE_ORIGIN="$ORIGIN" FAKE_PR="$WORK/pull-request-state"
quick_change 2026-01-05-pr listing
expect "merge refused: no pull request yet" "$(python3 "$S/merge.py")" "no pull request found"
git push -q -u origin 2026-01-05-pr && echo CLOSED > "$FAKE_PR"
expect "merge refused: the pull request is closed" "$(python3 "$S/merge.py")" "is closed, not open"
echo OPEN > "$FAKE_PR"
git commit -q --allow-empty -m "one more commit, not pushed"
expect "merge refused: the pull request is not at the branch's head" "$(python3 "$S/merge.py")" "push the branch first"
git push -q origin 2026-01-05-pr
expect "merge --check passes with an open pull request" "$(python3 "$S/merge.py" --check)" "nothing refuses the merge of pull request #7"
expect "agent may not merge a normal change of a PR project" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
OUT="$(hook_prompt '确认合并')"
expect "「确认合并」 merges the pull request" "$OUT" "merged pull request #7 on GitHub"
expect "…says that the merge publishes" "$OUT" "the merge publishes"
expect "…deletes the branch on origin too" "$OUT" "origin/2026-01-05-pr is deleted too"
expect "local main is the pull request's merge" "$(git log -1 --format=%s main)" "Merge pull request #7"
expect "local main has the product file" "$(git show main:src/listing.py)" "listing = 1"
expect "the checkout is on main, the branch is gone" "$(on_branch) $(git branch --list 2026-01-05-pr)" "main "
expect "origin no longer has the branch" "$(git --git-dir="$ORIGIN" branch --list 2026-01-05-pr)" ""
# a pull request the owner merged on the page, by squash: Git cannot see the branch in main
rm "$FAKE_PR" && quick_change 2026-01-06-squash banner
git push -q -u origin 2026-01-06-squash
(cd "$WORK/other" && git pull -q origin main && git fetch -q origin && git merge -q --squash origin/2026-01-06-squash >/dev/null 2>&1 && git commit -qm "squashed pull request" && git push -q origin main)
echo MERGED > "$FAKE_PR"
OUT="$(python3 "$S/merge.py")"
expect "a pull request merged on the page is only tidied up" "$OUT" "already merged on GitHub"
expect "local main took in the squashed merge" "$(git show main:src/banner.py)" "banner = 1"
expect "the checkout is on main, the squashed branch is gone" "$(on_branch) $(git branch --list 2026-01-06-squash)" "main "
# a small change of a PR project still merges locally, and main is pushed
F=specs/2026-01-07-small
git switch -q -c 2026-01-07-small main && mkdir -p $F
sed 's/<title>/Footer month/' "$T/change/intent-small.md" > $F/intent.md && commit "small intent" && python3 "$S/accept.py" intent >/dev/null
cp "$T/change/validation-small.md" $F/validation.md && echo "month = 1" >> src/app.py && commit "small change"
log_line "review (verifier) · Important open: 0" $F/validation.md && commit "review"
expect "the merge prompt of a deploying project says so" "$(hook_bash "python3 \"$S/merge.py\"")" "Merging publishes to production"
OUT="$(python3 "$S/merge.py")"
expect "a small change merges locally" "$OUT" "merged 2026-01-07-small into \`main\`"
expect "…and main is pushed" "$OUT" "pushed \`main\` to origin"
expect "origin and local main are the same again" "$(origin_main)" "$(git rev-parse main)"

echo "9. a change in a worktree of its own (main stays checked out elsewhere)"
git worktree add -q "$WORK/stream" -b 2026-01-08-stream main && cd "$WORK/stream"
F=specs/2026-01-08-stream && mkdir -p $F
sed 's/<title>/Footer day/' "$T/change/intent-small.md" > $F/intent.md && commit "small intent" && python3 "$S/accept.py" intent >/dev/null
cp "$T/change/validation-small.md" $F/validation.md && echo "day = 1" >> src/app.py && commit "small change"
log_line "review (verifier) · Important open: 0" $F/validation.md && commit "review"
OUT="$(python3 "$S/merge.py")"
expect "a merge from a worktree moves main where it is checked out" "$OUT" "merged 2026-01-08-stream into \`main\`"
expect "…the branch stays, with what is left to do by hand" "$OUT" "this checkout stays on 2026-01-08-stream"
cd "$WORK/repo"
expect "the checkout of main has the change" "$(grep -c 'day = 1' src/app.py)" "1"

cd "$HERE" && rm -rf "$WORK"
echo
echo "selftest: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
