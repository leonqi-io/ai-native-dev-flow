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

- 2026-11-21 · 按交接改 flow（清单第 1–13 项）之后第一次用到时要看的五点，`2026-11-21-product-skill` 走完之后还剩两点：（一）交计划之前的问询：在 plan mode 里弹得出来（owner 11-22 确认，飞猫 `2026-11-21-product-skill`，他选了接着做）；选「先停」之后 session 是不是只回一行就停，还没用到；（二）UI 改动的 mock 评审——researcher 的对比列不列得全、「接受 spec」在没写确认人时拒不拒绝——这次不是 UI 改动，等下一个 UI 改动。已经看到的三点记在 `docs/measures.md` 那一行里（「不记」的一组成块出现并被整组认可；收尾检查的「to do」一项没有看到误拒；小改动的合并提示上次已看）。留下没处理的一点，待 owner 裁定：`accept.py spec` 只把 intent、spec、validation 三份提交进 `main`，`mock.html` 到合并才进——mock 评审之后它是合同的一部分，而 `main` 上的批准记录里没有它。
- 2026-11-20 · **改 flow（一个改动一个 session，加 11-20 的模型裁定和三条待裁定）：做完，⑥ 交给 owner。** 都没有提交。owner 要做的：提交；`claude plugin validate plugin`；重跑改了 description 或 `when_to_use` 的 eval 用例——intent、spec、plan、implement、validate、close、review（`pick-spec` 的提问还是「intent 已经接受了，开始写 spec」，skill 的说法已改成「intent 写好了，开始写 spec」：改提问和重跑一起做，`docs/skills.md` 的生成段跟着重生成；11-20 这一轮没有再改 description）；把 `plugin/templates/user/model-table.md` 重新贴进 `~/.claude/CLAUDE.md`（那里还是 11-15 按步骤分模型的表）；飞猫仓库把 `.claude/flow.json` 的 `deploys` 改成 false、同步模板的 REVIEW.md（多了固定检查「New test-setup file」），roadmap 的 Status 行留到阶段 3 的分支上改；用飞猫阶段 3（博客）做第二个试点改动，数 owner 坐下来几次、中途被叫到几次，plan 上故意打回一次（第 8 条），看预读的 subagent 起不起得来（第 9 条）。
- 2026-11-20 · 高风险档留不留：先留着（回退路径、§3 必填、真实数据上走一遍）；要不要取消这一档、改成按事实触发，第二个试点改动之后按 `docs/measures.md` 的「高风险档留不留」一行再看。待 owner 裁定。
- 2026-11-20 01:00 · 试点清单第 2 条的第一份数据（飞猫，小改动「同步 REVIEW.md」的第一次点击，owner 贴的截图）：`ask` 的提示弹出来了，标题是「Hook PreToolUse:Bash requires confirmation for this command」，下面是钩子给的那句说明和 intent 的开头——标题、`Tier: small`、Problem 一段，之后是「… (+8 more lines)」，也就是提示里只显示了 intent 的前十行左右，剩下的折叠了。当时是什么权限模式、折叠的部分能不能在提示里展开，还没问到。按这份数据，intent 较长时 owner 在提示里看不全，要看全文得打开 `specs/<文件夹>/intent.md`；小改动的 intent 模板本来就短，是否需要压到提示能显示的行数以内，等第 2 条测完一起看。 同一个小改动的另一份数据（owner 01:03）：verifier 点开看是 Opus——定义里的 `model: opus` 在真实使用里生效了（主 session 当时用的什么模型没问到）。另一个 subagent 结束得很快、没看到模型；小改动里跑的是 code-reviewer 和 verifier，结束快的那个应该是 code-reviewer，它按设计跟主 session。
- 2026-11-21 · 同步项目里的模板副本（`CLAUDE.md`、`REVIEW.md`、`.claude/flow.json`）现在有两条路都通：走一个小改动（飞猫 `2026-11-21-sync-flow-templates` 走的这条，verifier 会读），或在工作分支上改完说「接受立项」（`accept.py setup` 在别的分支上只提交项目级文件，这三份在它的清单里；见 `docs/flow.md` 立项一节「以后改这三份文件」）。哪条管这类同步，待 owner 裁定。同一条记录里的另外两点（小改动的检查措辞、`template_mark` 的日期）已经改掉，见 `docs/decisions.md` 2026-11-21 最后一行。
- 2026-11-21 · 观察项，先放着，owner 以后觉得有问题再裁定：小改动的合并提示里，改动的文件清单还是列不全（飞猫 `2026-11-21-sync-flow-templates` 的第二次点击，owner 贴的截图）。提示本身这次没有折叠，十行都显示出来了；列不全是因为清单最多列 6 个文件，而前 6 个里有 3 个是 `specs/` 下的验证报告，第 7 个被折成「… and 1 more file(s)」。这次 3 个产品文件正好都排在前面，没有被挤掉；改动文件多、或者路径排在 `specs/` 之后时，产品文件会落进折掉的那一行。可选的改法（都没裁）：清单只列产品文件，`specs/` 下的合成一行计数；或者产品文件排在前面。
- 2026-11-21 22:20 · 观察项，只发生一次，先不改规则，再出现一次再裁定：skill 里数据跨工具的一步，机制到试用才发现不成立（飞猫 `2026-11-21-product-skill`）。spec 的 R19 写「把页面的可见文本存到 scratch 文件夹」，skill 第 4 步是 `get_page_text` 之后存成 `saved.txt`；没有人问过文本从浏览器到磁盘经谁的手——`get_page_text` 的结果在 session 的上下文里，落盘只能由 session 重打（tianbao 约 25,000 字，uvbookings 约 30,000 字），而「事实都能在存下来的页面上找到」这条保证不能建在 session 自己的抄本上。试用在合并前抓到了，session 停下来找 owner（开头定的做不到），提议在本改动内加 R35 `receive-page`；代价是一次中途改 spec 和多一轮评审，没有返工已合并的东西。先不改规则的理由：只发生一次；spec 和 plan 两个阶段都实测等于先做一遍 POC（owner，22:18）。再出现时的改法（未裁）：只在 plan 加一处，spec 不动——skill 里数据跨工具的步骤（浏览器到文件、邮件到文件）写明机制，researcher 拿一个真实大小的输入把这一步跑一次；这是把「validation 的每条命令由 researcher 试跑一遍」的覆盖面补到不是命令的 skill 步骤上，不是新增一个阶段。
- 2026-11-22 · **按飞猫 `2026-11-21-product-skill` 走完之后的五处调整（A–E）改 flow：做完，都没有提交。** 裁定和界限在 `docs/decisions.md` 2026-11-22 最后一行。owner 要做的：在自己机器上跑 `bash tools/selftest.sh`（陪跑在云端的副本上跑过，220 条全过）和 `claude plugin validate plugin`，提交；飞猫的 `REVIEW.md` 副本落后于模板了（模板的 Severity 多了「没有边的输入」一条，标记是 `2026-11-22 f731c63`），状态报告会报一行，同步一次；飞猫「To do」现有的 61 行另做一次处置。下一个改动上第一次用到、要看的：（一）spec 里有没有把识别、解析类的需求写成三样，verifier 对清单之外的写法是不是报成 Nit、合成一条；（二）有给人读的输出时，样例是不是在写代码之前出的、「接受 spec」在确认人空着时拒不拒绝，结尾还问不问语言和版式；（三）遗留项进 roadmap 是不是一条需求一行，「To do」涨了几行；（四）「做成什么样」那一屏有没有「中途要你在场」一行、plan 有没有把这些步骤排在评审循环之前；（五）中途说停时 `handoff.md` 是不是四段、接手的 session 是不是先读它、阶段结束时删没删。
