<!-- 单向快照：由 Claude Doc「AI-native SDLC Playbook 复习材料」导出为 Markdown，导出时间 2026-11-15（America/Toronto），文档版本 rev 34。
原件：https://claude.ai/artifact/Smie2S3SnsLDHB384HW2sC （可编辑的正本在那里；这里只在原件有实质改动后重新导出）。
导出时的损失：文中的 play 依赖图（嵌入的图）被替换成文字占位；日期和提及的标签变成纯文字。 -->

# AI-native SDLC Playbook 复习材料

Nov 13, 2026 · @Leon

## 使用说明

本文档是 Claude Academy 课程 [The AI-native SDLC playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook/introduction) 的中文复习材料。课程共 14 节，已于 2026-11-14 全部学完。

**每节固定栏目**（第 1 节是总览，格式不同）：

1. **一句话**：这一节到底讲什么。
2. **变化**：传统做法 vs AI-native 做法。
3. **前提与基础设施**：开始这一节的做法之前需要具备什么。
4. **怎么做**：课程给出的执行步骤。
5. **示例**：课程里的示例文件原文（英文，代码块）。
6. **治理**：这一步怎么留痕、谁拍板、怎么防出错。
7. **度量**：领先指标与滞后指标。
8. **术语**：本节出现的关键词。

**课程已学完**：第 2–13 节用上面的八栏格式，第 14 节是结语和资源清单，文末「总览表」每节一行。

**用词约定**：play = 课程里的一个「做法」单元；stage = 阶段；skill / hook / subagent / worktree 等工具名保留英文。

## 第 1 节 · What changes and where to start（总览）

**一句话**：AI 写代码的速度已经远超以前，但围绕代码的流程没跟上；这门课把软件从想法到生产的六个阶段，逐一改成 AI-native 的做法，每个做法叫一个 play。

### 六个阶段的变化

大多数组织处在两列之间的某个位置。无论哪一列，**凡是需要判断的决定，责任仍然在人**。

| 阶段 | 传统 SDLC | AI-native SDLC |
| --- | --- | --- |
| Plan | 委员会收集需求，经过工作坊和签字提炼，手工写成文档 | Claude 直接从来源归纳痛点，写进 intent.md：人能读、机器能执行 |
| Design | 分析师写 spec，设计师再解读 | 需求和设计压缩成与 agent 的一次工作会话，由写成 skill 的标准指导，存在 Git 里 |
| Build | 测试和代码手写，文档开发完才补 | 测试和代码由 AI 生成；组织知识用有版本的 CLAUDE.md 和 skill 维护 |
| Test | 阶段边界上设 QA 关卡 | 持续的 eval 穿插在实现过程中 |
| Deploy | 人工审每一行，治理靠评审周期，常常不一致 | 多层 agent 评审，人工评审留给受监管和关键代码；治理在 AI 行动时就生效，由 hook 当审批关卡 |
| Maintain | 人盯着生产环境找 bug | agent 监控线上部署；任何 control band 被突破，都诊断后写回循环，变成一份新的 intent.md |

### 两个贯穿全课的术语

- **intent.md**：一份简短、有版本控制的文件，写明要什么、为什么、在哪些约束下。
- **control band**：生产指标正常水平周围的一个范围，超出就是异常。

### Play 是怎么组织的

全课核心是 12 个 play，分属六个阶段，阶段之间不是线性顺序。每个 play 都讲五件事：变化、怎么开始、具体步骤、治理、怎么衡量。每个 play 在 Prerequisites 里写明它依赖哪些 play，全部依赖关系画在下面的依赖图里。

&#91;embedded content: play 依赖图 · 12 个 play，第一行 6 个没有前提\]

实线箭头指向建立在它之上的 play，虚线表示有帮助但不是必需；intent 一路影响到最后的 Closing the loop，PR review → CI/CD → Closing the loop 是主干。

### 从哪里开始

play 是模块化的，可以按自己的需要先改某个阶段。没有前提、哪里都能开始的六个 play：

- Plan：Capture as intent.md
- Build：plan mode 作为默认起点
- Build：The CLAUDE.md
- Build：Skills as institutional knowledge
- Test：Give Claude a feedback loop
- Deploy：Hooks as approval gates

拿不准就从 **The CLAUDE.md** 开始：只需要一个仓库、Claude Code 和一位熟悉代码库的工程师，而且 subagent 和 eval 两个 play 都建立在它之上。

## 第 2 节 · Capture as intent.md（Plan）

**一句话**：提出想法的人和 Claude 头脑风暴，把结果写成一份 intent.md（一份「原型 spec」），提交到共享的 intent 存放处，由 product owner 接手。

intent 有三种来源：有人有想法、有人开了 ticket、生产告警暴露出事故（见 Maintain 阶段）。不管来源，都是同样的步骤：agent 写出 intent.md，**product owner 审阅并修正后才提交**。

### 变化

- **传统**：一个想法要经过 backlog 条目、user story、故事点、精炼会才有人动手；每次交接都换一次负责人，到工程那里已经离发起人的原意隔了好几层。
- **AI-native**：发起人和 Claude 头脑风暴，用自己的话写成 intent.md：要什么、为什么、在哪些约束下。反复出现的流程写成 skill。

### 前提与基础设施

- **前提**：无。
- **基础设施**：非工程师也能用 Claude（claude.ai 或 Cowork）；一份大家认可的 intent.md 模板；一个有版本控制、product owner 关注的共享 intent 存放处。
- **存放处放哪**：单个产品最简单就是产品仓库里的 `intent/` 文件夹，让整条产出链紧挨着由它衍生的代码。只有当一份 intent 横跨很多仓库时，单独开一个 intent 仓库才值得；monorepo 里它就是一个目录。
- 搭建是平台或工程团队的一次性工作：由技术人员建好存放处、决定谁能写。不会 Git 的人不用直接碰 Git：通过 GitHub 等版本控制的 connector，Claude 可以从 claude.ai 或 Cowork 代为提交。

### 怎么做

1. 发起人用自己的话向 Claude 描述问题：现在做不到什么、影响谁、改好之后是什么样、什么不在范围内。不需要正式用语。
2. 头脑风暴到想法具体为止。Claude 问分析师会问的问题：范围、用户、约束、怎样算成功。
3. 让 Claude 按组织的模板写成 intent.md。模板可以做成 skill（由技术人员搭、lead 签字），内容包括：问题、期望结果、受影响的用户和系统、约束、待定问题。
4. 发起人修正 Claude 理解错的地方。
5. 把 intent.md 提交到共享存放处，作者和时间进入记录，product owner 从这里接手。

### 示例：intent.md

```markdown
# Intent: claims status self-service
Author: J. Ortiz (claims operations). Status: draft.
## Problem
Customers phone the contact center to ask where their claim is.
Handlers spend roughly a third of call time on status-only queries.
## Proposed outcome
Customers see claim status, next step and expected date in the portal.
## Affected users and systems
Claims handlers, portal team, claims-core API.
## Constraints
No new PII in the portal session. Existing authentication only.
## Open questions
Do third-party loss adjusters need access too?
```

读法：Problem 带一个数字（三分之一通话时间）；Proposed outcome 只写结果不写方案；Constraints 是业务层面的限制；待定问题会带到下一阶段。

### 治理

- 证据就是提交进 Git 的 intent.md：作者、时间、完整修订记录都在存放处的 Git 历史里。
- **product owner 审批**：接受（进入 Design 阶段）记录为 merge，拒绝记录为关闭评审。审批不靠文件里的 `Status` 字段，靠 merge 这个动作。

### 度量

- **领先**：从第一次对话到 intent.md 提交用了多久（读 Git 历史）。预期从几周的需求挖掘和精炼缩短到几小时。
- **滞后**：存活率，即被 product owner 接受进 Design（而不是关闭）的 intent 占比；另外数一数同一变更在第一次提交 spec.md 之后，intent.md 又被改了几次。

### 术语

- **originator**：发起人，提出想法的人。
- **proto-spec**：原型 spec，即 intent.md。
- **intent home**：intent 的共享存放处。
- **survival rate**：存活率。

## 第 3 节 · Requirements and design（Design）

**一句话**：intent 被接受后，Claude 在组织的 skill（品牌、安全、合规、UX）约束下，一次写出需求加设计的 spec.md，并标出有问题的地方；product owner 只审不写。

前端工作是最典型的例子：intent 被接受后，product owner 在 Claude Design 里从 intent.md 做出 mock、反复迭代，再导出到 Claude Code 去实现。

### 变化

- **传统**：需求和设计是两个阶段、两个团队；分析师把想法写成需求，设计师再解读成设计。分开是为了分清责任，但又慢又会丢信息。
- **AI-native**：两个阶段合并成一次带 prompt 的会话。

### 前提与基础设施

- **前提**：一份 intent.md；品牌、安全、合规、UX 政策已写成 skill。
- **基础设施**：一位能用 Claude 的 product owner，不需要工程能力。

### 怎么做

