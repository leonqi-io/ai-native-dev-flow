# ai-native-dev-flow

我们的开发流程 v3：规则文档，加一个把它落到实处的 Claude Code 插件 `flow`。面向多个项目，只用云端订阅。私有仓库。

## 里面有什么

| 位置 | 内容 |
|---|---|
| `docs/flow.md` | 规则：总则、立项、六个阶段；每章分「v3 试行的做法」和「只写不启用」 |
| `docs/skills.md` | skill 清单兼说明书，含测试通过的说法 |
| `docs/hooks-and-scripts.md` | 钩子和脚本清单 |
| `docs/measures.md` | 试点期间手工数的几项 |
| `docs/decisions.md` | 裁定索引 |
| `docs/pilot.md` | 试点清单，只放没做的条目 |
| `docs/study/` | 学习材料的 Markdown 快照（单向导出）：复习材料已在；课堂问答笔记已在 |
| `plugin/` | 插件：`skills/`、`agents/`、`hooks/`、`scripts/`、`templates/`、`reference/`、`evals/` |
| `tools/` | `selftest.sh`（脚本和钩子的自测）、`skill_list.py`（生成清单里的一列） |

## 在本机加载插件

```bash
claude --plugin-dir /path/to/ai-native-dev-flow/plugin
```

云端 session 和 Cowork 能不能从私有仓库加载：未核实，见 `docs/pilot.md`。

需要：Python 3.9 以上、Git。开 PR 的项目还需要 GitHub CLI（`gh`，已登录）。插件 eval 需要 Claude Code v2.1.269 以上。

## 一个项目怎么开始用

1. 在那个项目里说「给这个项目立项」（或 `/flow:setup-project`）。它会写三份项目级文件和 `.claude/flow.json`。
2. 读完它列出的文件清单，在对话里单独发一句「接受立项」，这些文件就进了 `main`。之后每个批准点都是一句话，见 `docs/skills.md`。
3. 之后每个改动从 intent 开始（「我想加一个功能：……」），小改动说「这个按小改动处理：……」。不记得到哪一步了就说「继续」。

仓库里没有 `.claude/flow.json` 时，插件的钩子什么都不做，所以插件可以在用户级启用。

## 改了这个仓库之后

```bash
bash tools/selftest.sh                                         # 改了脚本或钩子
claude plugin validate plugin                                  # 改了插件的任何文件
claude plugin eval plugin --case pick-<名字> --ablation none    # 改了某个 skill 的 description
python3 tools/skill_list.py                                    # 跑完 eval 之后
```
