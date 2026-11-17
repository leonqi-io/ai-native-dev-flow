# 钩子和脚本清单

全部在 `plugin/hooks/hooks.json` 和 `plugin/scripts/` 里，只用 Python 3 标准库，不装依赖。仓库里没有 `.claude/flow.json` 时，钩子什么都不做。

改了任何一个脚本之后跑自测（不调用模型）：

```bash
bash tools/selftest.sh
```

## 钩子

| 钩子 | 事件 | 做什么 |
|---|---|---|
| 状态报告 | 会话开始 | 跑 `state.py --hook`，把结果放进上下文：阶段、档位、下一步、owner 该说的那句话（和终端里的那一行）、本地 `main` 是否落后于 origin、未决待办的行数和最早日期、还没被新 session 读过的小改动 |
| 批准句 | 消息提交时 | `hook_user_prompt.py`：整条消息是五句批准句之一时，直接运行 `accept.py` 或 `merge.py`，把输出交给 agent，并给 owner 显示一段结果。见下面一节 |
| Bash | 工具调用前 | 见下表 |
| Edit / Write | 工具调用前 | 见下表 |
| 自发的提示 | 工具调用前（`CronCreate`、`ScheduleWakeup`、`SendMessage`） | 同一个 `hook_user_prompt.py`：调用里的文字是批准句就拒绝 |

### 批准句钩子

| owner 说 | 运行 | 效果 |
|---|---|---|
| `接受立项` | `accept.py setup` | 在 `setup` 分支上：整条分支进 `main`，切到 `main`，删 `setup`。在别的分支上：只提交项目级文件 |
| `接受 intent` | `accept.py intent` | intent.md 提交进 `main` |
| `接受 spec` | `accept.py spec` | spec.md 和 validation.md 提交进 `main` |
| `批准 plan` | `accept.py plan` | plan.md 提交进 `main` |
| `确认合并` | `merge.py` | 收尾检查，合并（本地，或合并 PR），推送，切到 `main`，删分支 |

- 整条消息只有这句话才触发。比较时去掉空格和标点、不分大小写；词序反过来（`intent 接受`）和英文说法（`accept intent`、`approve plan`、`confirm merge`）也认。句子的清单只在 `flowlib.OWNER_SENTENCES` 一处。
- 脚本和 owner 在终端里跑的是同一个，拒绝条件相同。被拒绝时 `main` 没动，拒绝的句子交给 agent，agent 修好自己能修的，再请 owner 说一次。
- 在 subagent 里触发（输入里有 `agent_id`）时不动作。
- 钩子的超时设成 120 秒，脚本自己有 100 秒，脚本里每个连 origin 的 git 命令 20 秒、每个 `gh` 调用 30 秒；超时算失败，说明原因，再说一次那句话即可（合并可以重复执行，已经合并的只做清理）。

### Bash 钩子的三种回答

| 回答 | 对什么 | 说明 |
|---|---|---|
| 拒绝 | 会移动 `main` 的 git 命令：在 `main` 上 commit、merge、rebase、reset、revert、cherry-pick、am、pull；push 到 `main`；fetch 进 `main`；`branch -f` 之类改动 `main`；`update-ref` 到 `refs/heads/main`；先切到 `main` 再做上述动作的连写命令。还有 `gh pr merge` | 原因里写明该走哪条路：批准和合并由 owner 说那句话（或在终端里跑脚本），本地 `main` 落后用 `sync_main.py`，发现用 `todo_add.py` 记 |
| 询问 | 小改动的 `accept.py intent`（显示 intent 全文）；小改动的 `merge.py`（显示 intent、改动的文件和行数，部署类项目加一行「Merging publishes to production」）；`roadmap_edit.py`（显示那一行和动作） | owner 点一次就是批准。这三个脚本必须单独运行，后面连了别的命令就拒绝。合并提示弹出之前钩子先跑一遍 `merge.py --check`，不过就直接拒绝并列出缺什么，不浪费那次点击 |
| 放行 | 只读的脚本（`state.py`、各个检查脚本、`accept.py … --check`、`merge.py --check`）；`todo_add.py`（只能追加一行）；`sync_main.py`（只做快进和补推） | 省掉一次权限提示 |

