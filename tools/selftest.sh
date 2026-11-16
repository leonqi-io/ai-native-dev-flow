#!/usr/bin/env bash
# Self-test of the plugin's scripts and hooks: walks one normal change and one
# small change through a throw-away Git repository and checks every refusal,
# prompt and pass on the way. No model is called.
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
commit() { git add -A >/dev/null && git commit -qm "$1"; }
log_line() { printf -- '- 2026-01-01 10:00 · %s\n' "$1" >> "$2"; }

echo "1. a directory that does not use the flow"
mkdir "$WORK/plain" && cd "$WORK/plain"
expect "bash hook silent outside a repository" "$(hook_bash 'git commit -m x')" ""
expect "write hook silent outside a repository" "$(hook_write 'a.py')" ""
expect "state --hook silent" "$(echo '{}' | python3 "$S/state.py" --hook)" ""

echo "2. project setup"
mkdir "$WORK/repo" && cd "$WORK/repo"
git init -q -b main . && git config user.email t@example.com && git config user.name tester
git switch -q -c setup
mkdir -p specs .claude src tests
cp "$T/project/mission.md" "$T/project/tech-stack.md" "$T/project/roadmap.md" specs/
cp "$T/project/CLAUDE.md" "$T/project/REVIEW.md" .
python3 - <<'EOF'
import json
json.dump({"test_scope": ["tests/**"], "deploys": False, "pull_request": False,
           "high_risk_paths": ["deploy/**"], "non_product_paths": ["notes/**"]}, open(".claude/flow.json", "w"))
EOF
expect "state: not set up" "$(python3 "$S/state.py")" "NOT SET UP"
expect "write hook does nothing before setup" "$(hook_write 'src/app.py')" ""
expect "accept refuses uncommitted setup files" "$(python3 "$S/accept.py" setup)" "commit these"
commit "setup files"
expect "accept setup creates main" "$(python3 "$S/accept.py" setup)" "main\` created"
expect "state: set up" "$(python3 "$S/state.py")" "project: set up"

echo "3. a normal change"
F=specs/2026-01-01-contact
git switch -q -c 2026-01-01-contact main && mkdir -p $F
expect "product file denied without an intent" "$(hook_write 'src/app.py')" '"deny"'
sed 's/<title>/Contact phone/' "$T/change/intent.md" > $F/intent.md
expect "spec denied before intent accepted" "$(hook_write "$F/spec.md")" '"deny"'
expect "agent may not run accept for a normal change" "$(hook_bash "python3 \"$S/accept.py\" intent")" '"deny"'
commit "intent draft"
expect "accept intent" "$(python3 "$S/accept.py" intent)" "intent accepted"
expect "spec allowed after intent accepted" "$(hook_write "$F/spec.md")" ""
expect "plan denied before spec accepted" "$(hook_write "$F/plan.md")" '"deny"'
cp "$T/change/spec.md" $F/spec.md
sed 's/(R2)//' "$T/change/validation.md" > $F/validation.md
commit "spec draft"
expect "accept spec refused: R2 not covered" "$(python3 "$S/accept.py" spec)" "R2 is not cited"
cp "$T/change/validation.md" $F/validation.md && commit "validation covers R2"
expect "accept spec" "$(python3 "$S/accept.py" spec)" "spec accepted"
expect "product file denied before plan approved" "$(hook_write 'src/app.py')" '"deny"'
sed 's#`<path>`#`src/app.py` `tests/test_app.py`#' "$T/change/plan.md" > $F/plan.md && commit "plan draft"
expect "accept plan" "$(python3 "$S/accept.py" plan)" "plan approved"
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
commit "close"
expect "close check passes" "$(python3 "$S/close_check.py")" "all checks passed"
expect "agent may not merge a normal change" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
expect "merge" "$(python3 "$S/merge.py")" "merged 2026-01-01-contact into \`main\`"
expect "main has the implementation" "$(git show main:src/app.py)" "555"
expect "state: one to-do line" "$(python3 "$S/state.py")" "to do: 1 open line"

echo "4. git commands that move main"
expect "commit on a branch: no decision" "$(hook_bash 'git commit -m x')" ""
expect "push a branch: no decision" "$(hook_bash 'git push origin 2026-01-01-contact')" ""
expect "new branch from main: no decision" "$(hook_bash 'git switch -c next main')" ""
expect "push main denied" "$(hook_bash 'git push origin main')" '"deny"'
expect "checkout main && merge denied" "$(hook_bash 'git checkout main && git merge next')" '"deny"'
expect "update-ref denied" "$(hook_bash 'git update-ref refs/heads/main HEAD')" '"deny"'
expect "branch -f main denied" "$(hook_bash 'git branch -f main HEAD')" '"deny"'
expect "chained owner script denied" "$(hook_bash "python3 \"$S/merge.py\" && echo done")" '"deny"'
git switch -q main
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
git switch -q main
expect "state: small change not yet read" "$(python3 "$S/state.py")" "not yet read by a fresh session: 1"

echo "6. disposing of a to-do line"
expect "roadmap_edit asks and shows the line" "$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"footer year\" --reason dismissed")" "footer year is wrong"
expect "roadmap_edit deletes" "$(python3 "$S/roadmap_edit.py" delete --match "footer year" --reason dismissed)" "deleted (dismissed)"
expect "state: no open line" "$(python3 "$S/state.py")" "to do: no open line"

cd "$HERE" && rm -rf "$WORK"
echo
echo "selftest: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
