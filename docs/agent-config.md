# Agent 静态配置管理

本仓库维护 Akira 的自定义 Skill、跨项目静态 Agent 规则和机械 Guard。`~/.agents` 只是运行时入口，不是第二份源码仓库。

本仓库**不负责项目上下文、动态上下文或 Memory 管理**：项目知识继续按 Matt flow 使用项目内 `CONTEXT.md`、ADR 等文件维护；未来动态上下文与 Memory 统一交给 `contextd`。

## 分层

```text
akira-lattice/
├── core/
│   ├── AGENTS.md            # 短小、稳定、跨项目的默认规则与路由
│   └── references/          # 少量低频工具事实与边界
├── scripts/
│   ├── install.py           # 跨平台部署运行时入口
│   ├── guard.py             # 统一机械检查与命令入口
│   └── upstream.py          # fork/upstream Git 状态机实现
├── skills/
│   ├── akira/               # Git submodule：Akira-TL/skills，自研 Skills + 用户文档
│   └── matt/                # Git submodule：Akira-TL/matt-skills，Matt fork
├── docs/                    # 仅保存 Lattice 基础设施与配置说明
└── .agents/adr/             # 本仓库的长期架构决策
```

遵循以下边界：

- **Core** 保留短小、稳定、跨项目且频繁使用的个人默认，例如 Git 语义、Python/前端默认、Documentation、Run & Debug、模型选择和工具路由。Git 交互节奏也在 Core 中明确：收到用户新的开发回复时先判断上一轮原子修改是否应提交，再计划本轮开发、实现、做最低限度语法检查、展示全部本地分支/worktree，并按需给出可选构建或检查说明。不要为了追求极短而把几行规则拆成额外读取。
- **Reference** 只放低频且有独立阅读价值的事实、边界或长说明。当前典型例子是 DevSpace/worktree 语义，以及 Matt skills fork/upstream 的维护边界。
- **Skill** 保存大型规则、检查清单和多步骤过程；代码项目先通过 `ask-matt` 决定应进入的 Matt flow。
- **Guard** 承担确定性、可机械判断的约束。Prompt 不重复维护可以由程序可靠验证的细节。
- **Project context** 由 Matt flow 的 `CONTEXT.md`、ADR 和相关项目文档维护，不由本仓库复制。
- **Dynamic context / Memory** 不属于本仓库，未来由 `contextd` 管理。
- **Runtime state** 由对应软件自己管理，例如 `~/.agents/skills/`、`.skill-lock.json`、MCP、插件、缓存和会话状态。

核心原则：**Prompt 只负责无法机械执行的判断；能够按需读取的不要常驻；能够机器验证的不要只写 Prompt；能够从项目上下文获得的项目知识不要复制成全局规则。**

## 运行时拓扑

```text
~/Projects/akira-skills/core/AGENTS.md
          ├──→ ~/.agents/AGENTS.md
          ├──→ ~/.codex/AGENTS.md
          ├──→ ~/.claude/CLAUDE.md
          └──→ ~/.config/opencode/AGENTS.md
```

所有入口都使用对应 Agent 原生识别的系统提示词文件名，并**直接软链接**到 `core/AGENTS.md`，不再通过 `~/.agents/AGENTS.md` 二次转发，也不使用只负责提示“继续读取另一个文件”的跳板 Prompt。这样既保持单一 canonical source，也避免 Agent 为加载同一份全局规则再执行额外文件读取。

`~/.agents/AGENTS.md` 仍作为通用运行时入口；`~/.agents/references` 指向 `core/references/`，`~/.agents/scripts` 指向仓库根 `scripts/`。`~/.agents/skills/` 与 `.skill-lock.json` 始终由 skills CLI 管理。

## Guard

统一机械检查入口：

```bash
uv run ~/.agents/scripts/guard.py <command>
```

当前命令：

```text
config        检查静态配置部署、链接和 Core 依赖的运行时 Skill
architecture  检查代码文件与目录规模
skills        检查 skills/akira 子模块中的 Skill 结构和文档映射
commit        验证提交格式、暂存架构后执行 git commit
upstream matt 同步 Matt fork 的 upstream；显式 --push 时发布 fork 并提交 submodule pointer
check         运行当前项目适用的组合检查，并输出所有本地分支与 worktree 概览
```

`commit` 不判断 diff ownership。Agent 必须先检查 diff，再用 `git add -- <paths...>` 只暂存当前原子修改；正式提交统一交给 Guard，日常不直接执行 `git commit`。架构阈值默认阻止新引入或加重的规模问题；确有合理理由时可在语义审查后显式使用 `--allow-architecture-warnings`。`config` 还会检查 `skills/matt` 是否作为 Git submodule 指向我们的 `Akira-TL/matt-skills` fork，以及其 `origin`/`upstream` 边界。`upstream matt` 的具体安全流程记录在 `core/references/matt-skills.md`。DevSpace 对 Git/MCP 宿主能力的边界记录在 `core/references/devspace.md`。

Guard 是全局入口，不要求每个项目安装全局 Git hook，因此不会与 Husky、pre-commit 或项目自有 Git hooks 抢占所有权。

## 安装

部署或修复运行时软链接：

```bash
uv run ~/Projects/akira-skills/scripts/install.py
```

迁移旧结构时，在确认新文件已经存在后可额外执行：

```bash
uv run ~/Projects/akira-skills/scripts/install.py --cleanup-legacy
```

该参数会在完成运行时部署后删除仓库中旧的 `context/` 迁移目录。

安装器替换已有运行时文件或目录前，会把原内容集中移动到仓库的 `backup/`。该目录按用户 Home 的相对路径镜像，例如 `~/.claude/CLAUDE.md` 的备份位于 `backup/.claude/CLAUDE.md.backup.<timestamp>`，`~/.agents/references` 的备份位于 `backup/.agents/references.backup.<timestamp>`。`backup/` 只保存本机恢复材料，整个目录由 Git 忽略；不在各 Agent 配置目录旁边散落备份。安装器也会收拢旧版本安装器在这些受管路径旁产生的 `.backup.*` / `.bak.*` 文件，但不会移动 Claude、Hermes 等软件自己维护的备份目录。

安装器不会直接写入 `~/.agents/skills/` 或 `.skill-lock.json`，而是统一调用 skills CLI，因此运行时状态所有权仍属于 skills CLI。Lattice 自有 Skill 从本地 `skills/akira` submodule 安装，其 GitHub `origin` 为 `Akira-TL/skills`，对应用户文档也随 Skill 保存在该子模块的 `docs/`；Matt 派生 Skill 从 `skills/matt` 全量安装，其 GitHub `origin` 为我们的 fork `Akira-TL/matt-skills`，Matt 原仓库只作为内部 `upstream`。这样两类 Skill 都由独立 Git 历史维护，而 Lattice 只锁定各自 submodule commit。Matt submodule 的同步边界记录在 `core/references/matt-skills.md`。

## 维护原则

新增规则时按以下顺序判断：

1. 短小、稳定、跨项目且频繁需要：直接放 `core/AGENTS.md`。
2. 大型规则、多步骤执行方法：做成 Skill。
3. 可以确定性判断：实现到 `scripts/guard.py`，Core 只保留必要的调用语义。
4. 低频工具事实或边界：放 `core/references/`。
5. 项目需求、领域知识、设计决策：交给 Matt flow 的项目上下文。
6. 动态上下文或 Memory：不在这里实现，交给 `contextd`。
7. 软件生成、安装或更新的状态：留给对应软件管理。

同一规则只保留一个 canonical source。Agent 侧目录只做投射，不维护第二份正文。
