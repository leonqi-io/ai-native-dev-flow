# 裁定索引

一行一条。到写仓为止的裁定，原文都在 LoomCV 仓库的 `dev_flow/notes/sdd_trial_2026-10-30.md`（只追加）里，下面每组标题后面是那份笔记里的小节名。**试点开始后的新裁定直接记在本文件末尾的「试点开始后」一节，那份笔记不再追加。**

## 前提（11/13 – 11/15 上午）

- v3 只用云端订阅，本地模型和本地无人值守运行不在 v3 里。（11/13）
- 所有无人值守、调用模型的工作流（CI 里的 eval、自动 PR 评审、CI 判断步骤、Stage 6 触发循环）写成设计、不启用。用订阅登录时 `claude -p` 用订阅自己的额度；不启用的原因是项目小，以及每周额度是实在的成本。（"Decision — headless runs out of v3"，11/15 12:35；计费事实 18:1x 更正）
- 云端定时任务用的是订阅额度，是可用的路。（11/15 12:38）

## 结构（"Summary session, agenda item 1"）

- 不用内部关卡编号；阶段和 play 用 playbook 的名字，文件用 SDD 的名字。（12:56）
- skill 用平常话触发，不定义带参数格式的命令；保底启动是 skill 自己的名字，因为在插件里所以写作 `/flow:<名字>`。（13:06，15:01；前缀一事 11/15 20:0x 对官方页核实）
- 新仓 `ai-native-dev-flow`（私有），通用部分是名叫 `flow` 的插件，在 `plugin/` 下。（1.1，15:06）
- `requirements.md` 改名 `spec.md`；`validation.md` 独立；intent 在同一个文件夹；文件夹是 `specs/<日期>-<slug>/`。（1.2，15:17）
- intent 和 spec 没有 `Status` 字段，状态从 Git 读。（1.3，15:17）
- 批准点按批准的对象命名；「walk」叫 validation，「Gate log」叫 Approval log。（1.4，15:26）
- 批准记录是文件在 `main` 上的已提交版本；agent 只在工作分支提交；钩子只查存在。（1.5，15:26）
- `ticket.md` 退役。（1.6，15:26）
- Plan 和 Design 用有界的多轮问答，配两项度量。（15:17，15:26）
- 立项一章：三份项目级文件，每个项目一次，owner 提交即批准，冲突时先改 mission。（"Supplement to agenda item 1"，18:39）

## 角色和评审（"Summary session, agenda item 2"）

- 三个档位；小改动也有文件夹和两份短文件；遗留项必须有去向。（2.1，15:53）
- 小改动的确认是一次点击，合并是第二次点击；只对小改动启用。（2.1 补裁，15:59）
- 没有角色表，只用 owner；评审的 session 不是实现的 session。（2.2，17:02）
- 「步骤 → 模型」表放在用户级。（17:02）
- 核心带三个只汇报的 subagent；新的 subagent 手工做过两三次之后才加。（2.3，17:12）
- 评审三层；读 REVIEW.md 的评审在新 session 里做。（2.4，17:17）
- 个人项目的批准是 owner 自己的合并；开不开 PR 按项目定。（2.5，17:17）

## 测试和 eval（"Summary session (continued), agenda item 3"）

- validation.md 正常档六段，按谁执行来分；加 R-ID 覆盖检查。（3.1，17:45）
- 测试锁六点。（3.2，17:52）
- 「eval」分成三个名字：插件 eval、项目配置 eval、产品 eval。项目配置 eval 不定期跑，只有两种事件触发的手动用法。（3.3，18:03）
- 插件 eval 启用：手动、订阅登录、`--ablation none`、三次、只用确定性检查。（3.4，18:18）
- skill 清单就是通过用例的说明书，「测试通过的说法」由脚本生成，说法用中文。（18:22）
- 「多少次运行才可信」：三次。（3.5，18:32）

## 部署和维护（"Summary session (continued), agenda item 4"）

