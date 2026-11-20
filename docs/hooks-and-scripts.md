# 钩子和脚本清单

全部在 `plugin/hooks/hooks.json` 和 `plugin/scripts/` 里，只用 Python 3 标准库，不装依赖。仓库里没有 `.claude/flow.json` 时，钩子什么都不做。

改了任何一个脚本之后跑自测（不调用模型）：

```bash
bash tools/selftest.sh
```

## 钩子

| 钩子 | 事件 | 做什么 |
|---|---|---|
| 状态报告 | 会话开始 | 跑 `state.py --hook`，把结果放进上下文：阶段和其中的小步、档位、下一步、owner 该说的那句话（和终端里的那一行）、本地 `main` 是否落后于 origin、未决待办的行数和最早日期、还没被新 session 读过的小改动 |
| 批准句 | 消息提交时 | `hook_user_prompt.py`：整条消息是五句批准句之一时，直接运行 `accept.py` 或 `merge.py`，把输出交给 agent，并给 owner 显示一段结果。见下面一节 |
| Bash | 工具调用前 | 见下表 |
| Edit / Write | 工具调用前 | 见下表 |
| 自发的提示 | 工具调用前（`CronCreate`、`ScheduleWakeup`、`SendMessage`） | 同一个 `hook_user_prompt.py`：调用里的文字是批准句就拒绝 |
| plan 的批准 | 工具调用后（`ExitPlanMode`） | `hook_plan_approved.py`：owner 接受计划时，把被接受的计划原文写成 `specs/<文件夹>/plan.md`，写批准标记 `plan-approved.txt`，两个一起提交在工作分支上。只在正常档和高风险档、spec 已接受、还没有批准标记、计划有模板的形状（「For the owner」等必备标题，和「批准 plan」同一项检查）时动作；否则说明为什么没记，形状不对时让 session 回 plan mode 补齐再交。在 subagent 里触发时（输入带 `agent_id`）不动作 |

### 批准句钩子

| owner 说 | 运行 | 效果 |
|---|---|---|
| `接受立项` | `accept.py setup` | 在 `setup` 分支上：整条分支进 `main`，切到 `main`，删 `setup`。在别的分支上：只提交项目级文件 |
| `接受 intent` | `accept.py intent` | 只用于小改动：intent.md 提交进 `main`。正常档和高风险档拒绝，原因里指向「接受 spec」 |
| `接受 spec` | `accept.py spec` | intent.md、spec.md、validation.md 一起提交进 `main` |
| `批准 plan` | `accept.py plan` | 退路：plan mode 里接受之后标记没记上时用。plan.md 已在工作分支上提交、没有未提交的改动时，写批准标记并提交在工作分支上；`main` 不动 |
| `确认合并` | `merge.py` | 收尾检查，合并（本地，或合并 PR），推送，切到 `main`，删分支 |

- 整条消息只有这句话才触发。比较时去掉空格和标点、不分大小写；词序反过来（`intent 接受`）和英文说法（`accept intent`、`approve plan`、`confirm merge`）也认。句子的清单只在 `flowlib.OWNER_SENTENCES` 一处。
- 脚本和 owner 在终端里跑的是同一个，拒绝条件相同。被拒绝时 `main` 没动，拒绝的句子交给 agent，agent 修好自己能修的，再请 owner 说一次。
- 在 subagent 里触发（输入里有 `agent_id`）时不动作。
- 成功之后交给 agent 的说明里写明下一步，agent 不停下来接着做：「接受 spec」之后进 plan mode，plan 批准之后实现。
- 钩子的超时设成 120 秒，脚本自己有 100 秒，脚本里每个连 origin 的 git 命令 20 秒、每个 `gh` 调用 30 秒；超时算失败，说明原因，再说一次那句话即可（合并可以重复执行，已经合并的只做清理）。

### Bash 钩子的三种回答

