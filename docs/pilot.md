# 试点清单

只放还没做的条目。做完一条删一条，结果写进 `docs/decisions.md`。

试点项目：flightcat.ca 改版。试点不从写这个仓库的 session 开始。

## 试点开始之前

- [ ] **飞猫的立项 session。** 对着今天的实际情况复查需求和设计，重新讨论有没有更好的部署方式，然后写 mission.md、roadmap.md、tech-stack.md。目前的状态在 `flightcat.ca-redesign/flightcat.ca_V3/dev/ARCHITECTURE.md`。
- [ ] **自测。** `bash tools/selftest.sh` 在本机通过。
- [ ] **插件格式检查。** `claude plugin validate plugin`。
- [ ] **把用户级的两段贴进 `~/.claude/CLAUDE.md`。** `plugin/templates/user/` 下的规范段和模型表。

## 试点第一天要实测的四条（都是「未核实」）

| # | 要测什么 | 怎么测 | 退路 |
|---|---|---|---|
| 1 | 云端 session 或 Cowork 能不能从私有仓库加载这个插件 | 在云端 session 里装插件，看 `/flow:continue` 在不在 | 本地用 `claude --plugin-dir <本仓>/plugin`；云端把插件复制进项目。另外要留意：skill 的 `when_to_use` 不在 Agent Skills 规范的字段里，按 claude.ai 上传的方式打包会报错，那时把它并进 `description` |
| 2 | `ask` 在自动批准模式下还弹不弹提示，提示里能显示多少字 | 在各个权限模式下各跑一次小改动的第一次点击，看提示出不出、intent 全文显不显示 | 钩子改成拒绝，原因里给一行可粘贴的命令，由 owner 自己运行。小改动的两次点击、测试文件的放行、roadmap 的删除和移动都依赖这一条 |
| 3 | 一个插件 eval 用例占多少额度 | `claude plugin eval plugin --case pick-continue --runs 1 --ablation none`，跑前跑后各看一次用量页 | 占得多就减少用例或减少运行次数 |
| 4 | 内置浏览器的三项：每个 session 一个还是共用；在后台会不会被限速；能不能上传文件 | 飞猫第一个 UI 改动之前，在桌面端开两个 session 各打开本地预览试 | 测完之前按最保守的读法：浏览器一次只给一个 session 用。结果只改一条规则：并行的 UI 改动要不要排队用浏览器 |

第 3 条测完、额度可以接受之后，整套跑一次并生成清单：

```bash
claude plugin eval plugin --ablation none
python3 tools/skill_list.py
```

## 试点期间

- 每个改动收尾时在 `docs/measures.md` 末尾记一行。
- 流程本身的问题当场记在下面一节，一行一条；修掉并回填规则文档之后删掉那一行。

## 试点中发现、还没处理的流程问题

（空）