- 部署要求按坏发布的代价分级；唯一的硬要求是凭据在 agent 够不到的地方、由合并触发部署。（4.1，19:04）
- 代价可接受的项目，合并就是发布批准；确认里写明「合并即发布」。（4.2，19:06）
- 4.3 撤销：内容类 skill 是工作流程，不是开发流程，不动。（19:11）
- 入口是 roadmap 的「To do」段，只放未决条目；另有「Known limits」段。（4.4，19:32）

## 浏览器（议程第 5 项）

- 三项内置浏览器实测推到试点第一天；测完之前浏览器一次只给一个 session 用。（19:55）

## 写仓时的裁定（"Repo-writing session — start"，11/15 21:03 – 21:26）

- 小改动不另开 session 评审，由 verifier 出结论；带四条兜底。（第 1 条，21:03、21:21）
- 模板放 `plugin/templates/`，顶层不留第二份。（第 2 条，21:13）
- 档位记在 intent.md 的 `Tier` 一行。（第 3 条，21:13）
- 给脚本读的项目设定放 `.claude/flow.json`，五项；有这个文件才算启用流程。（第 4 条，21:21）
- 核心不带「禁止用 shell 改写文件」的钩子；试点里数一项，出现绕过再加。（第 5 条，21:26）
- `docs/` 用中文；插件里的 skill、subagent、脚本注释和模板用英文。（第 6 条，21:26）
- 本文件是裁定索引；试点开始后新裁定记在这里。（第 7 条，21:26）
- 用户级模型表带「开场对一下当前模型，不符就提示一次」。（第 8 条，21:26）
- subagent 的定义里不写模型，跟主 session 的模型走：researcher 是 Opus，code-reviewer 和 verifier 是 Sonnet，小改动的评审结论因此由 Sonnet 出。先接受；试点里出现「小改动后来被判为行为变了、而 verifier 当时没报」，第一步是在用户级设 `CLAUDE_CODE_SUBAGENT_MODEL=opus`，不改插件。（"Repo-writing session — after the close"，22:10）

## 试点开始后

（从这里往下追加：日期、裁定、原因。）

