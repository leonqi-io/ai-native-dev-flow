# 试点清单

只放还没做的条目。做完一条删一条，结果写进 `docs/decisions.md`。

试点项目：flightcat.ca 改版。试点不从写这个仓库的 session 开始。

## 试点里要实测的几条（都是「未核实」）

| # | 要测什么 | 怎么测 | 退路 |
|---|---|---|---|
| 2 | `ask` 在自动批准模式下还弹不弹提示，提示里能显示多少字 | 在各个权限模式下各跑一次小改动的第一次点击，看提示出不出、intent 全文显不显示 | 小改动的两次点击改用批准句（「接受 intent」「确认合并」）。roadmap 的删除和移动没有批准句：钩子改成拒绝，原因里给一行可粘贴的命令，由 owner 自己运行。官方文档写明 auto 模式下 `ask` 一定弹提示，所以重点测其他模式和提示里能显示多少字 |
| 4 | 内置浏览器的三项：每个 session 一个还是共用；在后台会不会被限速；能不能上传文件 | 飞猫第一个 UI 改动之前，在桌面端开两个 session 各打开本地预览试 | 测完之前按最保守的读法：浏览器一次只给一个 session 用。结果只改一条规则：并行的 UI 改动要不要排队用浏览器 |
| 5 | 批准句钩子：三种不是 owner 打字的 prompt（定时唤醒、后台 subagent 的回报、别的 session 发来的消息）的文本长什么样 | 临时加一个只把输入写进日志的 `UserPromptSubmit` 钩子，各触发一次 | 文本可以恰好等于批准句：把批准句换成更长的，或加一个只有 owner 知道的词 |
| 7 | `main` 一动就推，会不会让流水线跑得太多 | 飞猫接上 Actions 之后，数一个改动从 intent 到合并触发了几次构建（每次批准、每条待办各推一次） | 在流水线里按路径忽略 `specs/**`；还嫌多就改成只在合并和同步时推 |
| 11 | 两个改动在两个 git worktree 里交错着走（规则在 `docs/flow.md` Build 一节，一个 worktree 一个分支一个 session）：`state.py`、各钩子、批准句和 `accept.py` / `merge.py` 认不认得出自己在哪个 worktree、哪个改动；`main` 被另一边的批准句移动之后，这一边把 `main` 合回来是否顺利（`roadmap.md` 的 Status 行和「To do」最容易撞）；内置浏览器两个 session 能不能同时用（和第 4 条一起看） | B 合并、flow 按交接改完之后试一次：N 在实现和评审时，开第二个 worktree 做 N+1 的 intent 和 spec，N+1 挑不碰网站模板的 pipeline 小修（roadmap「To do」里 blog import 那几条）；N 收尾后看两边的 `git log`、合并提交和 `state.py` 的报告 | 脚本认不出 worktree：改 `flowlib` 按 worktree 找改动文件夹；`roadmap.md` 冲突太多：交错时 N+1 在接受之前不碰 roadmap，遗留项等 N 合并后再记 |

## 试点期间

- 每个改动收尾时在 `docs/measures.md` 末尾记一行。
- 流程本身的问题当场记在下面一节，一行一条；修掉并回填规则文档之后删掉那一行。

## 试点中发现、还没处理的流程问题

