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
