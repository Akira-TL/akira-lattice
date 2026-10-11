# GitHub 议题跟踪约定

## 仓库与操作入口

本仓库的需求、规格和规划决策使用 `Akira-TL/akira-lattice` 的 GitHub Issues，统一通过 `gh` 操作。即使当前目录位于子仓库，本约定的命令也必须显式指定 `--repo Akira-TL/akira-lattice`，避免误写其他仓库。

集中跟踪不改变源码归属：实现仍在所属子仓库完成、验证并提交，再由 Lattice 更新固定版本。具体归属遵循根 `AGENTS.md`。

- 创建议题：`gh issue create --repo Akira-TL/akira-lattice --title '<标题>' --body-file <正文文件>`。
- 读取正文与讨论：`gh issue view <编号> --repo Akira-TL/akira-lattice --comments`；需要结构化内容时使用 `--json number,title,body,labels,comments,assignees,state`。
- 查询议题：`gh issue list --repo Akira-TL/akira-lattice --state open --limit 100 --json number,title,body,labels,assignees`，按所需标签、状态缩小查询范围。
- 添加讨论：`gh issue comment <编号> --repo Akira-TL/akira-lattice --body-file <正文文件>`。
- 更新正文：`gh issue edit <编号> --repo Akira-TL/akira-lattice --body-file <正文文件>`。
- 添加或移除标签：`gh issue edit <编号> --repo Akira-TL/akira-lattice --add-label '<标签>'` 或 `--remove-label '<标签>'`。
- 列出标签：`gh label list --repo Akira-TL/akira-lattice --limit 1000 --json name,color,description`。
- 创建缺失标签：`gh label create '<标签>' --repo Akira-TL/akira-lattice --description '<说明>' --color '<颜色>'`。先查询，仅创建缺失项，不使用 `--force`，不修改已有标签的颜色或说明。
- 关闭议题：`gh issue close <编号> --repo Akira-TL/akira-lattice`；完成依据先以讨论记录。

多行正文先写入文件并使用 `--body-file`，不在命令中拼接多行文本。工作流角色的具体标签从 `docs/agents/triage-labels.md` 读取，不在下游技能中另建映射。

## 拉取请求入口

**拉取请求作为需求入口：否。** `triage` 默认只处理议题。日后明确改为“是”时，拉取请求采用相同角色映射，通过 `gh pr` 读取、评论、添加标签和关闭；外部作者筛选使用 GitHub API 的 `author_association`，不把仓库所有者、成员或协作者提交当作外部请求。

GitHub 议题与拉取请求共享编号空间。来源不明的编号必须先确认对象类型；不能仅凭编号推断它是议题。

技能要求“发布到议题跟踪系统”时创建 GitHub 议题；要求“读取相关工作项”时读取其正文、标签和讨论。

## 工作项、依赖与领取

使用原生能力前实际检查 `gh issue create --help`、`gh issue edit --help`，并通过 `gh issue list --repo Akira-TL/akira-lattice --limit 1 --json number,blockedBy` 做只读字段探测。本次配置已验证当前 CLI 支持 `--parent`、`--add-sub-issue`、`--add-blocked-by` 和 `blockedBy`；后续运行环境仍需重新探测，不能只根据版本号推断能力。

- **阻塞关系**：优先使用 GitHub 原生议题依赖。当前 CLI 可用 `gh issue edit <被阻塞编号> --repo Akira-TL/akira-lattice --add-blocked-by <前置编号>`；读取时查询 `blockedBy`。缺少 CLI 便利参数时，通过 `gh api` 读取前置议题的数据库 `id`，向 `repos/Akira-TL/akira-lattice/issues/<被阻塞编号>/dependencies/blocked_by` 发送 POST，参数 `issue_id=<前置数据库ID>`；读取使用同一端点的 GET。只有仓库或账号的依赖 API 本身不可用时，才在正文使用 `Blocked by: #<编号>, #<编号>` 作为替代约定。
- **当前可处理的工作项**：查询相关未关闭工作项，排除存在未解决前置项或有效领取记录的项目，按所属工作流顺序选择。优先用 `blockedBy`，其次使用上述 REST 端点，最后才解析正文替代约定。
- **领取**：独立 GitHub 身份可用 `gh issue edit <编号> --repo Akira-TL/akira-lattice --add-assignee @me`。多个 Agent 共用同一 GitHub 身份时，指派仅用于展示，不能作为互斥锁；没有已加载的可靠协调协议时串行处理。
- **完成实现工作项**：重新读取验收条件，对照已提交实现、验证和复核依据，只勾选确实满足的条件；添加完成依据，移除映射到 `ready-for-agent` 的标签，然后关闭。存在未满足条件时保持打开并说明缺口，不顺带关闭父规格或父议题。

## Wayfinder 规划操作

规划地图使用映射到 `wayfinder:map` 的标签；子决策议题使用 `wayfinder:research`、`wayfinder:prototype`、`wayfinder:grilling` 或 `wayfinder:task` 对应标签。

- **地图**：创建单一权威议题，正文包含目的地、工作约定、已决事项索引、尚未明确的问题与范围之外的事项。已决事项只保存一句概述及其决策议题链接；详细结论只保存在对应决策议题的解决讨论中。未关闭子议题通过查询取得，不在地图正文重复维护清单。
- **子决策议题**：先创建议题，再关联父地图。当前 CLI 支持 `gh issue edit <子编号> --repo Akira-TL/akira-lattice --parent <地图编号>`。缺少 CLI 参数时，向 `repos/Akira-TL/akira-lattice/issues/<地图编号>/sub_issues` 发送 POST，参数 `sub_issue_id=<子议题数据库ID>`。只有子议题 API 本身不可用时，才在地图任务列表链接子议题，并在子议题正文顶部写 `Part of #<地图编号>`。
- **依赖**：所有子议题创建后再添加原生阻塞关系，避免尚无编号时写入虚构引用。
- **领取与推进**：处理前先领取；本次会话按串行规则推进，不以共享账号指派模拟多个 Agent 的互斥。
- **解决决策**：把答案写为子议题的解决讨论，关闭子议题，再在地图“已决事项”中追加一句概述与命名链接。范围之外的事项关闭后归入地图的范围之外区域，不混入已决事项。
- **用户可见引用**：以议题标题作为链接名称，不以裸编号代替名称。

规划、讨论、研究与实现边界由各技能正文规定，本文件只定义跟踪系统操作。
