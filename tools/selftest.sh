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
# hook_plan <plan text>: the owner accepts a plan in plan mode (PostToolUse of ExitPlanMode, the plan text in the response)
hook_plan() { python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PostToolUse","tool_name":"ExitPlanMode","tool_input":{},"tool_response":{"plan":sys.argv[1],"filePath":"/nowhere/plan.md"},"cwd":sys.argv[2]}))' "$1" "$PWD" | python3 "$S/hook_plan_approved.py" 2>&1; }
# hook_plan_file <path>: the same, with only the file plan mode wrote the plan to
# hook_plan_in_subagent <plan text>: the same tool call, made inside a subagent
hook_plan_in_subagent() { python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PostToolUse","tool_name":"ExitPlanMode","agent_id":"a1","agent_type":"Plan","tool_input":{},"tool_response":{"plan":sys.argv[1]},"cwd":sys.argv[2]}))' "$1" "$PWD" | python3 "$S/hook_plan_approved.py" 2>&1; }
hook_plan_file() { python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PostToolUse","tool_name":"ExitPlanMode","tool_input":{},"tool_response":{"filePath":sys.argv[1]},"cwd":sys.argv[2]}))' "$1" "$PWD" | python3 "$S/hook_plan_approved.py" 2>&1; }
# hook_edit <file> <old text> <new text>: the session edits a file in place
hook_edit() { python3 -c 'import json,sys; print(json.dumps({"tool_name":"Edit","tool_input":{"file_path":sys.argv[1],"old_string":sys.argv[2],"new_string":sys.argv[3]},"cwd":sys.argv[4]}))' "$PWD/$1" "$2" "$3" "$PWD" | python3 "$S/hook_pretool_write.py" 2>&1; }
commit() { git add -A >/dev/null && git commit -qm "$1"; }
log_line() { printf -- '- 2026-01-01 10:00 · %s\n' "$1" >> "$2"; }
on_branch() { git symbolic-ref --short -q HEAD; }
# quick_change <folder name> <product file> [sentence]: a normal change taken to the point where it may be merged;
# the plan is approved in plan mode, or with「批准 plan」when the third argument is "sentence"
quick_change() {
  local folder="specs/$1"
  git switch -q -c "$1" main && mkdir -p "$folder"
  sed 's/<title>/Quick change/' "$T/change/intent.md" > "$folder/intent.md"
  cp "$T/change/spec.md" "$T/change/validation.md" "$folder/" && commit "intent, spec, validation" && python3 "$S/accept.py" spec >/dev/null
  sed "s#\`<path>\`#\`src/$2.py\` \`tests/test_$2.py\`#" "$T/change/plan.md" > "$WORK/plan-$2.md"
  if [ "${3:-}" = sentence ]; then
    cp "$WORK/plan-$2.md" "$folder/plan.md"
    expect "「批准 plan」 refused while plan.md is not committed" "$(hook_prompt '批准 plan')" "uncommitted changes"
    commit "plan" && expect "accept plan --check" "$(python3 "$S/accept.py" plan --check)" "nothing refuses"
    hook_prompt '批准 plan' >/dev/null
  else
    hook_plan_file "$WORK/plan-$2.md" >/dev/null
  fi
  echo "def test_$2(): assert False" > "tests/test_$2.py" && echo "1 failed" > "$folder/red-run.txt" && commit "red tests"
  echo "$2 = 1" > "src/$2.py" && commit "implementation"
  mkdir -p "$folder/reports" && echo "No findings." > "$folder/reports/review.md"
  python3 "$S/record.py" review --by reviewer --important 0 --nit 0 --report "$folder/reports/review.md" >/dev/null
  python3 "$S/record.py" validation J1=pass >/dev/null && commit "review and validation"
}

echo "1. a directory that does not use the flow"
mkdir "$WORK/plain" && cd "$WORK/plain"
expect "bash hook silent outside a repository" "$(hook_bash 'git commit -m x')" ""
expect "write hook silent outside a repository" "$(hook_write 'a.py')" ""
expect "prompt hook silent outside a repository" "$(hook_prompt '接受 intent')" ""
expect "plan hook silent outside a repository" "$(hook_plan 'a plan')" ""
expect "state --hook silent" "$(echo '{}' | python3 "$S/state.py" --hook)" ""

expect "hooks.json runs the plan hook after ExitPlanMode" "$(python3 -c 'import json,sys; h=json.load(open(sys.argv[1]))["hooks"]["PostToolUse"]; print([e["matcher"]+" "+e["hooks"][0]["args"][0] for e in h])' "$HERE/plugin/hooks/hooks.json")" "ExitPlanMode \${CLAUDE_PLUGIN_ROOT}/scripts/hook_plan_approved.py"

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
expect "spec denied before the intent is written" "$(hook_write "$F/spec.md")" '"deny"'
sed 's/<title>/Contact phone/' "$T/change/intent.md" > $F/intent.md
expect "spec allowed once the intent carries its tier" "$(hook_write "$F/spec.md")" ""
expect "plan denied before spec accepted" "$(hook_write "$F/plan.md")" '"deny"'
commit "intent draft"
OUT="$(hook_prompt '接受 intent')"
expect "「接受 intent」 is retired for a normal change" "$OUT" "REFUSED"
expect "…the refusal names「接受 spec」" "$OUT" "接受 spec"
DENY="$(hook_bash "python3 \"$S/accept.py\" spec")"
expect "agent may not run accept for a normal change" "$DENY" '"deny"'
expect "…the refusal names the owner's sentence" "$DENY" "接受 spec"
expect "state: the spec comes next, in the same session" "$(python3 "$S/state.py")" "skill: spec"
expect "a plan accepted before「接受 spec」is not an approval" "$(hook_plan 'an early plan')" "not recorded"
expect "…and writes no plan.md" "$(ls $F)" "intent.md"
cp "$T/change/spec.md" $F/spec.md
sed 's/(R2)//' "$T/change/validation.md" > $F/validation.md
expect "「接受 spec」 refused while the drafts are not committed" "$(hook_prompt '接受 spec')" "REFUSED"
commit "spec draft"
expect "accept spec refused: R2 not covered" "$(hook_prompt '接受 spec')" "R2 is not cited"
cp "$T/change/validation.md" $F/validation.md && commit "validation covers R2"
echo "<html>mock</html>" > $F/mock.html && commit "a mock"
expect "accept spec refused: the mock is not confirmed" "$(hook_prompt '接受 spec')" "the mock is not confirmed"
sed -i.bak '/^## Mock$/,/^## Fact values$/{/^## Fact values$/!d;}' $F/spec.md && rm $F/spec.md.bak && commit "spec without a Mock section"
expect "accept spec refused: a mock and no Mock section" "$(hook_prompt '接受 spec')" "no '## Mock' section"
cp "$T/change/spec.md" $F/spec.md
sed -i.bak 's/^- Confirmed by:$/- Confirmed by: Leon, 2026-01-01/' $F/spec.md && rm $F/spec.md.bak && commit "mock confirmed"
CHECK="$(python3 "$S/accept.py" spec --check)"
expect "accept spec passes once the mock is confirmed" "$CHECK" "nothing refuses"
expect "accept spec --check names the intent too" "$CHECK" "$F/intent.md"
expect "accept spec --check changes nothing" "$CHECK" "nothing was changed"
expect "state names the sentence for the spec" "$(python3 "$S/state.py")" "接受 spec"
expect "「接受 spec」 accepts intent, spec and validation" "$(hook_prompt 'spec 接受')" "spec accepted"
expect "…the intent is on main" "$(git show main:$F/intent.md)" "Contact phone"
expect "state: the plan is drafted in plan mode" "$(python3 "$S/state.py")" "plan mode"
expect "product file denied before plan approved" "$(hook_write 'src/app.py')" '"deny"'
PLAN_TEXT="$(sed 's#`<path>`#`src/app.py` `tests/test_app.py`#' "$T/change/plan.md")"
expect "a plan without the template's shape is not recorded" "$(hook_plan 'just add the phone number')" "lacks the template's shape"
expect "…and writes neither plan.md nor the mark" "$(ls $F | tr '\n' ' ')" "intent.md mock.html spec.md validation.md "
expect "a plan accepted inside a subagent records nothing" "$(hook_plan_in_subagent "$PLAN_TEXT")" ""
expect "…and writes no mark" "$(ls $F | grep -c plan)" "0"
OUT="$(hook_plan "$PLAN_TEXT")"
expect "accepting the plan in plan mode approves it" "$OUT" "plan approved"
expect "…the session is told to do what the owner chose: stop or go on" "$OUT" "He chose to stop"
expect "…plan.md is the accepted text" "$(cat $F/plan.md)" '`src/app.py` `tests/test_app.py`'
expect "…the mark is committed on the branch" "$(git show HEAD:$F/plan-approved.txt)" "accepted in plan mode"
expect "…and main does not move" "$(git show main:$F/plan.md 2>&1)" "not in 'main'"
expect "agent may not write the approval mark" "$(hook_write "$F/plan-approved.txt")" '"deny"'
expect "a later plan-mode approval leaves plan.md alone" "$(hook_plan 'a fix-round plan')" "already approved"
expect "「批准 plan」 after the approval changes nothing" "$(hook_prompt '批准 plan')" "already approved"
expect "plan.md may be edited after the approval (departures)" "$(hook_write "$F/plan.md")" ""
expect "state: red run not committed" "$(python3 "$S/state.py")" "red run is not committed"
expect "test file free before the red commit" "$(hook_write 'tests/test_app.py')" ""
echo "def test_phone(): assert False" > tests/test_app.py && echo "1 failed" > $F/red-run.txt && commit "red tests"
expect "test file not asked after the red commit" "$(hook_write 'tests/test_app.py')" ""
expect "product file allowed" "$(hook_write 'src/app.py')" ""
expect "non-product path allowed" "$(hook_write 'notes/today.md')" ""
echo "phone = '555'" > src/app.py && commit "implementation"
expect "state: implement until the reviewer reports 0 Important" "$(python3 "$S/state.py")" "reviewer"
expect "close check: no review entry" "$(python3 "$S/close_check.py")" "no review entry"
REPORT=$F/reports/review-1.md
expect "record review refused without the report on disk" "$(python3 "$S/record.py" review --by reviewer --important 1 --nit 0 --report $REPORT)" "REFUSED"
mkdir -p $F/reports && echo "I1 the phone number is not checked" > $REPORT
expect "bash hook allows record.py" "$(hook_bash "python3 \"$S/record.py\" review --by reviewer --important 1 --nit 0 --report $REPORT")" '"allow"'
expect "record review writes the line" "$(python3 "$S/record.py" review --by reviewer --important 1 --nit 0 --report $REPORT)" "review (reviewer) · Important open: 1"
expect "close check: Important still open" "$(python3 "$S/close_check.py")" "still open"
expect "state names the open findings and the report" "$(python3 "$S/state.py")" "1 Important open"
log_line "review, re-check (reviewer) · Important open: 0 · Nit: 0 · at $(git rev-parse --short HEAD)" $F/validation.md
expect "a re-check line with more words is read too" "$(python3 "$S/close_check.py")" "PASS review"
python3 "$S/record.py" review --by verifier --important 0 --nit 0 --report $REPORT >/dev/null
expect "close check: a normal change needs the reviewer" "$(python3 "$S/close_check.py")" "needs the reviewer"
python3 "$S/record.py" review --by reviewer --important 0 --nit 1 --report $REPORT >/dev/null
echo "def test_phone(): assert True" > tests/test_app.py
echo "def test_more(): assert True" > tests/test_more.py
CHECK="$(python3 "$S/close_check.py")"
expect "close check: unreleased change to an existing test file" "$CHECK" "has no 'test-release: tests/test_app.py'"
expect "…a new test file needs no release" "$(echo "$CHECK" | grep 'test scope' | grep -c test_more)" "0"
expect "record test-release refused outside the test scope" "$(python3 "$S/record.py" test-release src/app.py --why "x" --row T1)" "REFUSED"
OUT="$(python3 "$S/record.py" test-release tests/test_app.py --why "the assertion was wrong" --row T1)"
expect "record test-release writes the line" "$OUT" "— the assertion was wrong — §1 row T1"
expect "…with the content it releases" "$OUT" "test-release: tests/test_app.py · sha256 $(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()[:12])' tests/test_app.py)"
echo "def test_phone(): assert 1" > tests/test_app.py
expect "close check: a released test file changed again" "$(python3 "$S/close_check.py")" "tests/test_app.py changed again after its latest test-release line"
python3 "$S/record.py" test-release tests/test_app.py --why "the assertion was wrong" --row T1 >/dev/null
expect "…a new release line covers the new content" "$(python3 "$S/check_test_scope.py")" "released: tests/test_app.py"
expect "check_test_scope lists the new test file" "$(python3 "$S/check_test_scope.py")" "new: tests/test_more.py"
expect "record ruling needs what it was checked against" "$(python3 "$S/record.py" ruling "keep the old number" 2>&1)" "--checked"
expect "record ruling writes the line" "$(python3 "$S/record.py" ruling "keep the old number" --checked "§0 J1, R1")" "ruling: keep the old number · checked against: §0 J1, R1"
echo "x = 1" > src/extra.py
expect "close check: file outside the plan" "$(python3 "$S/close_check.py")" "src/extra.py changed but is not in plan.md"
rm src/extra.py
python3 - "$F/plan.md" <<'EOF'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
# a path on a continuation line, and a file name with square brackets (a dynamic route)
text = text.replace("(R1)\n", "(R1)\n- `src/pages/[slug].astro` — the page, and its data\n  `src/data/pages.json` `tests/test_more.py`\n", 1)
open(path, "w", encoding="utf-8").write(text)
EOF
mkdir -p src/pages src/data && echo "page" > 'src/pages/[slug].astro' && echo "{}" > src/data/pages.json
expect "plan drift reads continuation lines and square brackets" "$(python3 "$S/check_plan_drift.py")" "PASS plan drift"
expect "close check: no validation entry" "$(python3 "$S/close_check.py")" "no validation entry"
expect "record validation refuses a question §0 does not ask" "$(python3 "$S/record.py" validation J9=pass)" "REFUSED"
python3 "$S/record.py" validation J1=fail >/dev/null
expect "close check: a failed judgment" "$(python3 "$S/close_check.py")" "J1 failed"
expect "state: the failed judgment is to be fixed and asked again" "$(python3 "$S/state.py")" "J1 failed"
expect "record validation writes「not judged」" "$(python3 "$S/record.py" validation J1=not-judged)" "validation · J1 not judged"
expect "close check: not judged needs a leftover" "$(python3 "$S/close_check.py")" "J1 was not judged"
sed -i.bak 's/^- None\.$/- **L1** J1 not judged: footer year → roadmap: to do/' $F/validation.md && rm $F/validation.md.bak
expect "close check: leftover not in the roadmap" "$(python3 "$S/close_check.py")" "(2026-01-01-contact L1)"
expect "bash hook allows todo_add" "$(hook_bash "python3 \"$S/todo_add.py\" --who Leon \"footer year is wrong (2026-01-01-contact L1)\"")" '"allow"'
expect "todo_add commits two lines at once" "$(python3 "$S/todo_add.py" --who Leon "footer year is wrong (2026-01-01-contact L1)" "footer month is wrong")" "added 2 lines"
expect "…in one commit on main" "$(git log -1 --format=%s main)" "(+1 more)"
OUT="$(python3 "$S/todo_add.py" --who "review loop" "header is too tall" --who Kitty "logo is the old one")"
expect "todo_add: who raised it, line by line (first)" "$OUT" "· review loop · header is too tall"
expect "todo_add: who raised it, line by line (second)" "$OUT" "· Kitty · logo is the old one"
expect "todo_add refuses a --who without a name after it" "$(python3 "$S/todo_add.py" --who Leon "a line" --who)" "Usage:"
git merge -q --no-edit main
TODO_LINE="$(grep 'header is too tall' specs/roadmap.md)"
DENY="$(hook_edit specs/roadmap.md "$TODO_LINE" "")"
expect "edit hook: deleting a To do line on a branch is denied" "$DENY" '"deny"'
expect "…the refusal names the fixed-directly route" "$DENY" "fixed-directly --commit"
expect "edit hook: rewriting a To do line is denied" "$(hook_edit specs/roadmap.md "header is too tall" "header is fine")" '"deny"'
expect "edit hook: adding a To do line is denied" "$(hook_edit specs/roadmap.md "$TODO_LINE" "$TODO_LINE
- 2026-01-01 · Leon · one more line")" "todo_add.py"
git rev-parse HEAD > "$(git rev-parse --git-dir)/MERGE_HEAD"   # a merge is being resolved
expect "edit hook: not held while a merge is being resolved" "$(hook_edit specs/roadmap.md "$TODO_LINE" "")" ""
rm "$(git rev-parse --git-dir)/MERGE_HEAD"
expect "edit hook: the Status line may be edited" "$(hook_edit specs/roadmap.md "Status:" "Status: stage 1 done;")" ""
expect "edit hook: a planned stage may be added" "$(hook_edit specs/roadmap.md "## To do" "- stage 9: the other half of this change

