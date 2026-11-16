<!-- 单向快照：由 Claude Doc「AI-native SDLC Playbook 课堂问答笔记」导出为 Markdown，导出时间 2026-11-15（America/Toronto），文档版本 rev 7。
原件：https://claude.ai/artifact/Us7wJmHdS3d7RfjBqhEa2W （可编辑的正本在那里；这里只在原件有实质改动后重新导出）。 -->
# AI-native SDLC Playbook 课堂问答笔记

Nov 14, 2026 · @Leon

这份笔记收的是学习这门课时你提出的问题和得到的回答，按节排列，和[复习材料](https://claude.ai/artifact/Smie2S3SnsLDHB384HW2sC)配合使用：复习材料讲课程本身，这里讲当时没懂的地方。每条回答末尾标「→ v3」的，是这条问答对新流程的结论；完整的 v3 记录在 `loomcv/dev_flow/notes/sdd_trial_2026-10-30.md` 第 4 节。第 1 节是总览，没有问答；第 14 节是结语，也没有问答。

## 第 2 节 · Capture as intent.md

（这一节的问答是 11/13 上午在课程页面上问 Gemini 的，中午对照原文核对过。）

**intent 放在哪里？** 放在使用它的产品仓库里的 `intent/` 目录。只有一个 intent 要跨很多仓库时，单独开一个 intent 仓库才值得。→ v3：每个项目仓库自己放。

**谁批准，留什么证据？** 证据是已提交的 `intent.md` 和 Git 历史（作者、时间、修改记录），不是聊天记录。product owner 接受就是 merge，拒绝就是关闭 review。

**草稿和已批准怎么区分？** 修改期间放在开着的分支或 PR 上，每次修改是一个新 commit。批准不是文件里的状态字段，merge 才是。Gemini 曾说 merge 前要把字段改成 `Status: approved`，这一点课程里没有，也和它自己前一个回答矛盾。→ v3 待定：模板里的 `Status` 字段去掉，还是只作信息保留。

**merge 之后 intent 还要改怎么办？** 再开一个 PR，经过 owner。

**怎么衡量？** 领先：从第一次对话到 `intent.md` 提交的时间。滞后：存活率 = merged ÷（merged + closed）；同一个改动的 `spec.md` 提交之后，`intent.md` 又被改了几次。

**示例 intent 长什么样？** 约 12 行：头部（作者、状态），然后 Problem（带数字）、Proposed outcome（用户之后能做什么，不写方案）、Affected users and systems、Constraints、Open questions。课程第 1 步要求写 out of scope，但示例里没有。

## 第 3 节 · Requirements and design

**某个领域没有对应的 skill 怎么办？** 先找已有但没包装成 skill 的政策（CLAUDE.md 里的锁定决定、技术栈、写作规则）。都没有的话，spec 要把「没有政策覆盖」单独列为一类 concern，交给 owner 决定。同类决定出现 2–3 次后，再整理成 skill，不提前写。

**通用的 skill 和项目规则要不要分开？** 要，按「谁拥有这条规则、它适用多广」分三层：流程 skill（写 intent / spec、关卡步骤、模板）、组织级政策（对你所有项目都成立，比如密钥不进仓库）、项目级政策（品牌、UX、锁定的架构）。项目规则可以收紧组织基线，不能放松。

**政策和 skill 是一回事吗？**（你指出 Kitty 的导航顺序、营业时间、「不写 24/7」是政策，不是 skill） 不是。政策是规则本身，归政策 owner，记在项目的政策文档里，不写进配置。配置和内容文件是满足政策的实现。skill 只是一种包装：在 Claude 生成新内容时把相关规则摆到它面前，指向政策记录，不复制。不是每条政策都要做成 skill。

**第 2 步的「手动 → 命令 → 触发」是什么意思？** 三个成熟度：先手动跑，直到 prompt 稳定；再固化成大家共用、有版本的 slash command；最后让 intent 的 merge 自动触发一个无人值守的任务，写出 `spec.md` 并开 PR。无人值守时 Claude 不能提问，所有疑问都必须写成 concern。→ v3：个人项目停在第二级（`/write-spec`）。

**spec 为什么要和 intent 放在一起，又分成两个文件？** 放在同一个目录，后来的人能同时看到「要什么」和「决定了什么」。分两个文件，是因为作者不同、批准的时机不同；合并会分不清哪个决定回答了哪个要求。

**一个 `spec.md`，还是我们现在的 requirements + validation 两个文件？** 我的意见是保留两个：读者不同（requirements 给你在 G1 定，validation 主要给 planner 和评审）、生命周期不同（requirements G1 后稳定，validation 一直长到结束）、度量更干净。可以把 requirements.md 改名叫 spec.md。→ v3 待定。

**示例 spec.md 长什么样？** 约 30 行：头部（来自哪个 intent、状态、用了哪些 skill）；R1–R4 四条原子、可测试的需求；设计；约束对照表；intent 里开放问题的处理；编号的 concern，每条写清问题、为什么定不了、建议和 owner。三条 concern 正好是三类：约束导致的范围排除、两个 skill 互相矛盾、未验证的假设。和我们的 requirements 比，我们缺 intent 和 skill 版本的头部、开放问题的对照、「没有政策 / 政策矛盾」这两类 concern，以及集中的设计部分。

## 第 4 节 · Claude Code plan mode

**具体怎么执行？**

1. 用 plan mode 打开 session，接受计划之前只读不改（Claude Code 里用 Shift+Tab 切换，或启动时加 `--permission-mode plan`）。
2. 给它 `intent.md` 和 `spec.md`，要求列出要改的文件、工作顺序、用来证明的测试。
3. 追问：会弄坏什么、哪一步风险最大、否掉了哪些方案。目的是趁改方向还只是改文档的时候，把 Claude 没说出来的假设问出来。
4. 反复改，直到一个没看过这段对话的人也能照着实现。
5. 先提交 `plan.md`，再写代码，评审时可以拿 diff 对照计划。
6. 接受后 Claude 实现，常常一次完成。
7. 实现偏离计划时，在同一个 commit 里更新 `plan.md`，可以用 hook 强制。

→ v3：「陌生人也能实现」作为 G2 的通过标准；「要改的文件」是一份清单，可以做机械的偏离检查：改了清单外的文件，或清单里的文件没动，而 `plan.md` 又没同时更新，就拦下。

**和我们 trial 的实际情况对得上吗？** 对得上：plan 作为评审对象、批准和修改有记录、一次实现就通过（Phase 0、1、2a、2c-0 都是无人值守 15–20 分钟完成）。返工来自 G4 走查发现的 UI 布局和措辞，是计划本来就预见不到的，这支持「先做 mock」而不是「计划写得更重」。课程建议我们改的：用工具（plan mode）强制关卡，而不是靠 session 自己停下；计划保持最新，而不是叠加修订；CLAUDE.md 要精简。

**示例 plan.md 长什么样？** 约 15 行：要改的文件、工作顺序（每步引用 R 编号）、风险（引用 spec 的 concern）、证明（哪个测试覆盖哪条 R，截图对得上 mock）。我们 F-6 的 plan 有 260 行，一部分重量是为本地模型写到签名级别造成的。

## 第 5 节 · The CLAUDE.md

**这些不都是常识吗？哪里和我们不一样？**（11/13 量过）

1. **大小**：LoomCV 的 CLAUDE.md 有 154 行但 94 KB（单行长达 5300 字符，每次 session 开始约读 2.3 万 token），另有 36 KB 的 AGENTS.md 重复同样的约束。大部分是逐个 ticket 的状态历史。课程要求一页以内。
2. **没有 Commands 段**：ruff、pytest、`pipeline …` 命令散落在各处。课程把命令放在最前面。
3. **纠正写在哪里**：我们的纠正大多写进了 Cowork 项目记忆（几十个 HARD RULE 文件），不在仓库里、不经过代码评审，而且犯错的 Claude Code 实现 session 读不到。课程把纠正放在每个 session 都会读的地方。
4. **几次犯错才写**：我们常在第一次就写规则；课程是第二次才写，避免偶然的失误占用每次 session 都要付的上下文。

→ v3：项目 CLAUDE.md 模板 = Commands · Conventions · Architecture · Things Claude gets wrong · 指针，一页以内；状态放 roadmap，历史放各 phase 目录；代码相关的纠正按「两次规则」写进仓库的 CLAUDE.md。

## 第 6 节 · Skills as institutional knowledge

**skill 和 hook 是什么关系？** skill 是建议性的，让违规变少，但强制不了。必须做到的规则，要再加一层确定性的检查：一个脚本用在三处，skill 让 Claude 跑它，hook 在编辑匹配的文件时跑它，CI 在 PR 上跑它。只管 Edit / Write 的 hook 拦不住用 shell 命令改文件，而我们的 `no_script_writes.py` 正好从另一头堵住了这个口子。

**我们有哪些现成的候选？**

- LoomCV 的「用户看到的文字用大白话」：F-6 的 G4 修复轮和很多 LK 发现都是措辞。做成 skill，再加一个脚本在 UI 文字里查算法术语。
- 飞猫的「不写 24/7、不超出营业时间做承诺」：政策归 Kitty，生成页面和推文时用 skill，部署前用脚本查生成内容。

我们现有的 `ln-scan`、`fc-*`、`flightcat-*` 是流程类 skill（一套操作步骤），不是政策类 skill。→ v3 要把这两类区分开；每个政策 skill 写明 owner 和来源文档；写 skill 时要测它能不能被触发。

## 第 7 节 · Parallel sessions and subagents

**我的理解对吗：一个 plan 可以按要改的文件拆成几个 worktree session；subagent 是预先定义好、负责不同类别任务的助手？** 基本对，补三点：

1. 并行 session 不只是一个 plan 拆出来的，也可以是不相关的改动。并行的单位是「有自己文件集的任务」。
2. subagent 在 session 自己的工作区里运行，隔离的是上下文，不是文件。要多个写入者并行，必须用 worktree；协调它们的是你，不是某个主 session。
3. subagent 按工作类型分（验证、简化、调研），不是按 plan 切片分；课程的 verifier 只汇报，不修改。

**我们做过吗？** 做过一次：UI-polish 的 2c-0 先把共享的 `common.py` 做完并冻结，2c 和 2d 在两个分支上并行，合并后再做一次整体走查。教训：worktree 只隔离文件，Chrome 扩展（11/10 两个 session 同时用把它弄崩了）、端口、本地数据库、模型额度这些共享资源隔离不了。

**浏览器冲突能用桌面 app 的内置浏览器解决吗？** 大体能。桌面 app Code 标签页的内置浏览器用的是和你个人 Chrome 分开的干净 profile；桌面 app 还会自动给并行 session 分 worktree，给每个 dev server 分空闲端口（前提是 server 读 `PORT`）。还要实测三项：多个 session 各自一个浏览器还是共用一个；不在前台时会不会降速；能不能上传文件。→ v3：localhost 的自查用内置浏览器，需要你登录的网站才用 Claude in Chrome，一次只给一个 session 用。

**subagent 名单，以及我的编码规范？**（你要求至少有一个 code reviewer；变量名长而有描述性；你不好读懂的地方要有详细注释）

- 规范是你自己跨项目的政策，写进用户级 `~/.claude/CLAUDE.md`；注释规则写成「解释原因和不显而易见的地方，和代码在同一个 commit 里更新」，避免注释过时。
- 「不好读懂」用两次规则慢慢积累：你每次要问某段代码在做什么，就把那类写法加进注释规则。
- 能量化的部分交给 linter 的复杂度规则（ruff `C901`、ESLint `complexity` / `max-depth`）。
- code-reviewer subagent 只汇报，在 session 报完成前对 diff 跑一遍；它不替代 G4 blind review。
- 待定名单：researcher、verifier、code-reviewer，simplifier 视情况。

## 第 8 节 · Give Claude a feedback loop

**feedback loop 和 verifier subagent 有什么区别？**（课程原文特意区分了） loop 贯穿整个任务，需要跑几次就跑几次；verifier 是 session 认为做完后，在新的上下文里跑一次的最终检查，这样结论不受写代码时那些假设的影响。

**verifier 和 reviewer 都是 subagent，在独立上下文里跑，对吧？** 对，上下文是独立的，看不到实现过程的对话。但独立只到一定程度：调用它时写的任务说明来自主 session，也就是实现者，可能写窄或漏掉；它看的也是同一个工作区。所以 G4 blind review 仍然单独开 session，任务说明来自 spec 和 validation，不经过实现者。→ v3：每个 subagent 的定义文件里写死它自己的检查清单，调用方只能加范围，不能减。

**和课程比，我们缺什么？**

- 「实现者不能改测试文件」只写在设计文档里，没有实现；现在靠 G3 和 G4 读 diff，属于课程说的较弱的替代做法。→ v3：红测试提交后用 hook 锁住测试文件。
- UI 的截图对比应该在实现 session 里完成，而我们的布局问题都是 G4 走查时才发现的。这需要一份 mock 和一个 session 自己能操作的浏览器。
- 检查没有合成一条命令，CLAUDE.md 没有写正常输出长什么样；报完成时不强制贴出绿测试的输出。

## 第 9 节 · Continuous evals in CI

**「活的套件；模型变强后，原来有区分度的用例会失去区分度」是什么意思？** 一个用例有区分度，是指好配置下它通过、坏配置下它失败。模型变强后，有的用例无论配置好坏都通过：比如新模型本来就不会把响应体写进日志，那 `status-no-pii-in-logs` 在 CLAUDE.md 有没有那一行时都通过，也就测不出那一行还有没有用。这时通过率 100% 只说明用例太容易，所以要从持续监控里不断补当前模型还会做错的新用例。我们 LoomCV 的 F-6 阈值「每有真实职位加进来就重新测」是同一个道理，不过那把尺子测的是产品里的模型，而这一节测的是 agent 的配置。

**怎么从线上事故建一个 eval？**

1. 事故：线上日志里出现客户的姓名和电话。
2. 复盘找到引入问题的 PR：`source` 记这个 PR，`from` 记它之前的最后一个 commit。
3. prompt 用当时的原始任务，不能写「别记录 PII」；写了答案就测不到配置了。
4. 按事故的实际后果写行为检查，写好 `may_change`。
5. 先用出事时的配置跑，必须失败。
6. 修配置（CLAUDE.md 加一行、或加 skill / hook），再跑必须通过；eval 和配置修改一起提交。
7. 一直留在套件里。

一次事故分两层处理：代码的 bug 加普通的回归测试；agent 为什么会写出这样的代码加 eval；跟 agent 无关的事故只需要第一层。课程没讲、我补充的一点：agent 每次运行结果不完全一样，第 5–6 步可能要多跑几次才可信。

**套件越来越大，要不要减负？** 课程只说了 20–50 个用例，以及可以按周期离线跑，没讲淘汰。我的建议：核心子集每次配置 PR 都跑，全量定期跑；去掉用例保护的那条配置后仍然通过的，移到归档目录；事故转成的用例，只有确定性检查完全覆盖同样行为时才停。

**eval 是人和 Claude 一起写的吗？** 课程只说初始用例由 platform engineer 收集、事故用例由负责事故的团队写。分工可以是：Claude 起草，人决定选哪些任务、什么算可以接受、亲自确认旧配置下会失败。检查要人来审，因为写得太松就会一直通过；eval 文件不能让运行中的 agent 看到。

→ v3 标记：LoomCV 现有的 eval 哪些适用、哪些不适用、还要补什么，留给梳理 session 展开。

## 第 10 节 · AI in the PR review loop

**这和我年初在 TELUS 做的 PR review Copilot instructions、后来延伸到 Claude Code 的 review skill 思路一致。区别是当时专门针对 JS/TS/React 和 TELUS 的编码规范，而且手动启动、修改建议手动接受。v2 缺这一块，v3 要加上吗？** 要加。v2 不是完全没有评审：G4 part 1 的 blind review 对照 ticket、validation、plan 读代码，接近课程的 compliance pass。v2 缺的是：

1. 书面的评审规则 `REVIEW.md`（固定几遍、严重程度怎么定），G4 每次查什么取决于当次的说明。
2. 每次改动都自动跑；我们只在关卡上评一次，而且 LoomCV 不走 PR。
3. 修复循环：评论里 @claude，Claude 改完推上去；我们的修复轮是手动开新 session。
4. 评审发现回写 CLAUDE.md（两次规则），以及定期调整评审设置。

和 TELUS 那套比：当时的 skill 相当于课程的 bugs pass 加一份编码规范，课程多出的关键是读 `spec.md` 和 `plan.md` 的 compliance pass。课程示例里第一条 Important（面板每次渲染都发请求，plan.md 要求缓存），只看 diff 的评审人发现不了。另外，触发和修复变成自动的，但批准始终是人：findings 本身不批准也不阻止。

→ v3 待定：会话内的 code-reviewer、PR review、G4 三层评审怎么避免重复（提议：PR review 接替 G4 part 1，G4 只留批准和走查）；个人项目里 GitHub 不允许作者批准自己的 PR，所以「你的 merge 就是批准」；自动运行需要订阅不够时，退回到手动跑 `/review`，但每次读同一份 `REVIEW.md`。

## 第 11 节 · Hooks as approval gates

**第一段在说什么？** hook 拦住 Claude 的动作后有三种处理，区别在于谁来批准：

1. **脚本自己放行或拦截，没有人参与**：Build 阶段的护栏，比如我们的 `no_script_writes.py`。
2. **ask：暂停，等正在用 session 的人确认**：适合操作者本人有权批准的情况。无人值守时没人回答，按拒绝处理，所以从 main 分支的流水线发布另外放行（main 上的 merge 已经批准过了）。
3. **批准人是别人：查批准记录，没有就一直拦着**：比如上生产要发布经理批准，弹 ask 给工程师就问错了人。hook 去查变更系统里有没有对应这个版本、已批准的变更单；没有就拦下，并告诉 Claude 怎么拿到批准。前提是 agent 不能写入它要检查的记录。

→ v3 标记：我们的 G1、G2 属于第三种（批准人是你，不是写代码的 session），现在靠 session 自觉停下，可以改成 hook 去检查你对 plan.md 的 merge 或 commit。career 仓库的「最终提交必须由你确认」也是这一类，现在只写在文字里。

**那两段 `hookSpecificOutput` JSON 都加在哪里？`settings.json`？** 不写在任何配置文件里，它们是 hook 脚本运行时打印到 stdout 的输出。三层：

1. `.claude/settings.json` 登记 hook：什么事件、匹配哪些工具、运行哪个脚本。
2. 脚本 `release-gate.sh` 做判断：Claude Code 每次匹配到调用就运行它，把这次调用的信息从 stdin 传进去。
3. 脚本打印的 JSON 就是这一次的决定：ask 的理由显示给人，deny 的理由交给 Claude。

课程里那两段是同一个脚本在两次不同调用下的输出。第 6 节的 `exit 2` 加 stderr 写法只能拦截；要 ask 或带理由放行，就要用 JSON 输出。

**managed settings 这一整段和我现在的流程有什么关系？** 大部分没有。那是公司 IT 通过 MDM 或管理后台统一下发、个人改不了的配置，个人项目没有这一层。有关的三点：

1. **现在就用得上**：项目级的 `permissions.allow` 放行安全的常用命令（并行 session 就不会卡在确认上），`permissions.deny` 禁止读密钥文件。
2. **平台已经做了**：云端工作区的网络白名单。
3. **以后在公司要注意**：公司开了 `allowManagedHooksOnly` 时，项目和个人的 hook 全部失效，v3 的测试文件锁、G2 关卡会被静默关掉；要通过公司批准的插件 marketplace 或 managed 配置下发。

## 第 12 节 · CI/CD integration and deployment

**「把部署通过 MCP 开放给 agent」在我的个人项目上能做到吗？比如飞猫网站、以后可能做的 Roblox 游戏、接的 contract 项目。** 这一步解决的问题是：agent 自己不拿部署凭据，只能调用几个固定的工具，而且每个环境分开授权。按这个目标：

- **飞猫网站**：能做，但现有方案已经达到效果。9/5 定的 Astro 静态站在 push 到 main 后由 GitHub Actions 通过 SFTP 部署到 GoDaddy，凭据在 GitHub secrets 里，agent 只能开 PR，你的 merge 就是批准。现在值得补的是一条演练过的回滚命令。等你想让 agent 在 session 里自己发布、检查、回滚时，再写一个小的部署 MCP server。GoDaddy 共享主机能不能开 staging 子域名还没核实。
- **Roblox**：技术上可能（Open Cloud 发布 place 版本、Creator Dashboard 回退版本，我没核实），但和你 9/13 定的「playground 只用于交互式学习、不做自动化」冲突，等真做游戏时再说。
- **Contract**：由客户决定。部署基础设施和凭据属于客户，你的交付物是 PR。能带过去的是 CI 里的只读判断步骤和只通过 PR 写入；先问清客户是否允许代码交给 Anthropic 的模型处理、API 费用谁付。

**所以 What it looks like 的例子只是参考，现在不必完全理解和照搬？** 对。它是按「公司有多套环境、有发布经理、有变更系统」写的。记住四条原则：

1. 放行规则只能指定工具，管不到参数，所以每个环境要单独一个工具或 server。
2. 无人值守运行用 `dontAsk`，会弹确认的调用直接拒绝，job 不会卡住。
3. 生产环境默认拒绝：只在 hook 明确放行时发布，hook 出错也是拒绝。
4. 回滚是事先批准的，一直在放行列表里，出事时不用等批准。

## 第 13 节 · Closing the loop on metrics

**What a control band is 的定义没看懂。** control band 就是一个指标平时正常波动的范围，超出这个范围才算真的出问题。用课程的数字：

1. **正常水平**：最近 30 天每小时读数的平均值，0.2%。
2. **平时波动有多大**：标准差 σ，读数通常离平均值多远，0.02%。
3. **从平均值往上划线**：1σ 线 0.22%、2σ 线 0.24%、3σ 线 0.26%。14:00 的读数 1.9% 远高于 3σ 线。

为什么分三级：系统完全正常时读数也会随机越线。每月 720 个读数里，纯随机会有每天约 4 次超过 1σ（只记日志）、每月约 16 次超过 2σ（Claude 只读诊断）、每月约 1 次超过 3σ（所以即使 3σ，Claude 也只能开 PR 或执行事先批准的 runbook）。

漂移规则抓慢慢变坏、从未到 3σ 的情况：最近 5 个读数有 4 个高于 1σ，或连续 8 个高于平均值，都算 2σ。整个检测是确定性的，没有模型参与，到 2σ 以上才启动 Claude。

→ v3：个人项目里指标的读数太少，很少用得上 control band；Stage 6 主要由消息或工单触发（Kitty 发来的链接、客户报的 bug）。现有的 `fc-next` 每小时循环已经是这种形状，要补上：和模型分开的确定性检测、按级别限定能做什么、已知步骤以外的情况写成 `intent.md` 放进队列。
