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
| 8 | owner 打回计划时，`ExitPlanMode` 的 PostToolUse 钩子触不触发（文档只写「工具成功完成之后运行」） | 飞猫阶段 3 的 plan 上 owner 故意打回一次，session 查 `plan-approved.txt` 有没有被写 | 打回时也触发：钩子不再写标记，plan 的批准只认「批准 plan」这句（`accept.py plan` 写同一个标记） |
| 9 | plan mode 里能不能起自定义的 subagent（`reviewer` 的预读） | 飞猫阶段 3 的 plan：session 在 plan mode 里调 `reviewer`，看它起不起得来、报告回不回得来 | 起不来：进 plan mode 之前先把草稿交给 `reviewer` 预读，再进 plan mode 定稿交给 owner |

## 试点期间

- 每个改动收尾时在 `docs/measures.md` 末尾记一行。
- 流程本身的问题当场记在下面一节，一行一条；修掉并回填规则文档之后删掉那一行。

## 试点中发现、还没处理的流程问题

- 2026-11-20 · **改 flow（一个改动一个 session，加 11-20 的模型裁定和三条待裁定）：做完，⑥ 交给 owner。** 都没有提交。owner 要做的：提交；`claude plugin validate plugin`；重跑改了 description 或 `when_to_use` 的 eval 用例——intent、spec、plan、implement、validate、close、review（`pick-spec` 的提问还是「intent 已经接受了，开始写 spec」，skill 的说法已改成「intent 写好了，开始写 spec」：改提问和重跑一起做，`docs/skills.md` 的生成段跟着重生成；11-20 这一轮没有再改 description）；把 `plugin/templates/user/model-table.md` 重新贴进 `~/.claude/CLAUDE.md`（那里还是 11-15 按步骤分模型的表）；飞猫仓库把 `.claude/flow.json` 的 `deploys` 改成 false、同步模板的 REVIEW.md（多了固定检查「New test-setup file」），roadmap 的 Status 行留到阶段 3 的分支上改；用飞猫阶段 3（博客）做第二个试点改动，数 owner 坐下来几次、中途被叫到几次，plan 上故意打回一次（第 8 条），看预读的 subagent 起不起得来（第 9 条）。
- 2026-11-20 · 高风险档留不留：先留着（回退路径、§3 必填、真实数据上走一遍）；要不要取消这一档、改成按事实触发，第二个试点改动之后按 `docs/measures.md` 的「高风险档留不留」一行再看。待 owner 裁定。
- 2026-11-20 01:00 · 试点清单第 2 条的第一份数据（飞猫，小改动「同步 REVIEW.md」的第一次点击，owner 贴的截图）：`ask` 的提示弹出来了，标题是「Hook PreToolUse:Bash requires confirmation for this command」，下面是钩子给的那句说明和 intent 的开头——标题、`Tier: small`、Problem 一段，之后是「… (+8 more lines)」，也就是提示里只显示了 intent 的前十行左右，剩下的折叠了。当时是什么权限模式、折叠的部分能不能在提示里展开，还没问到。按这份数据，intent 较长时 owner 在提示里看不全，要看全文得打开 `specs/<文件夹>/intent.md`；小改动的 intent 模板本来就短，是否需要压到提示能显示的行数以内，等第 2 条测完一起看。 同一个小改动的另一份数据（owner 01:03）：verifier 点开看是 Opus——定义里的 `model: opus` 在真实使用里生效了（主 session 当时用的什么模型没问到）。另一个 subagent 结束得很快、没看到模型；小改动里跑的是 code-reviewer 和 verifier，结束快的那个应该是 code-reviewer，它按设计跟主 session。
- 2026-11-20 01:04 · 小改动的合并提示 · 最该看的东西被折叠了（飞猫「同步 REVIEW.md」的第二次点击，owner 贴的截图）。提示先显示「Merge this small change into `main`?」，接着又是 intent 的开头（标题、`Tier: small`、Problem 一段，和第一次点击看到的一样），之后是「… (+15 more lines)」。小改动的兜底之一是「合并提示里列出改动的文件和行数，由 owner 自己看」，而文件清单排在 intent 后面，正好落在折叠掉的那 15 行里，owner 在提示上看不到。要改（建议，待 owner 点头）：`hook_pretool_bash.py` 的合并提示把改动的文件和行数放在最前面，intent 只留标题一行（第一次点击已经看过全文）；提示能显示的行数按这两次实测大约是十行，整段压到这个范围里。
- 2026-11-20 01:07 · 项目里从模板抄过去的文件落后了，没有东西提醒。改 flow 时模板改了三份项目级文件（`REVIEW.md`、`CLAUDE.md`、`flow.json`），交接和 ⑥ 里只让 owner 同步 `REVIEW.md` 和 `deploys`，漏了 `CLAUDE.md`——这是陪跑写交接时漏的。结果是飞猫同步 `REVIEW.md` 的那个小改动里，verifier 和 session 自己查出飞猫的 `CLAUDE.md` 有三处对不上（评审报告怎么发、「合并即部署」和 `deploys: false`、缺 `sync_main.py` 一行），记成了三条待办。小改动本身顺利：两次点击都弹了，verifier 跑在 Opus 上，没有发现 flow 的问题。要改（建议，待 owner 点头）：模板文件带一行版本标记，`state.py` 在项目的副本比插件里的模板旧时报一行「这几份落后于模板」，owner 再决定同步；飞猫的 `CLAUDE.md` 这三处在阶段 3 的分支上先改掉（`CLAUDE.md` 不是产品文件，可以直接在工作分支上提交）。
