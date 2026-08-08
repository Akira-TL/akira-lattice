# ADR 0001：统一 Agent 静态配置源码与运行时入口

## Status

Accepted

## Context

个人全局提示词此前直接维护在 `~/.agents`，同时 Claude、Codex、OpenCode 通过硬链接共享同一文件。这会把源码、运行时入口和 `skills` CLI 管理的安装状态混在一个目录中；而 Git 操作也可能替换 tracked 文件 inode，使跨仓库硬链接失效。

成熟配置通常保持一个 canonical source，再通过安装器或链接投射到各 Agent 的实际读取位置；短小稳定规则常驻 Core，大型流程交给 Skill，低频事实放到 Reference，可机械判断的规则交给程序。

## Decision

- `/home/Akira/Projects/akira-skills` 是自定义 Agent 能力与静态配置的唯一版本管理仓库。
- 全局静态配置源码放在 `core/`，其中 `AGENTS.md` 是常驻 Core，`references/` 只保存有独立阅读价值的低频事实和工具边界。
- 确定性规则与部署工具统一放在根 `scripts/`；`scripts/guard.py` 负责机械检查，`scripts/install.py` 负责跨平台部署。Agent Prompt 只保留需要语义判断的规则和 Guard 的调用边界。
- 项目知识继续由 Matt flow 的 `CONTEXT.md`、ADR 等项目文件管理；动态上下文与 Memory 不属于本仓库，未来由 `contextd` 负责。
- `~/.agents` 仅作为运行时 hub，不再初始化 Git；`AGENTS.md`、`references/`、`scripts/` 等自定义内容通过软链接指向仓库源码。
- Claude、Codex、OpenCode 的全局提示词文件通过软链接指向 `~/.agents/AGENTS.md`。
- `~/.agents/skills/`、`.skill-lock.json` 以及未来由 MCP、插件或其他软件生成的状态不纳入该源码部署链路，也不由本仓库直接版本管理。
- 跨 Git 仓库边界使用软链接而不是硬链接，避免 Git checkout/reset 替换 inode 后链接失效。

## Consequences

- 修改仓库中的 `core/AGENTS.md` 会立即反映到各 Agent 的全局提示词入口。
- 克隆或移动仓库后需要重新运行 `uv run scripts/install.py` 恢复运行时链接。
- 工具生成状态与人工维护源码的所有权边界清晰，不再互相污染 Git 历史。
- 多步骤、大型流程继续优先沉淀为 Skill；几行即可表达的稳定工程默认直接留在 Core，避免为了极端缩短 Prompt 反而增加额外读取。
- Guard 为所有项目提供统一机械入口，不要求项目安装全局 Git hook，因此不会抢占 Husky、pre-commit 或项目自有 hooks 的所有权。
