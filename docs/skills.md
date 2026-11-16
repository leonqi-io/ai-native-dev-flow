# skill 清单

这份清单兼作说明书：忘了怎么说，就来这里查。两种启动方式：

- **平常话**：照下面「测试通过的说法」那样说。那一列是脚本从测试用例生成的，只有用例存在并且通过，说法才会出现在里面。
- **保底**：在消息开头打 `/flow:<名字>`，一定会启动那个 skill。名字后面跟的内容当作普通指令读。

## 每个 skill 做什么

| skill | 阶段 | 什么时候用 | 做什么 | 结束时停在哪 |
|---|---|---|---|---|
| continue | 入口 | 想接着做，不确定到哪一步了 | 跑状态脚本，说现在在哪个阶段，加载那个阶段的 skill | 接到对应的 skill |
| setup-project | 立项 | 一个仓库第一次用这套流程 | 和 owner 写 mission、tech-stack、roadmap，以及项目的 CLAUDE.md、REVIEW.md、`.claude/flow.json` | 给 owner 一行提交命令 |
| intent | Plan | 想做一个改动，不是小改动 | 定档位，建文件夹和分支，起草 intent.md，跑问答 | 给 owner 一行提交命令（intent 接受） |
| spec | Design | intent 已接受 | researcher 查事实；写 spec.md 和 validation.md；跑问答；试跑每条命令；R-ID 覆盖检查 | 给 owner 一行提交命令（spec 接受） |
| plan | Build | spec 已接受 | 在 plan mode 里写 plan.md；高风险档提示另开 session 二读 | 给 owner 一行提交命令（plan 批准） |
| implement | Build、Test | plan 已批准；或评审意见回来了 | 红测试并提交 `red-run.txt`；实现到绿；跑 code-reviewer 和 verifier；贴出绿的输出 | 提示另开 session 评审 |
| small-change | 全程（简化） | 错字、文案、配置值、依赖升级、单处修复 | 起草短 intent；第一次点击；写 validation、改、验证、评审，一路不停 | 第二次点击（合并提示） |
| review | Deploy | 分支可以评审了；修完要复核；高风险档 plan 要二读 | 新 session 读 REVIEW.md，三遍加固定检查，出报告，在 Approval log 里记一行 | 有 Important 就回实现的 session；没有就进验收 |
| validate | Deploy | 评审过了，owner 要亲自验收 | 把 §0 一步一步递给 owner，每步一个命令块加预期结果，记录结果 | 全过就进收尾 |
| close | Deploy | 验收过了 | 处理遗留项，更新 roadmap 状态行，跑收尾检查 | 把合并交给 owner（他的一行命令，或 PR） |
| todo | Maintain | 发现一个不属于当前改动的问题；或要过一遍待办 | 往 roadmap 的「To do」加一行；逐行分流（现在修、排期、不做） | 说还剩几行未决 |

没有一个 skill 设成只能由人启动。会移动 `main` 的几处都由固定脚本加确认提示把关。

## 测试通过的说法

<!-- generated:phrasings:start -->
| skill | 保底启动 | 测试通过的说法 | 用例 | 最近一次结果 |
|---|---|---|---|---|
| close | `/flow:close` | （还没有通过的记录） | `plugin/evals/pick-close/` | 未跑 |
| continue | `/flow:continue` | （还没有通过的记录） | `plugin/evals/pick-continue/` | 未跑 |
| implement | `/flow:implement` | （还没有通过的记录） | `plugin/evals/pick-implement/` | 未跑 |
| intent | `/flow:intent` | （还没有通过的记录） | `plugin/evals/pick-intent/` | 未跑 |
| plan | `/flow:plan` | （还没有通过的记录） | `plugin/evals/pick-plan/` | 未跑 |
| review | `/flow:review` | （还没有通过的记录） | `plugin/evals/pick-review/` | 未跑 |
| setup-project | `/flow:setup-project` | （还没有通过的记录） | `plugin/evals/pick-setup-project/` | 未跑 |
| small-change | `/flow:small-change` | （还没有通过的记录） | `plugin/evals/pick-small-change/` | 未跑 |
| spec | `/flow:spec` | （还没有通过的记录） | `plugin/evals/pick-spec/` | 未跑 |
| todo | `/flow:todo` | （还没有通过的记录） | `plugin/evals/pick-todo/` | 未跑 |
| validate | `/flow:validate` | （还没有通过的记录） | `plugin/evals/pick-validate/` | 未跑 |

生成依据：还没有跑过插件测试。
<!-- generated:phrasings:end -->

每个 skill 只测一种说法，因为这套流程主要是我们自己用，忘了可以来查，查不到还有 `/flow:<名字>`。

## 一种说法测不到的两种情况

- 一句本该给相邻 skill 的话，被这个 skill 接走了。
- 由 session 而不是由人触发的 skill：入口 skill 加载某个阶段的 skill；某个 session 说「按小改动处理」。

这两种情况靠试点期间手工计数（见 `docs/measures.md`）。数出真实的漏选或错选，再补用例，不提前补。

## 用例的已知限制

- 每次测试运行从空目录开始，没有人回答问题，不授权就没有 Write 和 Bash。所以用例只检查「选对了 skill」，不检查产出文件的形状。要检查产出文件，得给用例加准备脚本并授权工具，等试点第一天量过一个用例占多少额度之后再决定加不加。
- 测试运行里只加载这个插件，不加载用户设置、项目的 CLAUDE.md 和项目钩子。所以插件 eval 测不了某个项目的配置，那是项目配置 eval 的事。

## 怎么跑、怎么更新这份清单

在本仓根目录、自己的终端里（用订阅登录，不配 API key）：

```bash
# 改了某个 skill 的 description 之后，跑它的用例
claude plugin eval plugin --case pick-<名字> --ablation none

# 试点开始前，整套跑一次
claude plugin eval plugin --ablation none

# 跑完后重新生成上面那张表
python3 tools/skill_list.py
```

没选中的话，改那个 skill 的 `description` 和 `when_to_use`，再跑，不改回命令。