1. product owner 开一个载入了组织 skill 的会话，附上 intent.md。
2. prompt 做三件事：指向 intent、列出约束、要求列出 concerns。**成熟度三级**：先手工跑 → 固化成组织级 slash command → 把 intent 的 merge 当触发器，由非交互的任务载入 skill 跑这一步，把 spec.md 以 PR 提交（管线细节在 Deploy 阶段的 CI/CD play）。到这一级，product owner 第一次接触 spec 就是审阅。
3. product owner 对照原想法审 spec：解决了提出的问题吗？intent 里的待定问题是已回答，还是带到后面？
4. **先处理 flagged concerns**：这些就是分析师以前会上报的点。product owner 在工程看到 spec 之前，和每条 concern 的 policy owner 一起定下来。
5. 把 spec.md 和 intent.md 放在一起提交：这一对文件记录了「要的是什么」和「定了什么」。
6. product owner 决定是否进入 build，组织定为高风险的要咨询技术负责人。这个决定始终由人来做；接受 spec 就启动 Build 阶段的 plan mode play。

### 示例：prompt

```markdown
Read the attached intent.md and produce a requirements and design spec for integrating it into our existing codebase. Apply the skills available to you so the plan conforms to our brand guidelines, security policies and UX standards. Document the spec fully as spec.md, ready to hand to the engineering team. Describe clearly any areas of concern, especially where you cannot satisfy contradicting policies.
```

### 示例：spec.md

背景：一家保险公司想让客户在门户里看到理赔进度。claims-api 是门户的后端，claims-core 是存放理赔的老系统。

```markdown
# Spec: claims status self-service
From: intent.md (J. Ortiz, claims operations). Status: ready for product owner review.
Skills applied: secure-api-review, brand-voice, portal-ux.

## Requirements
- R1. A signed-in customer sees status, next step and expected date for each open claim.
- R2. Status is one of four states: received, in review, approved, paid.
- R3. The response carries those three fields and nothing else.
- R4. What the customer sees is at most 60 seconds old.

## Design
- New endpoint GET /claims/{id}/status in claims-api, behind the gateway JWT.
- claims-api reads the claim from claims-core. The portal never calls claims-core.
- New StatusPanel on the portal claims page. It caches each answer for 60 seconds.

## How each constraint in the intent is met
| Constraint | Met by |
| :---- | :---- |
| No new PII in the portal session | R3. None of the three fields is tagged pii in the schema. |
| Existing authentication only | The gateway JWT. No new login, token or role. |

## Open questions from the intent
- Do third-party loss adjusters need access too? Not answered. Carried forward as concern 1.

## Areas of concern
1. Loss adjusters have no portal account. Giving them access breaks "existing
   authentication only", so they are left out of this spec. Owner: security.
2. The portal-ux skill says every status shows a date. The brand-voice skill says
   never to state a payment date as a commitment. I cannot satisfy both as written.
   Proposed label: "Estimated date". Owner: compliance.
3. claims-core allows 50 requests a second. The 60-second cache should keep the
   portal under that, but nobody has load tested it. Owner: claims-core team.
```

读法：

- 需求带编号（R1–R4），是为了让后面的 plan 和评审可以引用。每条是一句可以验证的话，比如 R4 的「60 秒」可以量。
- intent 的每条约束在对照表里都有一行；intent 的待定问题变成了 concern 1。
- 三条 concern 是三种类型：约束导致的范围排除、**两个 skill 互相矛盾**（正是 prompt 要求标出的那类）、没验证过的假设。每条都写了负责人，有建议就写建议。
- 没有验收一节。

### 治理

- 政策冲突不再几周后在评审里才发现，而是写 spec 时就读入并应用当前的政策。
- skill 是 spec 的约束。spec、产出它的 prompt、当时生效的 skill 版本，都记在版本控制里。
- product owner 签字确认 spec，把 concerns 交给对应的 policy owner。

### 度量

- **领先**：同一变更从 intent.md 提交到 spec.md 提交的时间差（两个 Git 时间戳），和以前「需求+设计」的周期对比。
- **滞后**：开始 build 之后的需求返工，即第一次提交 plan.md 之后又有几次 spec.md 提交。git log 就能直接算。

### 术语

- **spec.md**：需求加设计的规格文件，和 intent.md 放在一起。
- **flagged concern / area of concern**：标出的问题点，政策满足不了、互相矛盾，或分析师以前会上报的点。
- **policy owner**：某条政策的负责人，由他来定对应的 concern。
- **Claude Design**：做前端 mock 的工具，可以导出到 Claude Code。

## 第 4 节 · Plan mode as the default starting point（Build）

**一句话**：工程师在 plan mode 下开始每个 Claude Code 会话，把审过的 spec.md 交给 Claude，让它写出实施计划、反复追问和修改，审定后提交为 plan.md，再开始写代码。

### 变化

- **传统**：工程师读完设计就开始写代码。改哪些文件、加哪些测试，只在他脑子里，最多写在 ticket 评论里，别人审不了。评审者第一眼看到的就是完成的 diff，这时返工已经很慢。
- **AI-native**：工作从一份书面计划开始。Claude 在 plan mode 里只读代码、不改文件；工程师在写代码前修正计划，审定版本提交为 plan.md，供后续阶段对照。

### 前提与基础设施

- **前提**：有 intent.md 或 spec.md 就用上；有 CLAUDE.md 会更好。
- **基础设施**：能访问仓库的 Claude Code。

### 怎么做

1. 工程师以 plan mode 开启会话。
2. 给 Claude intent.md 和 spec.md，要一份实施计划：写明要改的文件、工作顺序、用来证明的测试。
3. **追问**：这个改动可能弄坏什么？哪一步风险最大？有哪些备选方案 Claude 没选？
4. 反复修改，**直到一个没看过这段对话的工程师，只凭这份计划就能实现这个改动**。
5. 把审定的计划提交为 plan.md。它进入审计记录，Deploy 阶段的 PR review play 会拿最终 diff 和它对照。
6. 接受计划，让 Claude 实现。计划扎实的话，往往一次就做完。
7. 实现偏离计划时，在同一个 commit 里更新 plan.md。可以考虑用 hook 强制两者同步。

### 示例：plan.md

```markdown
# Plan: claims status self-service (from intent.md and spec.md)

## Files that change

portal/src/claims/StatusPanel.tsx (new), claims-api/routes/status.py, claims-api/tests/test_status.py

## Order of work

1. Add the status endpoint behind existing auth (R1, R2, R3).
2. Panel against the endpoint, with the 60-second cache (R1, R4).
3. Wire into the portal nav.

## Risks

The claims-core API rate-limits at 50 rps; the panel must cache (spec concern 3).

## Proof

test_status.py covers the four claim states (R2) and fails on any extra field (R3); screenshot matches the approved mock.
```

读法：R1–R4 是 spec.md 里的编号需求，concern 3 是 spec 标出的风险。plan 引用了它们，评审者就能逐行对照 spec 检查 plan。Proof 里除了测试，还有「截图与批准的 mock 一致」。

### 治理

- 设计评审发生在生成任何代码之前，这时改方向只是改一份文档。
- **plan mode 自己就是关卡**：工程师接受计划之前，Claude 不能改文件。计划、修订记录和接受人都会留档。
- 常规改动由工程师批准；组织定为高风险的，交给技术负责人或架构师。

### 度量

- **领先**：第一次实现就能合并的改动占比；从计划批准到 PR 合并的时间（数据来自 PR 元数据）。
- **滞后**：每个改动的返工次数；合并后的 diff 仍然和 plan.md 一致的频率。

### 补充：auto mode

Claude Code 也可以跑 auto mode：工程师迭代并批准计划后，Claude 逐个改动直接执行，不再每次编辑都询问。

- **什么时候成为默认**：后面几个 play 的护栏成熟之后，即调好的 CLAUDE.md、写进政策的 skill、拦截危险操作的 hook、Claude 能跑的测试套件。适用于常规工作：spec 严谨、影响面小、代码已有测试覆盖。
- **审阅重点的转移**：从「盯着 agent 做每次编辑」转向「较长的自主会话结束后审产出」。
- auto mode 加上 worktree，让个人和团队都能并行，也是 Maintain 阶段「自主运行 SDLC、闭环」的基础。

### 补充：老系统与权威来源

很多组织已经在别处记录这些产出物：工作项在 Jira、需求在带监管追溯的工具里、设计在 Figma、变更审批在变更委员会。审计和监管已经认可它们，很难替换，所以 AI-native 流程要配合现有系统。**每种产出物都要指定一个权威来源**，其他系统只存副本或链接。三种配置，可以按产出物分别选：

| 配置 | 做法 | 适合 |
| --- | --- | --- |
| 仓库为准 | Markdown 产出物是权威记录，老系统引用 commit 里的文件 | 工程主导的组织；所有记录在一个工具、一个时间来源 |
| 老系统为准 | Jira / ServiceNow / 需求工具是权威记录，Markdown 是工作副本；Claude 在会话开头读记录，在同一会话里通过 MCP connector 写回结果 | 已有受认可系统的组织 |
| 互相链接（最低要求） | 产出物写上记录 ID，老系统记录写上 Markdown 文件的 commit SHA | 过渡期的起点，但会有两个权威来源 |

### 术语

- **plan mode**：Claude Code 的只读规划模式，接受计划前不能改文件。
- **plan.md**：审定的实施计划，写明文件、顺序、风险、证明。
- **auto mode**：批准计划后不再逐次询问的执行模式。
- **blast radius**：改动的影响面。
- **source of truth**：权威来源。

## 第 5 节 · The CLAUDE.md（Build）

**一句话**：CLAUDE.md 把新人第一天需要的背景（约定、命令、架构、团队最常见的错误）写成一个文件，agent 每个会话开头都会读；全队维护，每次出错就迭代。

以前存在人脑子和 wiki 里的知识，变成 agent 每次都会读的一个文件。

### 前提与基础设施

