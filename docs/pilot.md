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