- 2026-11-21 · **按交接改 flow（清单第 1–13 项）：做完，交给 owner。** 都没有提交。裁定和四个补充点在 `docs/decisions.md` 2026-11-21 的最后四行。owner 要做的：提交；`claude plugin validate plugin`；eval 不用重跑（没有改 description 或 `when_to_use`）；飞猫仓库同步三份模板副本（`CLAUDE.md`、`REVIEW.md`、`.claude/flow.json`——状态报告现在会报这三份没有模板标记；`CLAUDE.md` 还少 11-20 记下的两行和这次新增的三处），走一个小改动；然后按飞猫 roadmap 做下一个改动。下一个改动上第一次用到、要看的：（一）交计划之前的问询在 plan mode 里弹不弹得出来、选「先停」之后 session 是不是只回一行就停；（二）UI 改动的 mock 评审——researcher 的对比列不列得全、「接受 spec」在没写确认人时拒不拒绝；（三）「不记」的那一组在结尾那一屏上是不是成块出现、「To do」涨了几行；（四）小改动的合并提示是不是十行以内、文件清单在最前；（五）收尾检查的「to do」一项有没有误拒（把 `main` 合回分支之后）。这次留下没处理的一点，待 owner 裁定：`accept.py spec` 只把 intent、spec、validation 三份提交进 `main`，`mock.html` 到合并才进——mock 评审之后它是合同的一部分，而 `main` 上的批准记录里没有它。
- 2026-11-20 · **改 flow（一个改动一个 session，加 11-20 的模型裁定和三条待裁定）：做完，⑥ 交给 owner。** 都没有提交。owner 要做的：提交；`claude plugin validate plugin`；重跑改了 description 或 `when_to_use` 的 eval 用例——intent、spec、plan、implement、validate、close、review（`pick-spec` 的提问还是「intent 已经接受了，开始写 spec」，skill 的说法已改成「intent 写好了，开始写 spec」：改提问和重跑一起做，`docs/skills.md` 的生成段跟着重生成；11-20 这一轮没有再改 description）；把 `plugin/templates/user/model-table.md` 重新贴进 `~/.claude/CLAUDE.md`（那里还是 11-15 按步骤分模型的表）；飞猫仓库把 `.claude/flow.json` 的 `deploys` 改成 false、同步模板的 REVIEW.md（多了固定检查「New test-setup file」），roadmap 的 Status 行留到阶段 3 的分支上改；用飞猫阶段 3（博客）做第二个试点改动，数 owner 坐下来几次、中途被叫到几次，plan 上故意打回一次（第 8 条），看预读的 subagent 起不起得来（第 9 条）。
- 2026-11-20 · 高风险档留不留：先留着（回退路径、§3 必填、真实数据上走一遍）；要不要取消这一档、改成按事实触发，第二个试点改动之后按 `docs/measures.md` 的「高风险档留不留」一行再看。待 owner 裁定。
- 2026-11-20 01:00 · 试点清单第 2 条的第一份数据（飞猫，小改动「同步 REVIEW.md」的第一次点击，owner 贴的截图）：`ask` 的提示弹出来了，标题是「Hook PreToolUse:Bash requires confirmation for this command」，下面是钩子给的那句说明和 intent 的开头——标题、`Tier: small`、Problem 一段，之后是「… (+8 more lines)」，也就是提示里只显示了 intent 的前十行左右，剩下的折叠了。当时是什么权限模式、折叠的部分能不能在提示里展开，还没问到。按这份数据，intent 较长时 owner 在提示里看不全，要看全文得打开 `specs/<文件夹>/intent.md`；小改动的 intent 模板本来就短，是否需要压到提示能显示的行数以内，等第 2 条测完一起看。 同一个小改动的另一份数据（owner 01:03）：verifier 点开看是 Opus——定义里的 `model: opus` 在真实使用里生效了（主 session 当时用的什么模型没问到）。另一个 subagent 结束得很快、没看到模型；小改动里跑的是 code-reviewer 和 verifier，结束快的那个应该是 code-reviewer，它按设计跟主 session。
- 2026-11-21 · 同步项目里的模板副本（`CLAUDE.md`、`REVIEW.md`、`.claude/flow.json`）现在有两条路都通：走一个小改动（飞猫 `2026-11-21-sync-flow-templates` 走的这条，verifier 会读），或在工作分支上改完说「接受立项」（`accept.py setup` 在别的分支上只提交项目级文件，这三份在它的清单里；见 `docs/flow.md` 立项一节「以后改这三份文件」）。哪条管这类同步，待 owner 裁定。同一条记录里的另外两点（小改动的检查措辞、`template_mark` 的日期）已经改掉，见 `docs/decisions.md` 2026-11-21 最后一行。