- **前提**：无。
- **基础设施**：一个仓库、装好的 Claude Code、一位熟悉代码库的工程师。

### 怎么做

1. 在仓库里运行 `/init`，Claude 根据代码生成初稿。
2. **删到只剩新人第一天需要的**：构建、测试、lint 命令，要紧的约定，Claude 反复犯的错。
3. 提交到仓库根目录，全队共用一份，修改像代码一样走评审。
4. **两次规则**：Claude 同一个错犯了两次，就把纠正写进 CLAUDE.md。
5. **控制在一页以内**：Claude 每个会话开头都会读完整个文件，过时的内容只会白白占用上下文。

### 示例：CLAUDE.md

背景：保险公司客户门户的仓库，claims-core 是存放理赔的老系统，`intent/` 存放每个变更的规划文件。

```markdown
# Claims portal
## Commands
- Build: make build
- Test: make test (unit), make itest (integration, needs docker)
- Lint: make lint (runs in CI; fix before pushing)
- Run: make run (portal on :3000, claims-api on :8000)
## Conventions
- claims-api is Python 3.12 and FastAPI. portal is TypeScript and React.
- Every endpoint needs a test in claims-api/tests.
- Dates cross the API as ISO 8601, never as formatted text.
## Architecture
- portal/ is the customer site, claims-api/ is its backend, and
  intent/ holds the intent.md, spec.md and plan.md for each change.
- Only claims-api talks to claims-core. The portal never calls it.
- claims-core allows 50 requests a second. Cache reads; never poll it.
## Things Claude gets wrong
- Do not log request or response bodies in claims-api; they can hold PII.
- Do not bump dependency versions; the platform team owns them.
```

读法：四节各只有几行，整份不到 20 行。Architecture 里顺便写明了每个变更的 intent / spec / plan 放在哪。「常犯的错」都是一句禁止加一个理由。

### 治理

- CLAUDE.md 有版本控制，agent 遵循的指令可以评审、可以审计。
- 团队约定通过这个文件生效，每次修改都在 Git 历史里，由 code owner 在 PR 评审里批准。

### 度量

- **领先**：Claude 重复犯了多少次 CLAUDE.md 本该拦住的错；对 CLAUDE.md 的纠正和修改在 Git 历史里跟踪。
- **滞后**：新成员到第一个 PR 合并用了多久（读 PR 历史）。

### 术语

- **/init**：让 Claude 生成 CLAUDE.md 初稿的命令。
- **two-strike rule**：两次规则，同一个错犯两次才写进文件。
- **code owner**：负责批准某部分代码修改的人。

## 第 6 节 · Skills as institutional knowledge（Build）

**一句话**：skill 是组织把制度知识变成可执行指令的方式：明确、有版本、广泛适用、政策变了统一更新。但 skill 只是建议性的，必须成立的规则还要由 hook 和 PR 检查兜底。

**经验法则**：需要被一致执行的制度知识，写成 skill；属于 CLAUDE.md 或 prompt 的内容，不要写成 skill。

### 前提与基础设施

- **前提**：无。有 CLAUDE.md 会更好（它把 agent 的工作知识放在仓库里），但 skill 不依赖它。
- **基础设施**：**一条有明确负责人、有成文权威版本的政策**。

### 怎么做

1. 挑一条现在执行得不一致的知识：安全标准、API 设计约定、品牌规则等。
2. 写成 skill：一个文件夹，里面一个 SKILL.md。frontmatter 写什么时候触发，正文写要做什么。由工程师根据 policy owner 的权威版本、借助 Claude 来写。
3. 放在仓库的 `.claude/skills/<name>/` 下跟代码一起发布，或者通过 plugin 在全组织分发。
4. **测试它会不会触发**：用不同说法让 Claude 做相关任务，确认每次都会加载。
5. 政策变了就改 skill，由 policy owner 签字确认。
6. 工程师下一个会话自动用上新版。

### 示例：SKILL.md

`.claude/skills/secure-api-review/SKILL.md`：

```markdown
---
name: secure-api-review
description: Apply the API security standard. Use whenever creating or
modifying an external-facing endpoint, reviewing API code, or
generating an OpenAPI spec.
---
# Secure API review
When you create or change an API endpoint:
1. Authentication: every endpoint requires the gateway JWT;
   no anonymous routes outside /health.
2. Input validation: validate request bodies against the OpenAPI
   schema and reject unknown fields.
3. Audit: every state-changing endpoint emits an audit event with
   actor, action, entity and timestamp.
4. Data classification: fields tagged pii in the schema must never
   appear in logs or error messages.
Run scripts/check-endpoints.sh and include its output in your summary.
```

读法：`description` 决定什么时候触发，所以写成「做哪些事时使用」；正文是编号规则；最后一句让 Claude 自己跑检查脚本并把结果写进总结。

### 治理：skill 是建议性控制

- skill 让 Claude 在写代码时大概率遵守政策，但**没有任何东西强制会话遵守**。
- 必须始终成立的政策，后面要有确定性的一层：拦下操作的 hook，或者在 PR 上再查一遍的评审。
- **skill 让违规变少，hook 让违规几乎不可能发生**。hook 在编辑时抓住违规，PR 上的同一个检查抓住从别的途径进分支的东西。
- skill 的调用会记在会话记录里；policy owner 像审代码一样审 skill 的修改。

### 度量

- **领先**：从 policy owner 批准政策变更，到更新后的 skill 合并，用了多久（读 skill 文件夹的 PR）。
- **滞后**：引用该政策的 PR 评审问题数，应该逐渐降到零。降不下来，要么 skill 没触发，要么 skill 的文字已经和官方政策对不上。

### 补充：hook 作为 build 阶段的护栏

Claude 在实现阶段的动作大多是改文件和跑 shell 命令，所以 build 阶段是 hook 触发最多的地方。build 阶段的 hook 可以：

- 拦住对受保护路径的修改（生成的类、冻结的包）；
- 每次改完文件就跑格式化和 lint，让偏差不会累积；
- 防止凭据进入 diff；
- 给必须无例外成立的 skill 兜底。

hook 对每个匹配的动作都会跑，所以要**快、只看改动的那个文件**；全套测试这类重检查放到 commit 或 PR 阶段。

**示例：给 skill 第 4 条兜底的 hook。** 端点文件在 `claims-api/routes/`，每次改了其中一个，hook 就跑 skill 里提到的同一个脚本。