正常档和高风险档由 agent 调用 `accept.py` 或 `merge.py`、任何档位由 agent 调用 `accept.py setup`，都会被拒绝，原因里给出 owner 该说的那句话和终端里的那一行。

### Edit / Write 钩子

| 检查 | 条件 | 回答 |
|---|---|---|
| 存在检查 | 写 spec.md 或 validation.md，而 intent.md 不在 `main` 上 | 拒绝，说明该走哪条路 |
| 存在检查 | 写 plan.md，而 spec.md 和 validation.md 不都在 `main` 上 | 拒绝 |
| 存在检查 | 写产品文件，而 plan.md 不在 `main` 上（小改动：intent.md 不在 `main` 上） | 拒绝 |
| 存在检查 | 在 `main` 上或在没有改动文件夹的分支上写产品文件 | 拒绝 |
| 小改动 | 给小改动写 spec.md 或 plan.md | 拒绝 |
| 测试锁 | 锁开着时写测试范围内的文件 | 询问，显示文件；批准后 agent 在 Approval log 里记 `test-release:` 一行 |

- 产品文件 = `specs/`、`CLAUDE.md` 和项目 `non_product_paths` 之外的一切。
- 项目还没立项时（三份项目级文件不全在 `main` 上），这个钩子不动作。
- 存在检查只看「在不在 `main` 上」，不锁内容。
- 钩子脚本自己出错时不拦截，只在记录里留一行错误。

### 已知界限

- 拦截靠模式匹配：挡得住 agent 越过批准，挡不住人绕过去。
- 存在检查只看得到 Edit 和 Write。用 shell 写文件能绕过它，但绕过之后：测试文件的改动由测试范围差异检查查到，plan 之外的文件由 plan 对照检查查到，都在合并之前。核心不带「禁止用 shell 改写文件」的钩子；试点里数一项，出现绕过再加。
- `ask`：官方文档写明 auto 模式下钩子的 `ask` 一定弹提示；其他权限模式下弹不弹、能显示多少字，未核实，试点里测。退路是批准句。
- 批准句钩子分不出一条 prompt 是不是 owner 打的：定时唤醒、后台 subagent 的回报、别的 session 发来的消息也会触发它，输入里没有来源字段。现在靠三条：整句匹配、在 subagent 里不动作、拦掉内容是批准句的定时任务和跨 session 消息。这三种 prompt 的文本实际长什么样，未核实，试点里测。
- 批准句钩子的结果给 owner 显示用的是 `systemMessage` 字段，在 `UserPromptSubmit` 上显不显示，未核实。不显示的话，结果只由 agent 转述。
- 走 PR 的合并（`gh pr view`、`gh pr merge --merge`）只在自测里对着一个假的 `gh` 跑过，真实 GitHub 上未核实。
- 插件钩子没在跑的 session（云端、Cowork，未核实）里，批准句不会有反应，只能在终端里跑脚本。

## 脚本

