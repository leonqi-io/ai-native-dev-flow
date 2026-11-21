# 试点期间的度量

全部从 Git、Approval log 和手工记录里读，不设阈值，不建采集工具。用途是试点之后做几个已经说好要做的判断。每个改动收尾时顺手记一行。

## 试点后要做的判断，和各自看什么

| 判断 | 看什么 | 怎么数 |
|---|---|---|
| skill 的触发说法够不够 | Claude 没选 skill 或选错 skill 的次数，分开记是哪个 skill | 手工。出现真实的漏选或错选，改那个 skill 的 description 并补一个用例 |
| 问答问得太粗 | plan 批准之后 spec.md 又改了几次；验收里属于「本该问到」的发现有几条 | `git log` 看 plan 提交之后 spec.md 的提交；验收记录 |
| 问答问得太细 | 按默认答案回答、并且没让草稿发生变化的问题有几个；问答花的时间 | 手工，在 spec 接受时记一行 |
| plan 的预读要不要建议用 Fable | plan 批准之后 spec.md 的改动次数有没有变多 | 同上第二行。变多时建议 owner 让预读（reviewer subagent）用 Fable，主 session 不换 |
| code-reviewer 留不留 | 它的发现里有多少导致了代码改动；owner 遇到看不懂的代码是不是变少了 | 手工，每次实现结束时记「报了几条、改了几条」 |
| 小改动的界线要不要收紧 | 被后来的新 session 评审判为「行为变了」的小改动有几个 | Approval log 里 `small-change read … behaviour changed: yes` 的条数 |
| 批准句和点击各自留不留 | 批准句有没有误触发（一句普通的话被当成批准）或漏触发；小改动的两次点击用下来顺不顺；`ask` 在各权限模式下的表现 | 手工。误触发出现一次，就把那一句换成更长的 |
| 高风险档留不留，还是改成按事实触发 | session 在那一屏建议 Fable 几次、带的是什么事实、owner 接受没有；owner 在那一屏改过几次档位 | 手工，收尾时记。第二个试点改动之后看 |
| 一个改动一个 session 撑不撑得住 | R 条数、改动的文件数，和有没有发生上下文压缩 | 收尾时记；压缩看 session 里有没有出现压缩的提示 |
| owner 是不是只坐下来两次 | owner 坐下来几次、中途被叫到几次（分开记被叫的原因） | 手工，收尾时记 |
| 配置是不是在变差 | 一次通过率（实现后第一次评审就没有 Important）；每个改动的修复轮数；同一个错重复出现的次数 | Approval log 里 review 行的条数和 Important 数；CLAUDE.md 里两次即记的新增行 |

## 每个改动收尾时记的一行

记在这份文件末尾，一行一个改动：

```
<文件夹名> · 档位（owner 改过没有）· Fable 的建议（无 / 有：事实，接受没有）· 问答轮数 / 默认答案未改草稿的问题数 · plan 后 spec 改动次数 · 评审轮数 / Important 总数 · code-reviewer 报几条改几条 · skill 漏选或错选（哪个）· R 条数 · 改动的文件数 · 上下文压缩（有 / 无）· owner 坐下来几次 / 中途被叫到几次 · 备注
```

## 记录

