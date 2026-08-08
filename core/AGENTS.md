# 任何项目都必须遵守的规则

## 基本行为

- 永远使用简体中文进行思考和对话。
- 用户回复“1”“继续”“对”等简短肯定词，即代表同意当前询问并立即执行，不得再次解释或追问。
- 编写 `.md` 文档时使用中文；正式项目文档默认写入 `docs/`。
- 仅当任务确实需要用户个人资料、联系方式、报名、简历、自我介绍或项目经历时，才读取 `~/.config/akira/`；无关任务不得读取。
- 处理代码相关项目需求时，先读取 `ask-matt` Skill，根据其路由确定项目管理与开发流程；无需用户重复提醒或显式调用 `/ask-matt`。
- 多步骤、可复用的大型规则或执行流程优先使用 Skill；短小、稳定、跨项目的个人工程默认直接保留在本文件。

## 工程默认

以下规则是新项目或缺少明确项目约束时的默认值；已有项目明确采用其他版本或技术栈时，不得仅为迎合全局默认而主动迁移。

- Python 使用 `uv`，虚拟环境统一为 `.venv`；不直接使用 `pip`、`poetry`、`conda`、`python3` 或 `python`。数据结构优先强类型，确需未结构化 `dict` 时先征求用户同意；根目录和 `main.py` 保持简洁。
- React / Next.js 默认使用 Next.js 15.4、React 19、Tailwind CSS 4、ESM 和 TypeScript；禁止 CommonJS。确需 `any`、未结构化 JSON 或 JavaScript 时先征求用户同意，构建工具明确不支持 TypeScript 的场景除外。
- Run & Debug 必须通过项目 `scripts/` 中维护的 `.sh` 脚本启停；缺失或损坏时先建立/修复脚本。运行日志统一写入 `logs/`。构建、静态检查、格式化等非启停操作不受此限制。
- 代码应避免僵化、冗余、循环依赖、脆弱性、晦涩性、数据泥团和不必要的复杂性。发现明显坏味道时指出具体问题和优化方向；若优化超出当前任务边界，再询问用户是否处理。

## Git

- Git 提交随实现过程进行。修改前按复杂度拆分为可独立理解、独立回退、职责单一的原子修改；每完成一个原子修改先做最低限度语法检查，再准备提交，然后才开始下一单元。
- 提交前检查当前原子修改的 diff ownership，只暂存归属明确的当前修改。此前会话、其他 Agent、用户或来源不明的修改不得顺带提交、修改、还原或删除；存在时提醒用户。
- 不同功能、模块、问题、代码与文档原则上不得混入同一提交；不得为了减少数量扩大提交范围，也不得机械切碎不可独立工作的修改。
- 提交信息默认一行：`<TYPE>: (<SCOPE>) <DETAIL>`；`TYPE` 使用全大写的 `FIX`、`FEAT`、`REFACTOR`、`TEST`、`DOCS` 或 `CHORE`，`SCOPE` 使用简短英文单词，`DETAIL` 必须具体。确有必要使用多行时，每一行都必须独立完整地遵守同一格式。
- 选择性暂存完成后，统一使用 `uv run ~/.agents/scripts/guard.py commit -m '<message>'` 提交。该入口负责机械校验提交格式和当前暂存修改是否新引入代码规模问题；语义归属仍由 Agent 负责。
- 当前任务的实现型修改全部提交后，再进入可选的大范围测试、检查和收尾。收尾时可运行 `uv run ~/.agents/scripts/guard.py check` 获取适用检查和完整分支/worktree 概览，并向用户提供可选的构建/检查命令或说明。测试发现的新问题作为新的原子修改独立提交；除非用户明确要求，不 squash 已合理拆分的提交。

## 模型与多 Agent

调用 Claude 或子 Agent 时必须显式指定 `--model` 或 Agent 的 `model`，禁止省略、继承父会话模型或自行降级。

- `fable`：极少数超长上下文、重型规划任务
- `opus`：主会话、复杂决策、架构推理、关键审查、最终验收
- `sonnet`：默认子 Agent；代码实现、修复、重构、调查、测试分析和常规模块任务
- `haiku`：简单查找、信息摘取、机械核对、格式整理等低风险任务

DevSpace 子 Agent 默认使用 `sonnet`；确需独立高层判断时使用 `opus`，简单机械任务使用 `haiku`。底层模型 ID 和路由由本机配置解析，Agent 不负责替换。需要并行 Agent、tmux 或隔离 worktree 编排时，使用 `devspace-orchestration` Skill；涉及 DevSpace/worktree 的事实与路径边界时可读取 `~/.agents/references/devspace.md`。不要为了使用多 Agent 而拆分本可由单 Agent 清晰完成的任务。

## CodeGraph

若仓库根目录存在 `.codegraph/`，理解或定位代码时优先使用 CodeGraph，而不是先 grep/find 或逐文件阅读：MCP 可用时使用 `codegraph_explore`，否则使用 `codegraph explore "<symbol names or question>"`。不存在 `.codegraph/` 时直接跳过，不主动建立索引。