| 回答 | 对什么 | 说明 |
|---|---|---|
| 拒绝 | 会移动 `main` 的 git 命令：在 `main` 上 commit、merge、rebase、reset、revert、cherry-pick、am、pull；push 到 `main`；fetch 进 `main`；`branch -f` 之类改动 `main`；`update-ref` 到 `refs/heads/main`；先切到 `main` 再做上述动作的连写命令。还有 `gh pr merge` | 原因里写明该走哪条路：批准和合并由 owner 说那句话（或在终端里跑脚本），本地 `main` 落后用 `sync_main.py`，发现用 `todo_add.py` 记 |
| 询问 | 小改动的 `accept.py intent`（显示 intent 全文）；小改动的 `merge.py`（显示 intent、改动的文件和行数，部署类项目加一行「Merging publishes to production」）；`roadmap_edit.py`（显示那一行和动作） | owner 点一次就是批准。这三个脚本必须单独运行，后面连了别的命令就拒绝。合并提示弹出之前钩子先跑一遍 `merge.py --check`，不过就直接拒绝并列出缺什么，不浪费那次点击 |
| 放行 | 只读的脚本（`state.py`、各个检查脚本、`accept.py … --check`、`merge.py --check`）；`todo_add.py`（只能往待办段追加）；`sync_main.py`（只做快进和补推）；`record.py`（只往本改动的 Approval log 追加一行） | 省掉一次权限提示 |

正常档和高风险档由 agent 调用 `accept.py` 或 `merge.py`、任何档位由 agent 调用 `accept.py setup`，都会被拒绝，原因里给出 owner 该说的那句话和终端里的那一行。

### Edit / Write 钩子

| 检查 | 条件 | 回答 |
|---|---|---|
| 存在检查 | 写 spec.md 或 validation.md，而 intent.md 还没有带档位的 `Tier:` 行 | 拒绝，说明该走哪条路 |
| 存在检查 | 写 plan.md，而 spec.md 和 validation.md 不都在 `main` 上 | 拒绝 |
| 存在检查 | 写产品文件，而 plan 的批准标记不在（小改动：intent.md 不在 `main` 上） | 拒绝 |
| 存在检查 | 在 `main` 上或在没有改动文件夹的分支上写产品文件 | 拒绝 |
| 批准标记 | 写 `specs/<文件夹>/plan-approved.txt` | 拒绝：只有 plan 的批准写它 |
| 小改动 | 给小改动写 spec.md 或 plan.md | 拒绝 |

- 测试文件不在这里拦：改锁住的测试不询问 owner，agent 用 `record.py test-release` 记一行，收尾检查（`check_test_scope.py`）拒绝没有放行行的改动。

- 产品文件 = `specs/`、`CLAUDE.md` 和项目 `non_product_paths` 之外的一切。
- 项目还没立项时（三份项目级文件不全在 `main` 上），这个钩子不动作。
- 存在检查只看批准记录在不在（文件在不在 `main` 上、批准标记在不在），不锁内容。
- 钩子脚本自己出错时不拦截，只在记录里留一行错误。

### 已知界限

- 拦截靠模式匹配：挡得住 agent 越过批准，挡不住人绕过去。
- 存在检查只看得到 Edit 和 Write。用 shell 写文件能绕过它，但绕过之后：测试文件的改动由测试范围差异检查查到，plan 之外的文件由 plan 对照检查查到，都在合并之前。核心不带「禁止用 shell 改写文件」的钩子（2026-11-19 裁定）：plan mode 本身不让写文件，上面两项检查对 shell 写的文件实测管用。
- 评审行、验收行、放行行由实现的 session 调 `record.py` 写，它可以记一次没有发生的评审或放行；收尾检查信这些行。这个界限 owner 已接受（2026-11-19）。记了之后的改动查得到（2026-11-20）：评审行记被评审的提交，之后产品文件再变就拒绝；放行行记文件内容的哈希，之后再变就拒绝。
- owner 打回计划时 `ExitPlanMode` 的 PostToolUse 触不触发，文档没有明说，未核实；第一次真实使用时 owner 故意打回一次，看标记有没有被记上。
- plan mode 里能不能起自定义的 subagent（`reviewer` 的预读），未核实；飞猫阶段 3 的 plan 上看。
- `ask`：官方文档写明 auto 模式下钩子的 `ask` 一定弹提示；其他权限模式下弹不弹、能显示多少字，未核实，试点里测。退路是批准句。
- 批准句钩子分不出一条 prompt 是不是 owner 打的：定时唤醒、后台 subagent 的回报、别的 session 发来的消息也会触发它，输入里没有来源字段。现在靠三条：整句匹配、在 subagent 里不动作、拦掉内容是批准句的定时任务和跨 session 消息。这三种 prompt 的文本实际长什么样，未核实，试点里测。
- 批准句钩子的结果给 owner 显示用的是 `systemMessage` 字段，在 `UserPromptSubmit` 上显不显示，未核实。不显示的话，结果只由 agent 转述。
- 走 PR 的合并（`gh pr view`、`gh pr merge --merge`）只在自测里对着一个假的 `gh` 跑过，真实 GitHub 上未核实。
- 插件钩子没在跑的 session（云端、Cowork，未核实）里，批准句不会有反应，只能在终端里跑脚本。