- 2026-11-16：立项也跑问答。`setup-project` 起草三份项目级文件后按有界多轮问答来；完整性清单不套用，只在「这一轮没让草稿发生任何变化」时停。plan.md 和评审不跑问答。原因：准备飞猫立项时发现 skill 第 3 步只写了「先出草稿、每问带默认」，没有分轮、一轮的问题一起给、每裁一条重列剩余和停止条件；完整性清单是给单个改动写的。plan 不跑：需求在 spec 里已问完，剩下的实现选择一次列出来裁；评审不跑：要的是新 session 独立下结论。（09:39；规则在 `docs/flow.md` 立项、Plan 两章）
- 2026-11-16：立项问答的两处补充，都按默认。停下时还没定的问题记成 roadmap「To do」段的一行，不再问（立项时还没有 concern 清单）；`.claude/flow.json` 的五项并进同一轮问答，每项按仓库现状给默认值（原来是逐项问、不带默认，等于 skill 里留着第二种问法）。（20:56）
- 2026-11-17：批准改成在对话里说一句固定的话，所有档位可用：「接受立项」「接受 intent」「接受 spec」「批准 plan」「确认合并」。整条消息只有这句话才算；`UserPromptSubmit` 钩子直接运行 `accept.py` 或 `merge.py`，模型不参与判断。小改动的两次点击保留，终端里粘贴那一行留作退路，agent 自己调这两个脚本照旧被拒绝。取代「正常档和高风险档的提交由 owner 在终端里粘贴命令」和「正常档一次点击，试点之后再决定」。原因：飞猫立项时签字、接受、确认的步骤太繁琐，要等 agent 给命令、再开终端执行。没做成 skill：skill 由模型选，模型也能自己调用，批准就不再是 owner 的动作。已知界限见 `docs/hooks-and-scripts.md`。（09:26）
- 2026-11-17：开 PR 的项目，「确认合并」由脚本合并 PR（`gh pr merge --merge`），再把本地 `main` 快进到 `origin/main`、切过去、删分支；owner 在 GitHub 页面上合并之后说同一句话只做清理。`gh pr merge` 由 agent 调用会被拒绝（原来没拦）。真实 GitHub 上未核实，进试点清单。（09:26）
- 2026-11-17：`tech-stack.md` 改名 `decisions.md`，不拆成两份。原因：飞猫立项写出来的 120 行里技术栈只占几行，其余是页面类型、三条流程、内容怎么进 `main`、部署；模板本来也是 Decisions、Cost of a bad release、Deployment 三段。偏离「文件用 SDD 的名字」那一条，只此一处。飞猫要迁移一次。（09:26）
- 2026-11-17：部署方式按项目定，取代 4.1「唯一的硬要求」。立项时在 decisions.md 的 Deployment 段回答五项（怎么发布、什么触发、凭据在哪和谁够得到、怎么回退、发布由什么批准）；「合并触发发布、凭据 agent 够不到」降为推荐做法。合并不触发发布的项目 `deploys` 设 false，合并提示不带「Merging publishes to production」，发布批准是 Deployment 段写明的那个动作。原因：飞猫的备用发布（agent 在 owner 已登录的浏览器里经 cPanel 上传）不符合硬要求，却是合理的选择。（09:26）
- 2026-11-17：立项验收带整条 `setup` 分支（`main` 前移到 `setup` 的头），交接前把进 `main` 的文件清单给 owner 看，不设拒绝；在别的分支上修订项目级文件，照旧只提交那几份。原因：飞猫立项时写的 mockups 盘点留在了 `setup` 分支上，`main` 上的 CLAUDE.md 指向它，成了空指针。（09:26）
- 2026-11-17：合并和立项验收之后，脚本把检出切到 `main` 并删掉工作分支（本地和远端）；切不过去时不删，打印要手工做的两行；状态报告加一种状态「Merged」。不要求打开 GitHub 的自动删分支。原因：已合并的分支越积越多，容易误切回去接着干；`setup` 分支因为批准提交是另一组提交号，`git branch -d` 还会拒绝。（09:26）
- 2026-11-17：加 `sync_main.py`，把本地 `main` 快进到 `origin/main`，agent 可以直接跑；「确认合并」只管有改动文件夹的分支。原因：飞猫的例行内容走流程之外的 PR，而钩子拦了在 `main` 上的 `git pull`，PR 在 GitHub 上合并后本地 `main` 更新不了。批准已经在 GitHub 上发生，同步不带新的决定。（09:26）
- 2026-11-17：有远端的项目，`main` 一动就推，推之前先把 `origin/main` 快进进来；`deploys` 只决定合并提示里那一行。前半（合并后有 origin 就推）是裁定的默认；后半是实现时补的，owner 11/17 收尾时确认：批准文件的提交和待办行的增删也推。原因：只推合并的话，本地 `main` 上没推的待办行和 GitHub 上合并的内容 PR 会让两边分叉，快进同步做不成，只能回终端手工合并。代价：由推送触发流水线的项目，每次批准和每条待办也触发一次。（实现时；后半 11/17 收尾时确认）
- 2026-11-18：插件 eval 的额度可以忽略，不减用例、不减运行次数。实测：`claude plugin eval plugin --case pick-continue --runs 1 --ablation none` 在 plan 登录下得分 1.00，24 秒，eval 自报 $0.20；用量页按 1% 取整，看不出这一次。全套 11 个用例各跑一次约合 $2.2。原因：owner 判这个量可以忽略。（试点清单第 3 条，测完删去）
- 2026-11-18：试点前的插件 eval 全套跑完：11 个用例全部通过（默认每例 3 次，33 次全是 1.00），共 540 秒、eval 自报 $4.25；`docs/skills.md` 的生成段已按这次结果重生成。上一条里「全套约 $2.2」按每例 1 次估，实际默认是 3 次。
- 2026-11-18：开发只走本地，插件用 `claude --plugin-dir <本仓>/plugin` 加载；云端 session 和 Cowork 不用，试点清单第 1 条不测、删去。原因：owner 判本地够用，不值得为云端多一套加载方式。查过的文档事实：云端 session 没有 `/plugin`，本机装的插件和仓库 `.claude/settings.json` 里 `enabledPlugins` / `extraKnownMarketplaces` 打开的插件都不加载；剩下的「把插件放进项目 `.claude/skills/`」一条没测。
- 2026-11-18：批准句钩子在真实 session 里可用。飞猫 `2026-11-18-scaffold-content-model` 上，新开的 Sonnet session 第一条消息说「批准 plan」：钩子跑了 `accept.py plan`（plan.md 进 `main`，提交 630cd05，已推到 origin）；结果以 `UserPromptSubmit says:` 一段显示给 owner；agent 收到结果，用一行报告后加载了 `implement` 并开始做。（owner 18:08 报告并附截图；试点清单第 5 条的前半，测完删去；三种不是 owner 打字的 prompt 的文本还没测，留在清单里）
- 2026-11-19：试点清单第 6 条实测通过，从清单里删去。飞猫 `2026-11-18-scaffold-content-model`（走 PR 的项目）上 owner 说「确认合并」：PR #1 并入 `main`（737deb1），合并前的收尾检查六项通过，本地 `main` 跟上，工作分支本地和远端都删了。（21:47）
- 2026-11-19：**走完飞猫第一个改动之后改形状：一个改动一个 session，owner 坐下来两次。** owner 的判断：做一个样例脚手架切了记不清多少个 session 和模型，多数时候只是把提示词从一个 session 复制粘贴到另一个，报告长、记不住各自指向什么；仔细读每份报告不如自己写，不读只转贴则验收没有价值。原因归到一处：「评审的不是实现的」这条独立性是靠 owner 在 session 之间传话实现的。改成：开头坐下来一次（说要做什么、答问、确认事实值、认可「做成什么样」，接着终审 plan），结尾坐下来一次（看一屏结果、答只有他能答的判断题、说「确认合并」）；中间的评审、修复、复核、清点由 session 内部的 subagent 和脚本做，报告落盘，owner 不读；中途只在三种情况找他（开头定的做不到或互相矛盾；同一个问题修了两轮不过；要做开头没授权的不可逆的事）。取代 11/15 的「评审在新开的 session 里做」对正常档和高风险档的硬要求、四个批准点、高风险档 plan 的二读。规则文档和插件按 `docs/pilot.md` 里的 plan 改，改完之前以本条为准。（22:02 – 22:30）
- 2026-11-19：plan 保留 owner 的终审，在同一个 session 里做。对照 playbook 的 plan how-to：从起草到实现是同一个会话，追问（可能弄坏什么、哪一步风险最大、有哪些备选方案没选）是工程师本人做的；「没看过这段对话的工程师只凭计划就能实现」是停笔的标准，不是换 session 的程序。plan.md 开头一节写这三个追问的答案和要裁定的点，owner 读这一节、追问到满意、批准，批准之后同一个 session 接着实现。原因：这是动手之前工程师最后一次了解要怎么做。（22:27）
- 2026-11-19：批准合成三次：「做成什么样」（intent、spec、validation 一起接受）、plan、合并。小改动的两次点击不变。（22:38，owner 对列出的八条「全批默认」，以下七条同）
- 2026-11-19：批准之后默认接着做，owner 随时可以打断；不做停顿标记。取代 11/18「默认停、带『并继续』才往下」。
- 2026-11-19：测试放行不再问 owner。锁开着时改测试文件，agent 记一行放行记录，评审的 subagent 查测试有没有被削弱，改过哪些测试列在结尾那一屏。小改动的两次点击和 roadmap 待办行的删除、移动照旧询问。
- 2026-11-19：高风险档和正常档同一个形状，评审的 subagent 用更强的模型；新开 session 的评审变成 owner 想要时才用的选项，不是固定步骤。档位按出错的代价定，不按触发词。
- 2026-11-19：模型：正常档和高风险档的主 session 用 Opus，小改动用 Sonnet，一个改动中途不换。取代模型表里按步骤分模型的四行。
- 2026-11-19：核心不带「禁止用 shell 写文件」的钩子。飞猫脚手架的 Build 几乎全是 shell 写的（`docs/measures.md` 那一项「出现一次就加」因此不照做）；合并前按差异查的两项（测试范围、plan 对照）实测对 shell 写的文件管用。
- 2026-11-19：`deploys` 表示「现在合并会不会发布」，流水线接上的那个改动里才改成 true。原因：飞猫设了 true 而流水线还不存在，PR 第一行和合并脚本的提示都说了不实的话。
- 2026-11-19：结尾的判断题 owner 可以说「这题不判断」：脚本记一行，并在 Leftovers 留一条带去向的遗留项，收尾检查不拦。
- 2026-11-19：查过的文档事实（code.claude.com 的 sub-agents、model-config、hooks、tools-reference 页）：subagent 定义的 frontmatter 可以带 `model` 和 `effort`；Agent 工具调用时也可以带 model；`ExitPlanMode` 是「给出计划、请用户批准后退出 plan mode」的工具，需要许可，plan mode 里计划先写到磁盘上的一个文件，不在仓库里。
- 2026-11-19：改 flow 的 plan 和它的三个裁定点 owner 已批准（23:09）。（一）plan 在 Claude Code 的 plan mode 里起草，owner 接受计划那一下就是批准：`ExitPlanMode` 的 PostToolUse 钩子里由脚本把被批准的计划全文原样写成 plan.md 并记一个批准标记，写入钩子认标记才放行产品文件；plan 的批准记录不再是「plan.md 在 `main` 上」；「批准 plan」这句留作退路。原因：陪跑原先提的「不用 plan mode、写成文件说一句批准」是 V2 的做法，和 playbook 不符，也和「不带 shell 钩子」那条的理由（plan mode 自己不让写文件）矛盾。（二）「接受 spec」一句同时接受 intent、spec、validation，「接受 intent」在正常档退役。（三）评审行由实现的 session 调脚本记，脚本要求报告文件已落盘；接受「它可以记错」这个界限。
- 2026-11-19：避免上下文过长靠拆小，不设 R 条数的提问线（owner 23:07：只是在想办法，没必要硬加）。`spec` skill 里只写定性的拆分判断；拆出来的是独立的改动；`docs/measures.md` 每个改动多记 R 条数、改动的文件数、有没有发生上下文压缩。
- 2026-11-19：查过的文档事实（code.claude.com 的 hooks 页，读了前三分之二）：钩子输入带 `permission_mode`，取值包括 `plan`；`ExitPlanMode` 的 PostToolUse 里 `tool_response` 有 `plan` 和 `filePath` 两个字段，装的是被批准的计划；PostToolUse 在工具成功完成之后运行；手动拒绝许可时 PermissionDenied 不运行，PostToolUseFailure 也不因许可被拒触发。「打回计划时 PostToolUse 不触发」没有明说，留到第一次真实使用里看。
- 2026-11-20：**模型和档位脱钩；高风险是 session 的判断，不是决定。**（owner 2026-11-19 23:59 的裁定，00:05 更正、00:14 补充）默认正常的工作都用 Opus；模型表只是参考，模型由 owner 选。档位由 session 提、owner 在「做成什么样」那一屏上认可，说一个词就能改；「数据形状」只算已有真实数据的存储或输出形状（飞猫的脚手架因为动了数据形状被判成高风险，是误判：规则写成了触发词）。干活和核查分开：干活默认 Opus，效果不理想（测试不过、卡住、同一个问题修了两轮）时停下说明，owner 先加 effort 再决定换不换，换就在同一个 session 里 `/model`；核查（verifier、reviewer）固定用 Opus，写在两个 subagent 的定义里，因为核查的效果不好看不见——漏报的评审和干净的评审都报 0 条 Important（飞猫的 verifier 第一次报 0，第二次才查出不存在的日期会崩溃）。code-reviewer 和 researcher 不算核查，跟主 session。流程只在两种时候建议 Fable：session 判断出错代价高（在那一屏上带着事实建议一次，不只给「高风险」这个标签）；加了 effort 仍然不理想。owner 接受了核查用 Fable，就在调用里指定 `model: fable`。取代 11-19 的「高风险档的评审 subagent 用更强的模型」「一个改动中途不换模型」，以及 11-15 的「subagent 定义里不写模型」和「小改动的评审结论出自 Sonnet，出现漏报再设 `CLAUDE_CODE_SUBAGENT_MODEL=opus`」。陪跑检查里「把 `model: fable` 挪到模型表」那一点作废。高风险档本身（回退路径、§3 必填、真实数据上走一遍）先留着，要不要取消、改成按事实触发，第二个试点改动之后再看。
- 2026-11-20：查过的文档事实（code.claude.com 的 sub-agents 页「Choose a model」）：subagent 的模型按这个顺序取第一个：调用时传的 `model`（只收别名，如 `fable`）、定义里的 `model`、`CLAUDE_CODE_SUBAGENT_MODEL`、主 session 的模型。所以调用时指定盖得过 frontmatter，`CLAUDE_CODE_SUBAGENT_MODEL` 盖不过；另设 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 时定义里的 `model` 和调用时传的都被忽略。hooks 页：subagent 里的工具调用照样触发 PreToolUse 和 PostToolUse，输入带 `agent_id` 和 `agent_type`。
- 2026-11-20：plan 的钩子和退路一致（陪跑检查的第 1、2 点，owner 同意照改）。plan mode 里接受的计划缺模板的形状（「For the owner」等必备标题）时，钩子不记批准，让 session 回 plan mode 补齐再交，和「批准 plan」的形状检查一样；原来是照样记、只附一句 NOTE，这样「接受 spec」之后、真正的 plan 之前在 plan mode 里接受的任何计划都会被记成 plan 的批准。钩子在 subagent 里触发时（输入带 `agent_id`）不动作，和批准句的钩子同一条。
- 2026-11-20：三条待裁定的按陪跑检查的建议定（owner 2026-11-20）。（一）Watch figure：plan 批准之后 spec 改动变多时，建议 owner 让 plan 的预读用 Fable；换的是 subagent 的模型，主 session 不换。（二）测试放行记内容：放行行记文件当时内容的 sha256，收尾检查要求最新一条放行行的哈希等于文件现在的哈希，放行之后再改就要再记一行；没人被询问，多记一行不费事。新建的配置类测试文件（`conftest.py`、测试运行器的配置、共用的 fixture）交给 REVIEW.md 的固定检查「New test-setup file」读，不加设定。（三）评审行记被评审的提交（`at <短哈希>`，`record.py review` 在产品文件有未提交改动时拒绝），收尾检查拒绝「这个提交之后产品文件又变了」。原因：飞猫第一个改动里 verifier 和评审跑在最后一批改动之前出现过三次，这一项不占 owner 的时间。
- 2026-11-20：改 flow 之后插件 eval 全套重跑：11 个用例全部通过（每例 3 次，33 次全是 1.00），550 秒，eval 自报 $4.69。`pick-spec` 的提问先改成了 skill 里的新说法「intent 写好了，开始写 spec」再跑；`docs/skills.md` 的生成段按这次结果重生成。（owner 00:51 跑，01:06 贴结果）
- 2026-11-20：**「另一双眼睛」进 subagent；「照着做得出来吗」这一类题不问 owner。**（owner 21:05 同意，21:09 确认陪跑复述的三条）（一）owner 想让人评价 session 自己写的东西时，在同一个 session 里让它起一个没有上下文的 subagent，带一个具体问题去读；不另开对话。（二）「一个只拿到这份文档的会话能不能照着做」这一类题不是判断题：写成清点步骤，由一个只拿到文档和一份样例的 subagent 实际做一遍，产出交给机器检查。（三）普通的问答、解释、裁定不变，仍然是 owner 和实现的 session 直接谈，不经过 subagent。原因：飞猫 `2026-11-20-blog` 结尾的判断题 J1（读 `site-version.md`，flightcat 那边只看它能不能写出网站版本）问错了对象——owner 只读文档答不出来，三处缺口是陪跑对着字段定义找到的，而这份文档过了 3 轮 reviewer、6 轮 verifier 都没报；owner 当天把 session 的输出拿到陪跑这边讨论了 7 次，试点之后没有陪跑。skill 和规则文档还没改，改法记在 `docs/pilot.md`。
- 2026-11-20：试点清单第 8 条实测通过，从清单里删去。飞猫 `2026-11-20-blog` 的 plan 上 owner 用「Tell Claude what to change」打回一次，打回之后读仓（19:17）：没有 `plan-approved.txt`、没有 `plan.md`、没有新提交——**打回时 `ExitPlanMode` 的 PostToolUse 钩子不触发**。19:20 他接受之后钩子才把计划原样写成 plan.md、和批准标记一起提交（b337968），标记里的 sha256 和文件对得上。退路（「批准 plan」这句）留着不动。界面上的事实：这个版本的 Claude Code 交计划时给三项——「Yes, and use auto mode」「Yes, manually approve edits」「Tell Claude what to change」，第三项回车是打回，在第三项上按 shift+tab 是带着反馈批准。（2026-11-21 更正：是先在第三项的输入框里打字、再按 shift+tab，才是带着这段话批准；框是空的就按 shift+tab 是直接批准——飞猫 `2026-11-21-article-template` 上框空着按了，批准直接生效、进了 auto mode。带着一段话批准时钩子照常记不记批准、这段话交不交得到 session，还没实测。）
- 2026-11-20：试点清单第 9 条实测通过，从清单里删去。飞猫 `2026-11-20-blog` 的 plan：session 在 plan mode 里起了插件自己的 subagent（`flow:researcher` 重新核对代码事实，`flow:reviewer` 做预读），都起得来，报告回到对话里、没有写文件；预读报了 2 条 Important、6 条 Nit，并进计划之后才交给 owner（session 21:16 的说明，owner 转述）。退路（进 plan mode 之前先预读）不用启用。同时留下一条没核实的：plan mode 的只读限制管不管 subagent——`reviewer` 有 Bash，这次没改仓库是它自己的说法，不是 plan mode 保证的；另外 plan mode 自己的指示写的是探索阶段只用 Explore 类型的 subagent，session 用的是 flow 的两个。这一条作为新的第 10 条进试点清单。
- 2026-11-20：**第二个试点改动留下的九处建议，owner 全批（21:29「都按你建议批」，对着陪跑列的表）。**（一）待办行的删除只走 `roadmap_edit.py`：加一个原因给「不是产品文件、已经在工作分支上直接改掉」的情况，写入钩子拒绝在工作分支上删改「To do」段的行。（二）spec 模板第一行去掉 intent 的提交哈希，只留路径。（三）拆出来的部分写进 roadmap 的计划阶段，不进「To do」；「不是产品、直接在工作分支上提交」的清单补上本改动的裁定带来的计划阶段和 `specs/decisions.md` 的修改。（四）没改的发现多一个去向「不记」：代价可以忽略的 Nit 不进 roadmap，在结尾那一屏上成组给 owner 过目。（五）`plan` skill 交计划时告诉 owner 界面上哪一项是打回、接受选哪一项。（六）`todo_add.py` 的「谁提的」可以按行给。（七）小改动的合并提示把改动的文件和行数放最前面，intent 只留标题。（八）模板文件带版本标记，状态脚本在项目副本落后时报一行。（九）高风险档留不留：没有新的建议，还是「先留着」；这次的数据是正常档、owner 没改档位、session 没建议 Fable。原因和事实在 `docs/pilot.md` 各条里；skill、脚本、模板和规则文档还没改，交接在 `docs/pilot.md` 的「改 flow 交接」。
- 2026-11-20：**下一个改动（飞猫阶段 3 的 B，文章模板）不做全程陪跑，合并之后事后核对一次。**（owner 21:35 同意陪跑的建议，并加一个例外）解释、裁定、另一双眼睛都问实现的 session；owner 只记六样交给事后核对的 session（见 `docs/pilot.md`「下一个改动怎么核」）。两个例外：flow 自己坏了（钩子不触发、脚本报错、卡住走不下去）当场叫人；owner 对这个改动的流程有疑问时，开一个「半陪跑」的 session，只讨论有疑问的那一部分。原因：这次陪跑自己成了传话的一环（7 次），还影响了三处判断；B 要测的是 flow 自己接不接得住。
- 2026-11-21：试点清单第 10 条（plan mode 的只读限制管不管它里面起的 subagent）无限期延后，从清单里删去。owner 14:48：他不会在 plan 里要 subagent 写文件，这一条只防 agent 擅自做主，优先级很低。陪跑补的事实：plan mode 是否约束 subagent 仍未核实（`reviewer`、`researcher` 都有 Bash，没写东西是它们定义里「只报告」的约束，不是 plan mode 保证的）；兜底是两次真实使用里 plan 批准时工作区都干净（B 11:14 读仓），以及合并前的 plan 对照和测试范围检查会查到计划外的文件。
- 2026-11-21：**plan 批准之后可以选停，由 session 在交计划之前弹一次问询。**（owner 在改 flow 的 session 里裁）reviewer 预读之后、交计划之前，session 用 AskUserQuestion 问一次：批准之后接着实现（默认），还是先停。选了先停，钩子照常记批准，session 只回一行「plan 已提交 <哈希>」就停，owner `/clear` 之后说「继续」。和 11-19「批准之后默认接着做、不做停顿标记」的关系：默认没变，这是流程里唯一一处可以选的停，由 owner 当场选，不由脚本卡住。没采用的三种：owner 口头说一句「批准后先停」（要他记得说，还要在 skill 里为一句话加约定，owner 判多余）；在对话框第三项里带着话批准（没实测过，而第三项加回车是打回）；在 Claude Code 的接受对话框里加一个选项（对话框是自带的，插件加不了；自带的「清上下文并接受」有公开 issue 报它被当成打回）。代价：每个正常档和高风险档的改动多点一次。「核查用 Fable」的约定清上下文之后不在盘上，owner 判现在不用管（他目前用 Opus 核查，没发现不足）。数据在 `docs/measures.md` 的 `2026-11-21-article-template` 一行（批准时 24%，清掉之后接得顺）。
- 2026-11-21：**UI 改动在 Design 阶段多一步「mock 评审」，由脚本把关。**（owner 在改 flow 的 session 里裁；他的判断：这应该是 design review 的关键流程内容，不是往那一屏上补一行）定基准（mock 取代的旧 mockup 或现有页面）；researcher 逐块对比，不由写 mock 的 session 自己列；每处差异要么对得上一条需求或裁定，要么改 mock；有人看过 mock 本身并确认，spec 的「Mock」一节记确认人；改动文件夹里有 `mock.html` 而没有确认人时，「接受 spec」和收尾检查拒绝；之后 mock 是合同，结尾的判断题不重开版面。规则不写「等谁确认」的专门流程（这套流程不只用在飞猫上），只记是谁确认的。原因：飞猫 `2026-11-21-article-template` 的 mock 随 spec 一并接受，页脚和旧 mockup 不同没人看到，实现之后多了一轮修复。代价：每个 UI 改动 owner 在开头多一次坐在屏幕前。「实现和 mock 一致吗」不出成判断题：它是没有上下文的 subagent 做得了的，verifier 本来就在做。
- 2026-11-21：两个改动在两个 worktree 里交错着走，写进 `docs/flow.md` 的 Build 一节，标「v3 试行」，句子里写明未实测、指向试点清单第 11 条。（owner 按建议裁）不放「只写不启用」的原因：owner 打算下一个改动就试，而仓里没核实的做法都是写在试行里、另挂一条试点清单带退路；这一条不动 skill 和脚本。
- 2026-11-21：**按交接改 flow 做完（清单第 1–13 项）。** 11-20 批的九处照记录改；裁定没盖住、owner 按建议定的四点：（一）在分支上新增「To do」行也拒绝，不只删和改；正在解合并冲突的那次编辑不拦。（二）收尾检查加一项「to do」：分支自己动过「To do」段（和分支点上的 `main` 比）就拒绝——写入钩子看不到 shell 的改动，这和 11-19「不拦 shell、合并前按差异查」是同一个思路。（三）「不记」的发现留在 validation.md 的「Not recorded」一节，owner 整组认可用 `record.py ruling` 记一行，不加脚本检查。（四）带版本标记的模板是 `CLAUDE.md`、`REVIEW.md`、`flow.json` 三份；标记是日期，改模板的人在同一次改动里改它（本仓 `CLAUDE.md`），没有脚本查这一点。没有改任何 skill 的 description 或 `when_to_use`，eval 不用重跑。自测 211 条全过。