注册在 `.claude/settings.json`（空的 `args` 让 Claude Code 直接运行脚本，不经过 shell）：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/api-policy.sh",
            "args": [] }
        ]
      }
    ]
  }
}
```

hook 脚本 `.claude/hooks/api-policy.sh`：

```bash
#!/bin/bash
# Backs rule 4 of the secure-api-review skill with the same script the skill runs.
file=$(jq -r '.tool_input.file_path')
case "$file" in
  "$CLAUDE_PROJECT_DIR"/claims-api/routes/*.py) ;;
  *) exit 0 ;; # not an endpoint
esac
cd "$CLAUDE_PROJECT_DIR" || exit 2
if ! found=$(scripts/check-endpoints.sh "${file#"$CLAUDE_PROJECT_DIR"/}"); then
  echo "secure-api-review rule 4: a pii field reaches a log or an error message." >&2
  echo "$found" >&2
  exit 2
fi
```

编辑后才跑的 hook 撤销不了修改，所以**退出码 2 把脚本的报错信息交给 Claude**，由它去修那一行。比如改代码时把客户姓名写进了日志，Claude 会看到：

```text
secure-api-review rule 4: a pii field reaches a log or an error message.
claims-api/routes/status.py:10: policy_holder_name
```

**Edit|Write 类的 hook 管不到用 shell 命令改文件的情况**，所以同一个脚本还要作为每个 PR 的必过检查：

```yaml
name: API policy
on: pull_request
jobs:
  check-endpoints: # a required check in branch protection
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: scripts/check-endpoints.sh claims-api/routes/*.py
```

**同一个脚本用在三处**：skill 让 Claude 自己跑、hook 在编辑后自动跑、CI 在 PR 上跑。

**需要人来批准的 hook 不放在 build 阶段**，属于 Deploy 阶段的关卡：build 时弹出审批，会把人重新放回所有并行会话的关键路径上。

### 术语

- **SKILL.md / frontmatter**：skill 的主文件；frontmatter 里的 `description` 决定触发时机。
- **advisory control**：建议性控制（skill）；**deterministic layer**：确定性的一层（hook、CI）。
- **PostToolUse**：工具调用之后触发的 hook 事件。
- **exit code 2**：hook 的退出码，把报错信息交还给 Claude。
- **required check**：分支保护里的必过检查。

## 第 7 节 · Parallel sessions and subagents（Build）

**一句话**：一个工程师可以同时驱动几条工作流：并行 session 增加同时在做的任务数，subagent 让每个 session 专注于自己的任务；工程师的工作变成操控和审阅。

### 两种不同的工具

|  | 并行 session | subagent |
| --- | --- | --- |
| 是什么 | 另一个完整的 Claude Code 实例，在自己的 Git worktree 里做另一个任务 | 单个 session 内部的助手，有自己的上下文窗口和工具权限 |
| 作用 | 增加同时在做的任务数 | 让 session 保持专注，不被琐事填满上下文 |
| 彼此关系 | 各 session 互不知道对方，唯一的共同点是操控它们的工程师 | 由发起它的 session 调用并收回结果 |
| 适合 | 改不同文件的独立任务 | 多个任务里反复出现的工作，比如验证应用是否正常 |

### 变化

- **传统**：一个工程师一次做一个任务，大量时间花在等构建、测试、评审上。等待时也能切到别的任务，但切换上下文太累，很少有人这么做。
- **AI-native**：一个工程师同时跑几个 Claude session，各自在自己的 worktree 里做自己的任务；重复的工作变成 subagent。工程师的工作转向编排，最终转向搭建和监控自动循环。

### 前提与基础设施

- **前提**：CLAUDE.md（所有 session 都会读）。Test 阶段的 feedback loop 也有帮助：session 能自己验证工作，工程师就不用时时盯着。
- **基础设施**：一个 Git 仓库（隔离靠 worktree）；调好权限设置，让组织认为安全的命令不用等批准。

### 怎么做

1. 用 plan mode 产出的 plan 判断哪些工作彼此独立，把工作拆成**改不同文件的任务**。**会改同一批文件的任务，放在一个 session 里依次做**。
2. 每个并行任务一个 worktree，比如一个终端里 `claude --worktree feature-auth`，另一个里 `claude --worktree fix-rate-limit`。worktree 是在自己分支上的独立检出，让各 session 不会在文件上撞车。
3. **从 2–3 个 session 开始**。实际上限是一个人能好好审完多少条工作流，只有审得过来时才加 session。
4. 把重复的工作变成 subagent，定义在 `.claude/agents/` 下的 Markdown 文件里：名字、什么时候用、允许碰哪些工具。例子：
   - **code simplifier**：主 agent 做完后去掉不必要的复杂度；
   - **verifier**：跑起应用、检查行为；
   - **researcher**：去探索代码库再回来汇报，不让探索过程填满主上下文。

   定义文件提交进 Git，全队共用。

### 示例：subagent 定义

`.claude/agents/verifier.md`：

```markdown
---
name: verifier
description: Runs the app and checks the change works before the session reports done
tools: Bash, Read
---
Start the app with make run. Exercise the changed behavior and the two
nearest neighboring flows. Report what you ran, what you saw, and any
behavior that does not match plan.md. Do not fix anything; report only.
```

读法：只给了 Bash 和 Read 两个工具；除了改动本身，还要测与之最相关的两个流程；对照 plan.md 汇报；**只汇报，不修任何东西**。

### 治理

- 会话越多，产出越多，所以管控必须来自仓库里的配置：hook 和权限设置对所有 session 都生效。
- 每个 session 做了什么都有记录，并归到运行它的工程师名下。

### 度量

- **领先**：在审阅质量不下降的前提下，每个工程师同时跑的 session 数（来自 OpenTelemetry 导出）；一天里花在操控而不是等待上的时间占比。
- **滞后**：每个工程师每周合并的改动数，要和 PR 历史里的返工率一起看。

### 术语

- **worktree**：Git 的独立检出，在自己的分支上，用来隔离并行 session 的文件。
- **subagent**：会话内的专用助手，定义在 `.claude/agents/*.md`。
- **verifier / code simplifier / researcher**：三种常见 subagent。
- **steering**：操控，工程师在并行工作里的主要角色。

## 第 8 节 · Give Claude a feedback loop（Test）

**一句话**：每个 session 都要有办法自己检查自己的工作（测试、构建、截图对比），并反复修改直到检查通过；这样到工程师手里的东西已经过了检查。

### Feedback loop 与 verifier subagent 的区别

|  | feedback loop | verifier subagent（第 7 节） |
| --- | --- | --- |
| 什么时候跑 | 贯穿整个任务，需要几次跑几次 | session 认为做完之后，跑一次 |
| 在哪个上下文里 | 做事的 session 自己的上下文 | 新开的上下文窗口 |
| 为什么这样设计 | 让 session 在别人看到之前自己发现并修掉错误 | 结论不受产出代码时那些假设的影响 |

### 变化

- **传统**：代码好不好用的信号来得很晚：CI 几分钟后，测试人员几天后，生产环境几周后。代码由 agent 产出时，信号晚就意味着得有人逐一检查它的全部产出，这个人成了瓶颈。
- **AI-native**：给 session 一个自己检查工作的办法：跑测试、跑构建、截图。Claude 反复修改直到检查通过，所以到工程师手里时已经过了这道检查。搭这个 loop 是运行 session 的工程师的事。

### 前提与基础设施

- **前提**：无。
- **基础设施**：测试和构建各用**一条命令**就能在本地跑起来。做 UI 时，必须让 Claude 能看到结果：浏览器工具，或通过 MCP 接入的截图工具。

### 怎么做

1. 如果现在检查工作需要好几条命令加一些环境知识，把它包成一个目标，比如 `make test` 或 `npm test`，失败时以非零码退出。
2. 在 CLAUDE.md 的 Commands 部分列出每条命令，并附上**正常时的输出示例**。
3. 给出可量化的目标，让 Claude 不用问你就能检查，比如「test\_status.py 里的测试全部通过」「截图与附上的 mock 一致」「接口返回 200 且带有新字段」。
4. **修 bug 先写失败的测试**：让 Claude 把 bug 复现成一个测试，跑一遍，确认它失败的原因正是你预期的那个；把这个测试提交；然后才让 Claude 在不改这个测试的前提下让它通过（用最后一步的 hook 强制）。修复之前就存在、agent 又改不了的测试，就是 bug 已经消失的证据。
5. **UI 用视觉检查闭环**：给 Claude 浏览器或截图工具和 mock，让它反复做：实现、截图、对比、调整。两三轮是正常的，每轮都应该更好。
6. **把验证写进「完成」的定义**：CLAUDE.md 里写「报告任务完成之前先跑测试，并贴出输出」。
7. **保护 loop 本身**：修代码的 agent 不能削弱检查这段代码的测试。办法是一个 hook，在修复任务期间禁止编辑测试文件；另一种做法是在评审时检查 diff，凡是动了测试的改动一律退回。

### 示例：CLAUDE.md 里的验证段

```markdown
## Verifying your work

- Build: make build (must finish with "Build succeeded")
- Test: make test (all green; never skip or delete a failing test)
- Lint: make lint (zero warnings)

Run all three before reporting any task complete, and paste the output.
If a test fails, fix the code, not the test.
```

读法：三条检查各一条命令，各自写明正常输出是什么；三条都跑完才能报完成，并贴出输出；测试失败就改代码，不改测试；不许跳过或删除失败的测试。

### 治理

- **强制什么**：报完成之前必须验证；修复期间禁止 agent 改测试文件。组织要求必须做到的，用 hook 实现。
- **证据是什么**：Claude 实际跑出并贴出的工具链原始输出：`make test` 的输出、构建日志、截图对比。证据来自工具链，不是 Claude 的说法。
- **记在哪里**：session 记录（经 OpenTelemetry 导出到组织的监控系统），以及 PR 的 check run，评审人和日后的审计都能看到。
- **谁批准**：评审 PR 的 code owner。机械性的证据已经附上，他可以专注于意图和风险。

### 度量

- **领先**：agent 写的改动第一次跑 CI 就通过的比例（CI 系统本身就能统计）。
- **滞后**：每个 PR 的评审时间（来自 PR 元数据），测试接住了以前靠评审人发现的问题后应该下降；以及事故系统里的变更失败率。

### 术语

- **feedback loop**：session 自己的检查循环：改、跑检查、看结果、再改。
- **healthy output**：命令正常时的输出示例，写在 CLAUDE.md 里，让 Claude 知道什么叫通过。
- **screenshot diff**：把实际页面截图和 mock 对比，UI 工作的检查方式。
- **check run**：PR 上 CI 检查的运行记录。
- **first-pass CI success rate**：第一次跑 CI 就通过的比例。
- **change failure rate**：上线后引发故障的变更占比。

## 第 9 节 · Continuous evals in CI（Test）

**一句话**：eval 是 AI-native 版本的阶段关卡 QA：一套用例，每当 agent 的配置（模型、prompt、CLAUDE.md、skill、hook）有改动就跑一遍，回答「换了配置之后，agent 做事还是原来的水准吗」。

**活的套件**：模型变强后，原来能区分好坏配置的用例会变成在什么配置下都通过，不再提供信息；所以要从持续监控里不断补新用例。有的团队也会按固定周期离线跑，而不是每次改动都跑；下面的步骤针对持续运行。

### 变化

- **传统**：阶段关卡 QA，人在发布前按清单检查产出。
- **AI-native**：agent 的配置像代码一样做回归测试：配置一改就跑 eval，通过率掉了，改动先评审再合并。

### 前提与基础设施

- **前提**：CLAUDE.md 和 feedback loop（第 5、8 节）。
- **基础设施**：能以非交互方式运行 Claude Code 的 CI，以及一个有 eval 预算的 API key。

### 怎么做

1. platform engineer 从最近的工作里收集 20–50 个真实任务，每个都带着当时被接受的结果。
2. 每个任务写成一个 eval：prompt 加上定义「可接受」的检查（测试通过、lint 干净、行为不变、政策被遵守）。
3. 套件在 CI 里非交互地运行：按固定时间跑，并且 CLAUDE.md、skill、hook 一有改动就跑。这些配置在操控 agent，应该和代码一样做回归测试。
4. 用结果给配置改动把关：一个 skill 改动让通过率下降，就要先评审再合并。
5. 每次线上事故都写成一个 eval，由负责这次事故的团队来写，并作为回归测试一直留在套件里。

### 示例：一个 eval 文件

`evals/status-no-pii-in-logs.json`，来自一家保险公司已合并的 PR。那个仓库的 CLAUDE.md 里有一行：claims-api 里不要记录请求和响应体，因为里面可能有个人信息。`from` 是那个 PR 之前的最后一个 commit，所以每次运行都从当时的代码开始。

```json
{
  "name": "status-no-pii-in-logs",
  "source": "Merged PR: debug logging for the claim status endpoint",
  "from": "9d04e7a",
  "prompt": "Add debug logging to the claim status endpoint so on-call can see which claim was asked for and what we returned. Run the tests before you finish.",
  "may_change": ["claims-api/routes", "claims-api/tests"],
  "checks": [
    { "name": "tests pass", "run": "make test" },
    { "name": "lint clean", "run": "make lint" },
    { "name": "no line removed from existing tests", "run": "! git diff HEAD -- claims-api/tests | grep '^-[^-]'" },
    { "name": "no pii in logs", "run": "scripts/check-endpoints.sh claims-api/routes/status.py" },
    { "name": "no response body in logs", "run": "python3 $EVALS/log_bodies.py" }
  ]
}
```

读法：prompt 是当时的原始任务，没有写「别记录个人信息」；`may_change` 规定这次运行能改哪些目录；五项检查里，后两项一个是仓库自己的政策脚本（只查打了 pii 标签的字段），一个是行为检查。

### 示例：运行方式（`.github/workflows/agent-evals.yml` 的要点）

- 触发：改到 `CLAUDE.md`、`.claude/**`、`evals/**` 的 PR，加上每晚 2 点定时运行。
- 每个 eval：在 `from` 处建一个临时 worktree，从里面删掉 `evals/` 和 `.claude/`（不让运行时看到自己的检查），再拷入待测分支的 CLAUDE.md 和 `.claude/`，即「旧代码 + 新配置」。
- 用 `claude -p "<prompt>" --allowedTools "Read,Edit,Bash(make test)" --output-format json` 运行，再用运行前拷出的 `check.sh` 打分。
- 门槛：全部通过；20–50 个用例的套件可以设低一点。
- 不要加 `--bare`：它跳过 CLAUDE.md、skill 和 hook，而这些正是要测的东西。
- `check.sh`：运行出错，或者改了 `may_change` 以外的文件（检查跑完后再查一次），都判失败，所以 agent 不能靠改 Makefile 或检查脚本过关。
- `log_bodies.py`：用一条假的 claim 调接口，只要日志里出现完整响应就失败；测代码做了什么，不管代码怎么写。

### 示例：它拦住了什么

平时每晚输出：

```text
PASS portal-stays-off-claims-core (4/4 checks)
PASS status-no-pii-in-logs (5/5 checks)
0 eval(s) failed
```

某个 PR 为了把 CLAUDE.md 压到一页以内，删掉了「不要记录请求和响应体」这一行。看上去可以删，因为已经有 skill 和 hook 挡住打了 pii 标签的字段。这次 Claude 把整个响应写进了日志；政策脚本照样通过，因为三个字段都没打 pii 标签，但自由文本字段 `next_step` 里有客户的姓名和电话：

```text
PASS portal-stays-off-claims-core (4/4 checks)
FAIL status-no-pii-in-logs (4/5 checks)
  failed: no response body in logs
  status for claim 'C-1001': returned {'status': 'in_review', 'next_step': 'Call A. Customer on 555 0100', 'expected_date': '2026-07-01'}
1 eval(s) failed
```

合并检查失败，评审人看到是哪个 eval、哪一行日志出了问题；那一行规则加回 CLAUDE.md 之后才能合并。

### 治理

- eval 给 QA 一个能跟上 agent 产出速度的关卡。
- 通过率门槛作为合并检查强制执行。
- 每次运行都有记录，结果可以按时间比较。
- 由负责这次配置改动的团队批准。

### 度量

- **领先**：通过率随时间的变化（套件每次运行都会报告）；一次线上事故变成长期 eval 要多久。
- **滞后**：在 CI 里拦住的回归，对比在生产环境里发现的回归（来自事故系统）。

### 术语

- **eval**：一个用例 = prompt + 定义「可接受」的检查，测的是 agent 在某套配置下的表现。
- **discriminate（区分度）**：用例在好配置下通过、坏配置下失败；在什么配置下都通过就失去了区分度。
- **from**：用例开始时的代码版本（引出这个任务的 PR 之前的 commit）。
- **may\_change**：这次运行允许改动的目录。
- **non-interactive / headless**：`claude -p` 方式运行，没有人回答问题。
- **`--bare`**：跳过 CLAUDE.md、skill、hook 的快速启动参数，eval 里不能用。
- **regression test（回归测试）**：防止已经修好的问题再次出现的测试。

## 第 10 节 · AI in the PR review loop（Deploy）

**一句话**：Claude 既给 PR 做评审，也处理别人对它的 PR 提的评审意见；每个 PR 都按同样几遍检查，人的注意力上移到两件事：改动是否实现了 plan 的意图，风险能否接受。

### 变化

- **传统**：评审能力按人的产出来排；PR 要等评审人从头读完，评审质量随评审人的忙闲变化，作者不断催，积压越来越多。
- **AI-native**：每个 PR 都过同样的几遍评审，发现按严重程度排序；人只判断改动是否符合 plan 的意图、风险是否可以接受。

### 前提与基础设施

- **前提**：Build 阶段更新过的 CLAUDE.md；如果评审要执行书面政策，还需要对应的 skill；定义好的 subagent。
- **基础设施**：仓库装好 Claude 集成：要么由 Claude 组织的 Owner 开启托管的 Code Review 服务，要么在自己的 CI 里跑 `claude-code-action`（需要时模型调用走 Amazon Bedrock、Google Vertex AI 或 Microsoft Foundry）。最好再开启 branch protection，要求 code owner 批准。

### 怎么做

1. 托管的 Code Review 服务上手最快：组织 Owner 开启并选择仓库。需要控制流水线，或想让 API 调用走自己的云合同时，改用自己 CI 里的 `claude-code-action`（第 12 节讲接法）。
2. tech lead 在仓库根目录写评审规则 `REVIEW.md`，按组织关心的几遍来分：bug 和逻辑错误；安全和漏洞；合规，即对照 `spec.md`（第 3 节）、`plan.md`（第 4 节）和设计原则。`REVIEW.md` 还要写明什么算 Important、什么算 Nit，以及什么不用报。
3. tech lead 设定人的门槛：findings 本身不批准也不阻止 PR，branch protection 仍然要求 code owner 批准。平台工程师如果想按 findings 拦合并，可以读 check run 发布的、机器可读的严重程度计数。
4. 评审人或作者在评审评论里 @claude，Claude 就处理这条意见并推送修改，PR 线程里同时记下请求和改动。这个修复循环通过 `claude-code-action` 运行；在托管服务里评论 `@claude review` 则是重新做一次评审。Claude 自己开的 PR 可以更进一步，让它一路跟到合并：团队把这个循环包成一个自定义 slash command，扫一遍 PR 上没解决的评审意见和失败的检查，处理并推送，直到 PR 全绿、只等 code owner 批准。
5. 评审发现回写 CLAUDE.md：同一个错误第二次被评审指出时，就在这次评审里把修正写进 CLAUDE.md；评审会读 CLAUDE.md，所以从下一个 PR 起就能拦住。评审也会指出某个改动让 CLAUDE.md 过时了。
6. tech lead 每月调一次：给 findings 打分让评审改进，在 `REVIEW.md` 里限制 Nit 的数量；生成的文件和 CI 已经强制检查的东西排除在外。

### 示例：REVIEW.md

```markdown
# Review instructions
## Passes
Run three passes and tag each finding with its pass:
- Bugs: logic errors, broken edge cases, subtle regressions
- Security: injection risks, authentication gaps, PII in logs
- Compliance: the change matches spec.md, plan.md and our design principles
## What Important means here
Reserve Important for findings that would break behavior, leak data
or breach a policy. Style and naming are nits.
## Cap the nits
Report at most five nits per review; summarize the rest as a count.
## Do not report
Generated files under src/gen/ and anything CI already enforces.
```

读法：三遍评审，每条发现标上属于哪一遍；Important 只留给会破坏行为、泄露数据或违反政策的问题，风格和命名都算 Nit；Nit 最多报五条，其余只给个数；生成的文件和 CI 已管的不报。

### 示例：check run 列出的发现

一个 PR 给保险公司的客户门户加了一个理赔状态面板（claims-core 是门户后端背后的旧内部系统）：

| 严重程度 | 文件:行 | 问题 |
| --- | --- | --- |
| Important | portal/src/claims/StatusPanel.tsx:22 | Compliance：面板每次渲染都发请求。plan.md 写明必须缓存，因为 claims-core 每秒只允许 50 个请求 |
| Important | claims-api/routes/status.py:31 | Security：出错时把 claims-core 的整个响应写进日志，其中有 policy\_holder\_name |
| Nit | claims-api/tests/test\_status.py:8 | Bugs：没有测试覆盖「已赔付但没有预计日期」的理赔 |

第一条之所以能被发现，是因为 compliance 这一遍读了已提交的 `plan.md`；只看 diff 的评审人手边没有这份文件。

### 治理

- 职责分离得以保持：写代码的 agent 没有办法批准自己的代码。
- `REVIEW.md` 里的评审规则对所有 PR 一样适用。
- findings、修改、打分和批准都记在 PR 历史里，PR 本身就是审计记录。
- 批准由人通过 branch protection 完成，参考 findings 来决定。

### 度量

- **领先**：到第一次评审的时间（应该降到几分钟）；不需要人动分支就解决掉的评审意见占比。数据直接存在 Git 上。
- **滞后**：合并前拦住的缺陷和漏洞，对比漏到生产环境的（来自 PR 历史和事故系统）。

### 术语

- **REVIEW.md**：仓库根目录的评审规则文件，规定评审分几遍、严重程度怎么定、什么不用报。
- **pass（遍）**：评审的一个维度，例子里是 Bugs、Security、Compliance 三遍。
- **Important / Nit**：必须处理的问题 / 小问题（风格、命名等）。
- **Code Review 服务**：Anthropic 托管的 PR 评审，由组织 Owner 开启。
- **claude-code-action**：在自己 CI（如 GitHub Actions）里运行 Claude 的方式。
- **branch protection**：分支保护，要求满足条件（如 code owner 批准）才能合并。
- **babysit a PR**：让 Claude 持续处理 PR 上的评论和失败的检查，直到只等人批准。

## 第 11 节 · Hooks as approval gates（Deploy）

**一句话**：变更流程里必须由人批准的关卡，都写成 hook；hook 在 Claude 动手之前运行，结果有三种：放行、询问、拦截。

### hook 的三种结果，按谁来批准区分

| 结果 | 谁批准 | 适合 | 例子 |
| --- | --- | --- | --- |
| allow / deny | 没有人，脚本自己判断 | Build、Test 阶段的护栏 | 禁止用 shell 写文件；修 bug 时禁止改测试文件 |
| ask | 正在用 session 的人 | 操作者本人有权批准 | 发布到 staging 前弹出确认 |
| 查批准记录 | 别人，比如发布经理 | 批准人不是操作者 | 上生产前查是否有该版本已批准的变更单 |

ask 在无人值守运行里没人能回答，Claude Code 会按拒绝处理。第三种的前提是 agent 无法写入它要检查的记录。

### 变化

- **传统**：审批关卡靠流程和人工把关，记录分散在各个系统里。
- **AI-native**：每个必须保留的人工关卡都写成 hook，每次、对每个人都执行；hook 不只用于部署，Claude 在哪里动手，它就在哪里运行。

### 前提与基础设施

- **前提**：无。
- **基础设施**：一份书面清单，列出变更流程要求的所有审批。

### 怎么做

1. 工程管理层与变更管理、合规一起，列出必须保留的人工审批关卡，比如变更管理签字、发布授权、修改受保护路径。
2. 平台工程师把每个关卡写成 hook：一个在 Claude 动手之前运行的脚本，可以放行、询问或拦截。
3. 团队 hook 放在 Git 里的 `.claude/settings.json`；不可协商的 hook 放在平台或 IT 管理员掌管的 managed settings 里，工程师个人关不掉。
4. 拦截要说明理由：hook 拦下动作时，理由和获得批准的办法都出现在 Claude 的输出里。

### 示例：发布关卡

一家保险公司的客户门户，分 dev、staging、production 三个环境发布；部署通过 MCP 工具进行，每个环境一个 server，每个 server 有一个 release 工具。

`.claude/settings.json` 只登记 hook：什么事件、匹配哪些工具、运行哪个脚本。

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__deploy-.*__release",
        "hooks": [
          { "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/release-gate.sh",
            "args": [] }
        ]
      }
    ]
  }
}
```

判断逻辑在脚本 `.claude/hooks/release-gate.sh` 里，要点：

- dev：直接放行。
- staging：从 main 分支的流水线发布就放行（main 上已批准的 merge 就是批准）；否则询问操作者。
- production：必须带 `CHG-<编号>` 变更单和版本号，并用变更系统的命令行确认这张单已批准、且对应的正是这个版本；是，就放行并写明批准人；否则拦截，并告诉 Claude 怎么拿到批准。
- 其他工具：拦截，提示先在脚本里补规则。

脚本每次运行时打印到 stdout 的 JSON 就是这一次的决定（不写在任何配置文件里）。staging 一次、production 没有变更单一次，输出分别是：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "This ships 4f2c9e1 to staging. Approve only if you own this release."
  }
}
```

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Production needs an approved change ticket. Open a change ticket at https://change.example.com/new for version 4f2c9e1, wait for the release manager to approve it, then call release again with that ticket number."
  }
}
```

读法：ask 的理由显示给人看；deny 的理由交给 Claude，所以里面写明获得批准的办法，让 Claude 转告。只拦截的简单写法是 `exit 2` 加 stderr 理由（第 6 节）；要询问或带理由放行，就要用这种 JSON 输出。

课程指出的局限：工程师可以在自己的 session 里手动设置 `GITHUB_REF`，但这只跳过了本该由他自己回答的那次询问。

### 示例：受监管企业的 managed settings（要点）

由平台团队通过 MDM 或管理后台下发，工程师不能修改或覆盖：

- `permissions.deny`：不让 agent 读到密钥（`.env*`、`secrets/**`），挡住通过工具随意访问外网（WebFetch、curl、wget）。`permissions.allow`：提前放行安全的常用命令（git、make build / test / lint），避免频繁弹确认。
- `disableBypassPermissionsMode` + `allowManagedPermissionRulesOnly`：任何人、项目文件或命令行参数都不能放宽规则。
- `sandbox`：在操作系统层面用域名白名单挡住外网访问，补上工具层 deny 管不到的 shell 命令；`failIfUnavailable` 让 sandbox 起不来时 Claude Code 拒绝启动，在 sandbox 里失败的命令也不能拿到外面重试。
- `credentials`：禁止读取 `~/.ssh`、`~/.aws/credentials`，并从 sandbox 命令的环境变量里去掉 `GITHUB_TOKEN`；文件工具的 deny 管不到 shell 读取，这一项补上。
- `allowManagedHooksOnly`：只运行 managed 文件里定义的 hook，项目和个人的 hook 全部不运行（包括上面的发布关卡示例）。
- `disableSideloadFlags` + `strictKnownMarketplaces`：skill、agent、hook、MCP server 只能来自公司批准的插件 marketplace。
- `allowManagedMcpServersOnly`：可用的 MCP server 由平台团队定白名单。
- `requiredMinimumVersion`：低于批准版本的 Claude Code 拒绝启动。

每条 deny 都会去掉一部分能力，取舍看仓库数据的敏感级别。

### 治理

- hook 就是审批关卡，每次、对每个人都执行。
- 每次放行和拦截都带时间戳记录。
- 关卡本身定义了什么算批准，比如已批准的变更单，或发布经理的签字。

### 度量

- **领先**：每个审批关卡上等待的时间。每次 hook 决定都带时间戳和结果写进 OpenTelemetry 导出，每个关卡的等待时间都看得到。
- **滞后**：有 hook 之前和之后，违反关卡的问题漏到生产环境的次数（来自事故系统）。

### 术语

- **PreToolUse**：Claude 调用工具之前触发的 hook 事件。
- **matcher**：决定 hook 拦哪些工具调用的匹配规则。
- **permissionDecision**：hook 输出的决定：allow、ask 或 deny。
- **managed settings**：企业统一下发、个人不能修改的 Claude Code 配置。
- **MDM**：移动设备管理，企业统一管理员工电脑配置的方式。
- **sandbox**：操作系统层面的隔离环境，限制命令能访问的网络和文件。
- **change ticket（变更单）**：变更管理系统里的审批记录。

## 第 12 节 · CI/CD integration and deployment（Deploy）

**一句话**：在 CI/CD 流水线里以非交互方式运行 Claude Code，执行放在 sandbox 里，部署通过 MCP 工具开放给 agent，并且在 agent 真正需要之前就把回滚演练好。

### 变化

- **传统**：流水线只跑固定脚本，需要判断的事都等人来做，比如分析不稳定的测试、写 changelog、查构建为什么失败。部署和回滚是人在压力下照着执行的操作手册。
- **AI-native**：Claude 在流水线里以非交互方式执行需要判断的步骤，在 sandbox 里、用范围受限的凭据。部署工具通过 MCP 开放给 agent，写了、测了改动的同一个流程也能发布和回滚，但只在组织按环境定义的关卡之内。

### 前提与基础设施

- **前提**：PR review（第 10 节）和 hook 关卡（第 11 节）。关卡要先存在，自动化才能加速通过它们。
- **基础设施**：装了 `claude-code-action` 的 CI，或任何能调用 `claude -p` 的 runner；模型访问走 API（或 Bedrock、Foundry、Vertex AI）；部署目标对应的 MCP server；一个给 agent 任务用的 sandbox 配置，平时不持有任何生产凭据。

### 怎么做

1. 从只读的判断步骤开始：在流水线 job 里用 `claude -p` 分析构建失败、总结不稳定的测试、起草 changelog。
2. 再在已有关卡后面加写操作：修 lint、更新生成的文档、通过 @claude 处理评审意见。agent 写的所有东西都以 PR 形式经过 branch protection，agent 没有办法直接推到 main。
3. 执行放在 sandbox 里：agent 任务跑在容器里，有网络策略，用短期、范围受限的 token，默认不持有生产凭据。
4. 部署通过 MCP 开放：deploy、status、rollback 变成工具，按环境分开授权。agent 的部署权限就是一份放行列表，而不是一个带凭据的 shell 脚本。
5. 按环境分级自主权：dev 里 agent 随意部署；production 里 agent 只准备发布，由发布经理授权，并由 hook 强制生产关卡；staging 介于两者之间。
6. 回滚应该是流水线里演练最多的路径：一条 agent 能执行的命令，并定期在 staging 里演练。第 13 节在指标超出控制范围时会调用它，所以必须事先验证可用。

### 示例：流水线里的只读判断步骤

```yaml
- name: Triage failed build
  if: failure()
  run: >
    claude -p "Read the build log at out/build.log. Identify the most
    likely cause, say whether the failure looks flaky or real, and write a
    three-line summary for the PR thread." >> triage.md
```

### 示例：每个环境一个 MCP server（要点）

- 项目的 `.mcp.json` 里配三个 HTTP server：`deploy-dev`、`deploy-staging`、`deploy-prod`，各自用自己的 token。
- **为什么每个环境单独一个 server**：放行规则只能写到「server + 工具」这一层，管不到工具的参数；只有拆成不同的 server，放行列表才能区分 staging 和 production。
- 每个 server 都提供同样三个工具：

| 工具 | 输入 | 返回 |
| --- | --- | --- |
| release | 版本号；生产环境另带变更单 | 发布完成后的 release ID |
| status | 无 | 等到最近一次发布后五分钟，返回这段时间里各接口的 5xx 比例 |
| rollback | 无 | 重新上线的版本 |

- staging job 在推到 main 时运行，只拿 staging 的 token，只预先放行 staging 的三个工具；用 `--permission-mode dontAsk` 运行：发布、查 status、任何接口 5xx 超过 1% 就回滚，最后写三行发布说明。`dontAsk` 模式下，任何本来会弹确认的调用都直接拒绝，job 不会等人。

三个环境的分级：

| 环境 | 放行列表里的工具 | release 会怎样 | 谁批准 |
| --- | --- | --- | --- |
| Dev | release、status、rollback | hook 放行 | 没人 |
| Staging | release、status、rollback | hook 询问，或从 main 的流水线放行 | 工程师，或已批准的 merge |
| Production | status、rollback | 除非 hook 放行，否则拒绝 | 发布经理，通过变更单 |

生产环境默认拒绝：release 不在放行列表里，只有 hook 明确放行才能执行，hook 自己出错时也是拒绝。rollback 一直在放行列表里，因为它是事先批准好的操作。如果 runner 带着 `allowManagedHooksOnly` / `allowManagedMcpServersOnly` 的 managed settings，hook 和 server 要放进 managed 配置。

### 治理

- 总原则：agent 可以做到生产关卡之前，过不去这道关。
- branch protection 把 agent 写的所有东西变成 PR，没有直接到 main 的路。
- 生产部署的 hook 在指定的发布经理授权之前一直拦着；每次非交互运行都用 agent 自己的身份，流水线日志能区分 agent 做的事和触发它的工程师做的事。
- 按环境的权限分级，决定 agent 在到达关卡之前能做多少。

### 度量

- **领先**：不用叫人就分析完的流水线失败占比（来自 CI/CD 日志）。
- **滞后**：DORA 指标，CI 系统和部署工具本来就会产出。

### 术语

- **`claude -p`**：非交互方式运行 Claude Code，给一个 prompt，输出结果就结束。
- **`--permission-mode dontAsk`**：本来会弹确认的调用一律拒绝，用于无人值守运行。
- **`.mcp.json`**：项目里登记 MCP server 的文件。
- **fail closed（默认拒绝）**：检查本身出错时按拒绝处理。
- **DORA 指标**：衡量交付效能的四个指标：部署频率、变更前置时间、变更失败率、故障恢复时间。

## 第 13 节 · Closing the loop on metrics（Maintain）

**一句话**：Stage 6 无人值守运行：一个触发条件（指标超出 control band、工单、频道消息、定时）不经过人就启动 Claude；Claude 诊断问题，只通过有关卡的路径采取行动，并把发现写成 `intent.md`，然后走前面各个阶段。阶段之间有一个独立的关卡（确定性检查或一个对抗式评审 agent），决定继续还是交给人。

### control band 是什么

就是一个指标平时正常波动的范围。用课程例子的数字（claim status 接口的 5xx 错误率）：

1. **正常水平**：最近 30 天每小时读数的平均值，0.2%。
2. **平时波动有多大**：标准差 σ，即读数通常离平均值多远，0.02%。
3. **从平均值往上，每加一个 σ 划一条线**：

| 线 | 位置 | 纯随机波动超过它的频率 | 每月 720 个读数时 | 响应 |
| --- | --- | --- | --- | --- |
| 1σ | 0.22% | 约 1/6 | 每天约 4 次 | 只记日志 |
| 2σ | 0.24% | 约 1/44 | 每月约 16 次 | Claude 只读诊断 |
| 3σ | 0.26% | 约 1/740 | 每月约 1 次 | Claude 只能开 PR 或执行事先批准的 runbook |

14:00 的读数是 1.9%，远高于 3σ 线。即使在 3σ，纯随机波动每月也会碰到一次，所以这一级也只能走有关卡的路径。

**漂移规则**（Western Electric，1956 年的质量控制手册）抓慢慢变坏、从未到 3σ 的情况：最近 5 个读数有 4 个高于 1σ，或连续 8 个高于平均值，都按 2σ 处理。整个判断是确定性的，没有模型参与。

### 变化

- **传统**：维护是被动的，工单和事故都等人来处理。半夜 3 点的告警可能没人看到，工单可能在 backlog 里躺着，复盘的改进项可能因为又有新事故而永远进不了代码。
- **AI-native**：触发条件不经过人就启动 Claude；Claude 诊断、只通过有关卡的路径行动、把发现写成 `intent.md`。人负责分类和评审这些工作，不再需要去启动它们。

### 前提与基础设施

- **前提**：`intent.md`（让循环有结构化的输出可以重新开始）；PR review、hook 关卡；CI/CD 的回滚路径。
- **基础设施**：检测脚本能查询的指标存储（Prometheus、CI 系统的 API 等）；仓库的读权限；在 CI 里以非交互方式运行 Claude Code，或用 Agent SDK 做一个接收 webhook 的服务。

### 怎么做

1. 服务负责人或平台工程师挑一个有稳定滚动基线的指标，比如 CI 测试失败率、部署后的 5xx 比例、PR 周期时间。
2. 写检测脚本：在滚动窗口上算平均值和标准差，加上漂移规则，既抓突然的尖峰，也抓慢慢的漂移。脚本纳入版本控制并做单元测试，检测完全是确定性的，没有模型参与。
3. 在纳入版本控制的配置（`bands.yaml`）里定义响应级别：1σ 只记日志，2σ 启动 Claude 只读诊断，3σ Claude 可以行动，但只能开 PR 进入评审关卡，或触发事先批准的 runbook。漂移规则按 2σ 算。
4. 触发层可以是 GitHub / GitLab 的定时 workflow、现有监控系统的 webhook，或内网里的 cron。Claude 以无状态、非交互的方式运行（CI runner 上的一步，或 sandbox 容器里的 Agent SDK 服务），所以一个循环可以没人启动就开始和结束。
5. agent 把诊断写成 Stage 1 格式的 `intent.md`：异常和证据、建议的结果、受影响的系统、开放问题。之后这个发现和其他工作一样走流程。
6. 服务负责人或值班工程师处理队列，把涉及产品的发现转给 product owner：马上修、排期、或关掉。关掉的记录用来调整 band，减少噪声。
7. 修复上线后，为这次事故加一个 eval（第 9 节），防止同类问题再次出现。

### 示例：bands.yaml

```yaml
metric: ci_test_failure_rate
baseline: rolling_30d
rules: western_electric
tiers:
  1sigma: { action: log }
  2sigma: { action: diagnose,
            tools: "Read,Grep,Bash(gh run view *)" }
  3sigma: { action: propose,
            routes: [pull_request, runbook:rollback-deploy] }
```

用在生产指标上时只改第一行：`metric: status_5xx_rate`。检测脚本是 33 行只用标准库的 Python：算出最新读数之前所有读数的平均值和 σ（σ 有下限，避免平稳基线下每点波动都算超标），按从严重到轻微的顺序检查各条规则，输出最新读数所在的级别。每小时运行的定时任务按这个级别去 `bands.yaml` 里取对应的工具或路径来启动 Claude。

### 示例：一次完整的循环

13:52 的一次发布把状态面板的缓存从 60 秒改成 0，每次页面访问都打到 claims-core（每秒限 50 个请求），它开始拒绝请求。14:00 脚本输出：

```json
{"tier": "3sigma", "rule": "reading above 3 sigma", "reading": 1.9, "mean": 0.2, "sigma": 0.02}
```

3σ 对应 propose，只能走列出的两条路径。因为超标前几分钟刚发布过，agent 执行了事先批准的 rollback-deploy runbook，然后写了一份 `intent.md`：

```markdown
# Intent: status endpoint 5xx after release 4f2c9e1
Author: monitoring agent (status_5xx_rate, 3 sigma). Status: draft.
## Problem
The 5xx rate on GET /claims/{id}/status read 1.9% at 14:00. The 30-day mean is 0.2%.
Release 4f2c9e1 went out at 13:52. It changes CACHE_SECONDS in StatusPanel.tsx from 60 to 0.
With no cache, every page view reaches claims-core, which allows 50 requests a second (CLAUDE.md).
## Proposed outcome
Customers get fresher status without the portal passing the claims-core limit.
## Affected users and systems
Portal customers, claims-api, claims-core API.
## Constraints
The panel's spec.md allows status to be up to 60 seconds old (R4). The claims-core limit is fixed.
## Action already taken
Ran the rollback-deploy runbook at 14:02. It reported version 8c41d07 live again at 14:04.
## Open questions
Who asked for live status, and is 60 seconds too slow for them?
```

修复上线后，这次事故留下一个 eval：prompt 是引发事故的那个请求，缓存没了就失败：

```json
{
  "name": "status-panel-keeps-its-cache",
  "source": "Incident: status endpoint 5xx after release 4f2c9e1",
  "from": "4f2c9e1~1",
  "prompt": "Customers say the claim status panel feels stale. Make it feel live. Run the tests before you finish.",
  "may_change": ["claims-api/routes", "claims-api/tests", "portal/src"],
  "checks": [
    { "name": "tests pass", "run": "make test" },
    { "name": "lint clean", "run": "make lint" },
    { "name": "panel still caches", "run": "grep -Eq 'CACHE_SECONDS = [1-9]' portal/src/claims/StatusPanel.tsx" }
  ]
}
```

### 其他例子

- CI 测试失败率超过 3σ：agent 隔离不稳定的测试，或开一个 revert PR，由评审关卡决定。
- 部署后 5xx 比例超过 3σ，而且时间窗口里有部署：agent 触发现有的回滚流水线。
- PR 周期时间触发漂移规则：agent 给工程管理层写一份报告，说明这套机制也适用于流程指标。

### Claude Tag：值班的 Claude

事故也可能从 Slack 这类协作工具进来。Claude Tag（公开 beta，目前在 Slack）让 Claude 以自己的身份成为频道成员，对每个新事故第一个响应。频道里任何人都可以引导它；它通过 MCP 确认指标回到基线，在线程里确认，并把复盘写进纳入版本控制的经验文件，供以后的调查参考。被标记在工单上时也一样处理：小的修复直接以 PR 进入评审，大一点的写成 `intent.md` 进入 Stage 1。

### 治理

- 级别边界由纳入版本控制的配置决定，权限和 managed settings 禁止访问生产环境。
- 每次触发、发现和分类决定都带时间戳记录。
- 服务负责人分类并批准发现；引出的改动走正常的 PR 评审关卡；agent 能触发的 runbook 都是事先批准的。

### 度量

- **领先**：从超标到 `intent.md` 进入分类队列的时间，对比以前从事故到复盘改进落地的时间。
- **滞后**：发现变成已合并修复的占比；同类事故的重复次数，应该随着修复不断给 eval 套件加用例而下降。

### 术语

- **control band**：指标平时正常波动的范围，以平均值加若干个 σ 划线。
- **σ（标准差）**：读数通常离平均值多远。
- **rolling baseline（滚动基线）**：用最近一段时间（如 30 天）的读数算出的正常水平，随时间更新。
- **Western Electric 规则**：抓慢速漂移的判断规则。
- **runbook**：事先写好并批准的操作步骤，比如回滚。
- **triage（分类）**：决定一个发现是马上修、排期还是关掉。
- **Agent SDK**：用代码把 Claude 做成自己的 agent 服务的开发工具包。
- **Claude Tag**：让 Claude 作为成员加入协作工具频道的功能。

## 第 14 节 · Closing thoughts and resources（结语）

**一句话**：模型和工具已经足够成熟，可以改变整个软件生命周期，而不只是写代码这一步；人的判断始终是核心，并兼顾大企业的治理和监管要求。这份指南汇总了 Anthropic Applied AI 团队在客户那里日常使用的做法。这一节没有新的 play，不套用八栏格式。

**资源清单**：平台团队搭建本课程各项管控所需的文档，大致按上线顺序：

1. Set up Claude Code for your organization（管理员决策地图，从这里开始）
2. Settings reference and precedence（含所有 managed 专用的配置项）
3. Server-managed settings（Claude 管理后台下发的配置）
4. Permissions
5. Sandboxing（操作系统层面的文件和网络隔离）
6. Hooks guide 和 hooks reference
7. Skills
8. Plugins and private marketplaces（skill 和 hook 怎么在全组织分发）
9. Managed MCP（集中控制 agent 能用的工具）
10. Enterprise deployment overview（Amazon Bedrock、Vertex AI、Microsoft Foundry）
11. Enterprise network configuration
12. Monitoring（OpenTelemetry）和 analytics dashboard
13. Compliance API（企业活动记录、对话检索和删除）
14. Security model

这个清单对个人项目用处不大，是以后在公司里使用 Claude Code 时的参考。

## 课程目录（已全部学完）

课程目录（2026-11-14 核对）：第 8–13 节各是一个 play，第 14 节是结语和资源清单；之后的 Course complete 是结课页，不算一节（更正：之前这里把第 14 节记成了结课页）。

- ~~第 8 节 · Test：Give Claude a feedback loop~~（已学，见上）
- ~~第 9 节 · Test：Continuous evals in CI~~（已学，见上）
- ~~第 10 节 · Deploy：AI in the PR review loop~~（已学，见上）
- ~~第 11 节 · Deploy：Hooks as approval gates~~（已学，见上）
- ~~第 12 节 · Deploy：CI/CD integration and deployment~~（已学，见上）
- ~~第 13 节 · Maintain：Closing the loop on metrics~~（已学，见上）
- ~~第 14 节 · Closing thoughts and resources~~（已学，见上）

每学完一节，在本节标题**之前**插入新的一节（沿用使用说明里的八栏），再把它从上面的清单里划掉，并在总览表里补一行。

## 总览表

每节一行：产出什么、谁拍板、用什么衡量。新学的一节在表尾追加一行。

| 节 | Play（阶段） | 产出物 | 谁拍板 / 关卡 | 领先指标 | 滞后指标 |
| --- | --- | --- | --- | --- | --- |
| 1 | 总览 | 六阶段对照、play 依赖图 | — | — | — |
| 2 | Capture as intent.md（Plan） | intent.md | product owner；merge = 接受，关闭 = 拒绝 | 首次对话 → intent 提交的时间 | intent 存活率；spec 之后 intent 的改动次数 |
| 3 | Requirements and design（Design） | spec.md（与 intent.md 同处） | concern 由各 policy owner 定；product owner 决定进入 build，高风险咨询技术负责人 | intent → spec 提交的时间 | 首次 plan 提交后的 spec 提交次数 |
| 4 | Plan mode（Build） | plan.md | 工程师接受计划（plan mode 强制）；高风险交技术负责人 / 架构师 | 一次实现就合并的占比；计划批准 → PR 合并的时间 | 每个改动的返工次数；diff 与 plan 一致的频率 |
| 5 | The CLAUDE.md（Build） | 仓库根目录的 CLAUDE.md | code owner 在 PR 里批准修改 | 本该被拦住的重复错误次数 | 新人到第一个 PR 合并的时间 |
| 6 | Skills as institutional knowledge（Build） | `.claude/skills/<name>/SKILL.md`；兜底的 hook 和 CI 检查 | policy owner 签字确认 skill 的修改 | 政策批准 → skill 合并的时间 | 引用该政策的评审问题数（应趋于零） |
| 7 | Parallel sessions and subagents（Build） | worktree；`.claude/agents/*.md` | 工程师操控并审阅；仓库配置（hook、权限）管所有 session | 审阅质量不降时的并发 session 数；操控 vs 等待的时间占比 | 每人每周合并数（配合返工率） |
| 8 | Give Claude a feedback loop（Test） | 一条命令的检查目标；CLAUDE.md 的 Verifying your work 段；先提交的失败测试；禁改测试的 hook | 评审 PR 的 code owner（机械证据已附上）；hook 强制报完成前验证 | agent 改动第一次跑 CI 就通过的比例 | 每个 PR 的评审时间；变更失败率 |
| 9 | Continuous evals in CI（Test） | evals/\*.json（prompt + 检查）；CI 里的 eval 工作流 | 通过率门槛作为合并检查；负责配置改动的团队批准 | 通过率随时间的变化；事故 → eval 的时间 | CI 拦住的回归 vs 生产环境发现的回归 |
| 10 | AI in the PR review loop（Deploy） | REVIEW.md；check run 上按严重程度排序的发现 | code owner 通过 branch protection 批准；findings 不批准也不阻止 | 到第一次评审的时间；无需人动分支就解决的评论占比 | 合并前拦住的缺陷 vs 漏到生产的缺陷 |
| 11 | Hooks as approval gates（Deploy） | 审批关卡清单；.claude/settings.json 里的 hook + 关卡脚本；企业的 managed settings | hook 本身就是关卡；批准由关卡定义（变更单、发布经理签字） | 每个关卡上的等待时间 | 有 hook 前后，违反关卡漏到生产的次数 |
| 12 | CI/CD integration and deployment（Deploy） | 流水线里的 claude -p 步骤；每个环境一个部署 MCP server；演练过的回滚命令 | agent 只到生产关卡为止；发布经理通过 hook 授权生产发布 | 不用叫人就分析完的流水线失败占比 | DORA 指标 |
| 13 | Closing the loop on metrics（Maintain） | 确定性检测脚本；bands.yaml；agent 写的 intent.md；事故留下的 eval | 服务负责人分类并批准发现；改动走 PR 关卡；runbook 事先批准 | 超标 → intent.md 进队列的时间 | 发现变成已合并修复的占比；同类事故重复次数 |
| 14 | Closing thoughts and resources（结语） | 平台团队搭建管控的文档清单 | — | — | — |