## 脚本

| 脚本 | 谁运行 | 做什么 |
|---|---|---|
| `state.py` | 钩子、skill、人 | 从仓库推出当前阶段和小步（批准记录、批准标记、红测试、Approval log 里最新的评审行和验收行），报「项目未立项」、档位、下一步、owner 该说的那句话、分支是否已经合并、本地 `main` 是否落后、待办和未读小改动 |
| `accept.py setup\|intent\|spec\|plan [--check]` | owner 说批准句（钩子运行），或在自己的终端；小改动的 `intent` 由 agent 调用并弹确认；`--check` 谁都可以跑 | `setup`、`intent`（只限小改动）、`spec`（intent、spec、validation 三份）：把批准文件提交进 `main`，再把 `main` 合回工作分支。先查：文件已在工作分支上提交、形状对、（`spec`）R-ID 全覆盖。`plan`：退路，plan.md 已提交且没有未提交的改动时写批准标记，提交在工作分支上。`setup` 在 `setup` 分支上不同：整条分支进 `main`，列出每个进去的文件，然后切到 `main`、删 `setup`。`--check` 只查、只列，不改 |
| `merge.py [--check]` | owner 说「确认合并」（钩子运行），或在自己的终端；小改动由 agent 调用并弹确认 | 先跑收尾检查；小改动碰高风险路径就拒绝。本地合并（小改动、不开 PR 的项目）：把 `main` 前移到分支头并推到 origin。走 PR（开 PR 的项目的正常档和高风险档）：核对 PR 的头，`gh pr merge --merge`，本地 `main` 快进到 `origin/main`。之后切到 `main`，删本地和远端分支。分支已经在 `main` 里时只做清理 |
| `sync_main.py` | agent、人 | 本地 `main` 和 `origin/main` 对齐：origin 领先就快进本地，本地领先就补推，分叉就拒绝。不批准任何东西 |
| `close_check.py` | skill、`merge.py` | 把下面五项检查，和评审、验收两项一起跑：最新的评审行没有未处理的 Important、它指向的报告在盘上、它记的提交之后产品文件没有再变（已提交的和未提交的都算；正常档和高风险档要求是 reviewer 或新 session 的）；最新的验收行每道判断题都有答案、没有不通过、不判断的在 Leftovers 里 |
| `check_shape.py` | skill、`accept.py`、`close_check.py` | 每份产出物的必备标题在不在 |
| `check_rid_coverage.py` | skill、`accept.py`、`close_check.py` | spec.md 的每个 R-ID 至少出现在 validation.md 的 §0、§1、§2 之一 |
| `check_test_scope.py` | `close_check.py`、skill | 锁开始时已经存在、之后有变动的测试文件，最新一条 `test-release:` 记录的哈希都要等于文件现在的哈希（没有记录、或记录之后又变了，都拒绝）；新建的测试文件不要求，单独列出 |
| `check_plan_drift.py` | `close_check.py` | 改动的产品文件都在 plan.md 的「Files that change」里（列表项和它的缩进续行里的反引号路径；方括号按字面） |
| `check_leftovers.py` | `close_check.py` | 每条遗留项指向新 intent、「To do」的一行或「Known limits」的一行 |
| `todo_add.py --who <名字> "<一句话>" ["<一句话>" …]` | agent、人 | 往 `main` 上 roadmap 的「To do」段追加一行或多行，一次提交 |
| `record.py review\|validation\|test-release\|ruling` | agent | 往本改动 validation.md 的 Approval log 追加一行，时间和格式由脚本写。`review` 要求报告已在改动文件夹里、产品文件没有未提交的改动，并记下被评审的提交；`validation` 只收 §0 里有的判断题编号，并带上之前的答案；`test-release` 只收测试范围内的路径，并记下文件当时内容的哈希；`ruling` 要求写明核对过什么。这些行的解析也在这个脚本里 |
| `roadmap_edit.py delete\|move --match "<文字>"` | agent 调用并弹确认；人 | 删除一行待办（现在修或不做），或移到计划阶段 |
| `flowlib.py` | 其他脚本 | 共用的部分：读 `main`、读档位、plan 的批准标记、往 `main` 提交的唯一机制 |
| `hook_pretool_bash.py`、`hook_pretool_write.py` | 钩子 | 上面两张表 |
| `hook_plan_approved.py` | 钩子 | plan mode 里接受计划之后写 plan.md 和批准标记 |
| `hook_user_prompt.py` | 钩子 | 批准句；拦掉内容是批准句的自发提示 |

