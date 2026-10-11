# 工作流角色与标签映射

本文件将当前已安装的 `to-tickets`、`triage` 和 `wayfinder` 使用的工作流角色映射到主仓 GitHub 标签。角色与标签同名，其他已有标签不受本配置管理。

| 工作流角色 | GitHub 标签 | 使用技能 | 含义 |
| --- | --- | --- | --- |
| `ready-for-agent` | `ready-for-agent` | to-tickets、triage | 需求已明确，可交由 Agent 实现 |
| `bug` | `bug` | triage | 缺陷请求 |
| `enhancement` | `enhancement` | triage | 新增功能或改进请求 |
| `needs-triage` | `needs-triage` | triage | 等待维护者评估 |
| `needs-info` | `needs-info` | triage | 等待请求者补充信息 |
| `ready-for-human` | `ready-for-human` | triage | 需要人工实现或判断 |
| `wontfix` | `wontfix` | triage | 不予处理的请求 |
| `wayfinder:map` | `wayfinder:map` | wayfinder | 规划地图 |
| `wayfinder:research` | `wayfinder:research` | wayfinder | 通过资料调查解决的决策 |
| `wayfinder:prototype` | `wayfinder:prototype` | wayfinder | 通过原型与用户反馈解决的决策 |
| `wayfinder:grilling` | `wayfinder:grilling` | wayfinder | 通过与用户讨论解决的决策 |
| `wayfinder:task` | `wayfinder:task` | wayfinder | 使后续决策能够进行的前置操作 |

下游技能从此表读取实际标签，不自行发明映射。配置时只创建缺失标签，保留已有标签的颜色与说明；新增标签说明使用本表的中文含义。