| 脚本 | 谁运行 | 做什么 |
|---|---|---|
| `state.py` | 钩子、skill、人 | 从 Git 推出当前阶段，报「项目未立项」、档位、下一步、owner 该说的那句话、分支是否已经合并、本地 `main` 是否落后、待办和未读小改动 |
| `accept.py setup\|intent\|spec\|plan [--check]` | owner 说批准句（钩子运行），或在自己的终端；小改动的 `intent` 由 agent 调用并弹确认；`--check` 谁都可以跑 | 把批准文件提交进 `main`，再把 `main` 合回工作分支。先查：文件已在工作分支上提交、形状对、（`spec`）R-ID 全覆盖、前一份批准文件已在 `main` 上。`setup` 在 `setup` 分支上不同：整条分支进 `main`，列出每个进去的文件，然后切到 `main`、删 `setup`。`--check` 只查、只列，不改 |
| `merge.py [--check]` | owner 说「确认合并」（钩子运行），或在自己的终端；小改动由 agent 调用并弹确认 | 先跑收尾检查；小改动碰高风险路径就拒绝。本地合并（小改动、不开 PR 的项目）：把 `main` 前移到分支头并推到 origin。走 PR（开 PR 的项目的正常档和高风险档）：核对 PR 的头，`gh pr merge --merge`，本地 `main` 快进到 `origin/main`。之后切到 `main`，删本地和远端分支。分支已经在 `main` 里时只做清理 |
| `sync_main.py` | agent、人 | 本地 `main` 和 `origin/main` 对齐：origin 领先就快进本地，本地领先就补推，分叉就拒绝。不批准任何东西 |
| `close_check.py` | skill、`merge.py` | 把下面五项检查和「评审结论里没有未处理的 Important」一起跑 |
| `check_shape.py` | skill、`accept.py`、`close_check.py` | 每份产出物的必备标题在不在 |
| `check_rid_coverage.py` | skill、`accept.py`、`close_check.py` | spec.md 的每个 R-ID 至少出现在 validation.md 的 §0、§1、§2 之一 |
| `check_test_scope.py` | `close_check.py` | 锁开始之后测试范围内有变动的文件，都要有 `test-release:` 记录 |
| `check_plan_drift.py` | `close_check.py` | 改动的产品文件都在 plan.md 的「Files that change」里 |
| `check_leftovers.py` | `close_check.py` | 每条遗留项指向新 intent、「To do」的一行或「Known limits」的一行 |
| `todo_add.py --who <名字> "<一句话>"` | agent、人 | 往 `main` 上 roadmap 的「To do」段追加一行并直接提交 |
| `roadmap_edit.py delete\|move --match "<文字>"` | agent 调用并弹确认；人 | 删除一行待办（现在修或不做），或移到计划阶段 |
| `flowlib.py` | 其他脚本 | 共用的部分：读 `main`、读档位、往 `main` 提交的唯一机制 |
| `hook_pretool_bash.py`、`hook_pretool_write.py` | 钩子 | 上面两张表 |
| `hook_user_prompt.py` | 钩子 | 批准句；拦掉内容是批准句的自发提示 |

## 脚本读的几种固定写法

- **档位**：intent.md 里一行 `Tier: small`、`Tier: normal` 或 `Tier: high-risk`。
- **评审结论**：Approval log 里 `- <日期 时间> · review (fresh session) · Important open: 0 · Nit: 2`；小改动是 `review (verifier)`。只看最后一条。
- **测试放行**：`- <日期 时间> · test-release: <路径> — <原因> — §1 row <编号>`。
- **小改动被新 session 读过**：`- <日期 时间> · small-change read (fresh session) · behaviour changed: yes|no`。
- **遗留项**：`- **L1** <内容> → specs/<新文件夹>/intent.md`、`→ roadmap: to do`、`→ roadmap: known limits`；没有就写 `- None.`。指向 roadmap 的，roadmap 那一行末尾带 `(<文件夹名> L1)`。
- **待办行**：`- <日期> · <谁提的> · <一句话>`。

## 往 `main` 提交是怎么做的

`accept.py`（文件级的提交）、`todo_add.py`、`roadmap_edit.py` 都通过 `flowlib.commit_to_main` 提交：在临时索引里搭出新的树，不切换分支，不动当前工作区。`main` 如果正被某个 worktree 检出，那个 worktree 里已跟踪的文件必须没有未提交的改动，提交后它会被同步到新提交。

整条分支进 `main`（`merge.py` 的本地合并、`setup` 分支的立项验收）走 `flowlib.move_main`：只做快进。

有远端的项目，这两种方式都先 `flowlib.sync_main`（把 `origin/main` 快进进本地，分叉就拒绝），做完再 `flowlib.push_main`。推送失败不回退本地的提交，脚本说明没推上去，下一次移动 `main` 或 `sync_main.py` 会补推。