## 脚本读的几种固定写法

- **档位**：intent.md 里一行 `Tier: small`、`Tier: normal` 或 `Tier: high-risk`。
- **Approval log 里脚本读的行**，都由 `record.py` 写，格式只在它的说明里一处：
  - 评审：`- <日期 时间> · review (reviewer) · Important open: 0 · Nit: 2 · at 3f2a9c1 · report: specs/<文件夹>/reports/review-1.md`（`at`：记行时的 HEAD，即被评审的提交）；小改动是 `review (verifier)`，新 session 是 `review (fresh session)`。`review` 和括号之间可以有别的字（`review, re-check (reviewer)`）。只看最后一条。
  - 验收：`- <日期 时间> · validation · J1 pass · J2 not judged`。每一行带着到那时为止的全部答案，只看最后一条。
  - 测试放行：`- <日期 时间> · test-release: <路径> · sha256 <前 12 位> — <原因> — §1 row <编号>`（哈希是记行时文件的内容，文件已删除时写 `deleted`；小改动没有 §1，不带最后一段）。
  - 裁定：`- <日期 时间> · ruling: <裁定> · checked against: <核对过什么>`。
- **plan 的批准标记**：`specs/<文件夹>/plan-approved.txt`，一行：怎么批准的、时间、批准时 plan.md 的 sha256 前 12 位。
- **报告**：`specs/<文件夹>/reports/` 下，code-reviewer、verifier、reviewer 各一份，按轮编号。
- **小改动被新 session 读过**：`- <日期 时间> · small-change read (fresh session) · behaviour changed: yes|no`。
- **遗留项**：`- **L1** <内容> → specs/<新文件夹>/intent.md`、`→ roadmap: to do`、`→ roadmap: known limits`；没有就写 `- None.`。指向 roadmap 的，roadmap 那一行末尾带 `(<文件夹名> L1)`。
- **待办行**：`- <日期> · <谁提的> · <一句话>`。

## 往 `main` 提交是怎么做的

`accept.py`（文件级的提交；`plan` 除外，它只提交在工作分支上）、`todo_add.py`、`roadmap_edit.py` 都通过 `flowlib.commit_to_main` 提交：在临时索引里搭出新的树，不切换分支，不动当前工作区。`main` 如果正被某个 worktree 检出，那个 worktree 里已跟踪的文件必须没有未提交的改动，提交后它会被同步到新提交。

整条分支进 `main`（`merge.py` 的本地合并、`setup` 分支的立项验收）走 `flowlib.move_main`：只做快进。

有远端的项目，这两种方式都先 `flowlib.sync_main`（把 `origin/main` 快进进本地，分叉就拒绝），做完再 `flowlib.push_main`。推送失败不回退本地的提交，脚本说明没推上去，下一次移动 `main` 或 `sync_main.py` 会补推。