## To do")" ""
grep -v 'header is too tall' specs/roadmap.md > "$WORK/roadmap" && cp "$WORK/roadmap" specs/roadmap.md   # as a shell command would
expect "close check: a To do line removed by the branch itself" "$(python3 "$S/close_check.py")" "this branch removed or rewrote a To do line"
python3 -c 'import sys; p="specs/roadmap.md"; t=open(p).read(); open(p,"w").write(t.replace("## Known limits", "- 2026-01-01 · Leon · slipped in on the branch\n\n## Known limits", 1))'
expect "close check: a To do line added by the branch itself" "$(python3 "$S/close_check.py")" "this branch added a To do line"
git checkout -q specs/roadmap.md
expect "close check: To do untouched passes" "$(python3 "$S/close_check.py")" "PASS to do"
FIX="$(git rev-parse --short HEAD)"
expect "roadmap_edit fixed-directly needs its commit" "$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"header is too tall\" --reason fixed-directly")" "wrong arguments"
expect "roadmap_edit fixed-directly refuses an unknown commit" "$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"header is too tall\" --reason fixed-directly --commit 0123abc")" "not a commit of this repository"
ASK="$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"header is too tall\" --reason fixed-directly --commit $FIX")"
expect "roadmap_edit fixed-directly asks" "$ASK" '"ask"'
expect "…and the prompt shows the commit" "$ASK" "fixed by commit $FIX"
expect "roadmap_edit fixed-directly deletes (after the click)" "$(python3 "$S/roadmap_edit.py" delete --match "header is too tall" --reason fixed-directly --commit $FIX)" "deleted (fixed-directly, $FIX)"
expect "…the commit on main names the fix" "$(git log -1 --format=%s main)" "fixed directly ($FIX)"
python3 "$S/roadmap_edit.py" delete --match "logo is the old one" --reason dismissed >/dev/null
git merge -q --no-edit main
expect "state: the end screen is done, the close is next" "$(python3 "$S/state.py")" "skill: close"
expect "「确认合并」 refused while changes are uncommitted" "$(hook_prompt '确认合并')" "uncommitted changes"
expect "record review refused while product changes are uncommitted" "$(python3 "$S/record.py" review --by reviewer --important 0 --nit 0 --report $REPORT)" "commit the product changes first"
commit "close"
expect "close check: product files changed after the latest review" "$(python3 "$S/close_check.py")" "product files changed after the latest review"
expect "record review records the commit reviewed" "$(python3 "$S/record.py" review --by reviewer --important 0 --nit 0 --report $REPORT)" "· at $(git rev-parse --short HEAD) ·"
commit "re-review"
expect "close check passes" "$(python3 "$S/close_check.py")" "all checks passed"
expect "state names the sentence for the merge" "$(python3 "$S/state.py")" "确认合并"
expect "agent may not merge a normal change" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
expect "agent may run merge --check" "$(hook_bash "python3 \"$S/merge.py\" --check")" '"allow"'
expect "「确认合并」 merges" "$(hook_prompt '确认合并')" "merged 2026-01-01-contact into \`main\`"
expect "main has the implementation" "$(git show main:src/app.py)" "555"
expect "after the merge the checkout is on main" "$(on_branch)" "main"
expect "after the merge the working branch is deleted" "$(git branch --list 2026-01-01-contact)" ""
expect "state: two to-do lines" "$(python3 "$S/state.py")" "to do: 2 open line"
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
expect "test file not asked in a small change either" "$(hook_write 'tests/test_app.py')" ""
expect "spec refused for a small change" "$(hook_write "$F/spec.md")" '"deny"'
cp "$T/change/validation-small.md" $F/validation.md
echo "year = 2026" >> src/app.py && mkdir -p deploy && echo "x" > deploy/site.yml && commit "small change"
log_line "review (verifier) · Important open: 0 · at $(git rev-parse --short HEAD)" $F/validation.md && commit "review"
expect "merge refused: high-risk path" "$(python3 "$S/merge.py")" "high-risk path"
expect "no merge prompt while the merge would be refused" "$(hook_bash "python3 \"$S/merge.py\"")" '"deny"'
git rm -q deploy/site.yml && commit "drop deploy change"
expect "merge refused: a product file removed after the review" "$(python3 "$S/merge.py" --check)" "product files changed after the latest review (at"
log_line "review (verifier) · Important open: 0 · at $(git rev-parse --short HEAD)" $F/validation.md && commit "review again"
ASK="$(hook_bash "python3 \"$S/merge.py\"")"
expect "merge asks" "$ASK" '"ask"'
expect "merge prompt lists the changed files" "$ASK" "src/app.py"
PROMPT="$(printf '%s' "$ASK" | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["permissionDecisionReason"])')"
expect "merge prompt: the changed files come before the intent" "$(printf '%s' "$PROMPT" | sed -n 2p)" "Changed: "
expect "merge prompt: the intent is its title only, on the last line" "$(printf '%s' "$PROMPT" | tail -1)" "Intent: Footer year"
expect "merge prompt: short enough not to fold (10 lines)" "$( [ "$(printf '%s\n' "$PROMPT" | wc -l)" -le 10 ] && echo short )" "short"
expect "merge (after the click)" "$(python3 "$S/merge.py")" "merged 2026-01-02-footer"
expect "after the click the checkout is on main" "$(on_branch)" "main"
expect "state: small change not yet read" "$(python3 "$S/state.py")" "not yet read by a fresh session: 1"