- 2026-11-18-scaffold-content-model（飞猫）· 高风险 · 问答轮数不知道 / 不知道 · plan 后 spec 改动 4 次（R36 的例外、R32 改写、R8、spec 第 5 行的例外句）· plan 二读 1 轮 6 条 Important（复核后 0）；分支评审 1 轮 1 条 Important，之后复核 3 轮都是 0 · code-reviewer：Build 报 15 改 13，验收后的修复轮报 3 改 1 · skill 漏选或错选：无 · R 44 条 · 改动的产品文件 141 个（多数是测试样例）· 上下文压缩：不知道 · owner 坐下来几次 / 被叫到几次：数不清（多 session 的形状，见 `docs/pilot.md` 11-19 22:02 owner 的判断）· 验收 6 步 1 失败（品牌名），修复后重验 1 步 0 失败；这次走完之后改成一个改动一个 session
- 2026-11-20-sync-review-md（飞猫）· 小改动（owner 没改）· Fable 的建议：无 · 问答：小改动没有 · plan 后 spec 改动：小改动没有 spec · 评审：verifier（Opus）一轮，Important 0、Nit 1，行为没变 · code-reviewer 报 0 条 · skill 漏选或错选：无 · R 条数：无 · 改动的产品文件 1 个（REVIEW.md）· 上下文压缩：不知道 · owner 坐下来 1 次、点击 2 次，中途被叫到 0 次 · 新形状下的第一次真实使用；记了 3 条待办（都是飞猫的 CLAUDE.md 落后于模板）
- 2026-11-20-blog（飞猫，阶段 3 的 A 部分：博客导入）· 正常档（owner 没改）· Fable 的建议：无 · 问答：intent 阶段 1 轮 4 题全按默认（其中 1 题因为 owner 另外确认 caribbean 已发布，草稿变了），spec 阶段几轮没问到 · plan 后 spec 改动 2 次提交（R23 连注释也拒绝 = owner 在 plan 上的新裁定；第 3 行回填哈希 = 模板问题；Amendments 一行跟着 R23 改），都不是问答漏问 · reviewer 3 轮，Important 1、1、0；verifier 6 次，Important 2、1、0、1、0、0；合计 6 条，一次通过：否 · code-reviewer 6 次报 27 条，第一次的 12 条全改，其余没有逐条数 · skill 漏选或错选：没发现 · R 28 条 · 产品文件 7 个（不算测试）、测试和样例 45 个、另有 `CLAUDE.md` · 上下文压缩：无（结尾 461k / 1.0M，Opus 5.5 high，输出 222k） · owner 坐下来：按设计 2 次，实际 3 段（开头那一次被他自己离开约 3 小时分成两段：14:48–15:34、18:42–19:21；结尾 20:36–21:11），中途被叫到 0 次 · 新形状下第一个正常档；开场到合并墙钟 6 小时 23 分，其中实现和评审循环 69 分钟；拆分是 session 在写 spec 之前提的；plan 上打回 1 次；判断题 2 道，J1「不判断」（问错了对象）、J2 通过；遗留项 12 条（10 条进「To do」、2 条进「Known limits」），「To do」从 8 行到 15 行；PR #2。owner 把 session 的输出拿到陪跑这边 7 次，拆分、J1、J2 三处判断受陪跑影响，不算 flow 自己的表现
- 2026-11-21-article-template（飞猫，阶段 3 的 B 部分：文章模板）· 正常档（owner 没改）· Fable 的建议：无 · 问答：spec 阶段 1 轮 · plan 后 spec 改动：plan 批准时 4 处（预读 I1–I3、N1 和 owner 对三个裁定点的默认答案），结尾 J1 失败后 1 处（页脚改三栏：R21、C2、Fact values、`mock.html`、T17；Kitty 经 owner 的裁定）——后一处起因是 mock 没有单独审（见 `docs/pilot.md` 2026-11-21 12:25），不是问答漏问 · verifier 4 次，Important 1、0、0、0；reviewer 5 次，Important 1、0、1、1、0（review-3、4 的 I1 是截图不对：旧截图、非 390 px 设备模拟）；一次通过：否 · code-reviewer 3 次，按报告条目约 17、8、6 条，改了几条没逐条数 · skill 漏选或错选：没发现 · R 29 条 · 产品文件 22 个（不算测试），测试和样例 22 个，另有 `CLAUDE.md`、`references/mockups/README.md`、blog-import 的 `site-version.md` · 上下文压缩：无；plan 批准时 24%（238k），owner `/clear` 后说「继续」接上实现第一步，顺；到「确认合并」前 45%（453k / 1.0M），输出 190k，Opus 5.5 high · owner 坐下来：开头（intent、spec、plan）和结尾（J1–J3，J1 失败、修复轮之后再判）；中途被叫到 0 次 · 实现 11:17 起，12:17 到第一次结尾那一屏，J1 修复轮 13:05–13:33，J1–J3 通过 14:24–14:35；遗留 L1–L12（10 条进「To do」，L11 等阶段 4，L12 宽屏侧栏）；收尾检查七项全过（陪跑 14:40 在 `07ed8f1` 上跑）；判断题 J1–J3 都在主 session 里答，没有起 subagent（11-20 裁定的「另一双眼睛进 subagent」只管 owner 要第二意见时，flow 还没按它改）；试点清单第 4 条（内置浏览器，这次全程用 Chrome）和第 10 条（plan mode 里 subagent 会不会写东西，这次没按清单的办法测，只是没看到写）都没测，留在清单上；PR 待「确认合并」
- 2026-11-21-sync-flow-templates（飞猫，同步 `CLAUDE.md`、`REVIEW.md`、`.claude/flow.json` 三份模板副本）· 小改动（owner 点名）· Sonnet 5.5 · Fable 的建议：无 · 问答：小改动没有 · verifier（Opus）有结果的 3 轮，Important 1、1、0，另有 2 次没查就返回；两条 Important 都不是这个改动的毛病，是 flow 的：第 1 轮是固定检查的措辞和档位规则相反（动了三个文件就判 Important），第 2 轮是它同步到的模板改动在本仓还没提交、而当时的标记只有日期分不出版本 · code-reviewer 报 1 条措辞建议，没改（模板原文）· skill 漏选或错选：无 · 改动的产品文件 2 个（`REVIEW.md`、`.claude/flow.json`），另有 `CLAUDE.md` · owner 点击 2 次；中途被叫到 3 次（两条 Important 各一次、verifier 空返回一次），每次都回到改 flow 的 session 处理 · 这个小改动带出本仓四处修改：小改动检查的措辞、模板标记带短哈希、subagent 的简报改成一句固定的话、合并提示的标签重复；「To do」没变（27 行）；合并提示十行以内、没有折叠