echo "6. disposing of a to-do line"
expect "roadmap_edit asks and shows the line" "$(hook_bash "python3 \"$S/roadmap_edit.py\" delete --match \"footer year\" --reason dismissed")" "footer year is wrong"
expect "roadmap_edit deletes" "$(python3 "$S/roadmap_edit.py" delete --match "footer year" --reason dismissed)" "deleted (dismissed)"
python3 "$S/roadmap_edit.py" delete --match "footer month" --reason dismissed >/dev/null
expect "state: no open line" "$(python3 "$S/state.py")" "to do: no open line"

echo "6b. project copies of the templates"
expect "every template's mark matches its content" "$(python3 "$HERE/tools/template_marks.py" --check)" "every mark matches"
STATE="$(python3 "$S/state.py")"
expect "state: a copy without a template mark is reported" "$STATE" ".claude/flow.json (no mark; template "
expect "state: a copy in step with its template is not reported" "$(printf '%s' "$STATE" | grep -c 'REVIEW.md (')" "0"
sed -i.bak 's/flow-template: [0-9-]*/flow-template: 2020-01-01/' REVIEW.md && rm REVIEW.md.bak
expect "state: a copy older than its template is reported" "$(python3 "$S/state.py")" "REVIEW.md (2020-01-01 "
git checkout -q REVIEW.md
sed -i.bak 's/\(flow-template: [0-9-]*\) [0-9a-f]*/\1 0000000/' REVIEW.md && rm REVIEW.md.bak
expect "state: the same date with another hash is reported" "$(python3 "$S/state.py")" " 0000000; template "
git checkout -q REVIEW.md
sed -i.bak 's/flow-template: [0-9-]*/flow-template: 2026-02-30/' REVIEW.md && rm REVIEW.md.bak
expect "state: a mark that is not a real date counts as no mark" "$(python3 "$S/state.py")" "REVIEW.md (no mark; template "
git checkout -q REVIEW.md

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
expect "a plan read from the file plan mode wrote" "$(cat specs/2026-01-05-pr/plan.md)" "src/listing.py"
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
rm "$FAKE_PR" && quick_change 2026-01-06-squash banner sentence
expect "「批准 plan」 writes the same mark" "$(cat specs/2026-01-06-squash/plan-approved.txt)" "「批准 plan」"
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
log_line "review (verifier) · Important open: 0 · at $(git rev-parse --short HEAD)" $F/validation.md && commit "review"
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
log_line "review (verifier) · Important open: 0 · at $(git rev-parse --short HEAD)" $F/validation.md && commit "review"
OUT="$(python3 "$S/merge.py")"
expect "a merge from a worktree moves main where it is checked out" "$OUT" "merged 2026-01-08-stream into \`main\`"
expect "…the branch stays, with what is left to do by hand" "$OUT" "this checkout stays on 2026-01-08-stream"
cd "$WORK/repo"
expect "the checkout of main has the change" "$(grep -c 'day = 1' src/app.py)" "1"

cd "$HERE" && rm -rf "$WORK"
echo
echo "selftest: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
