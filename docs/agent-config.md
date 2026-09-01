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
│   ├── install.py           # 安装/更新运行时内容
│   ├── uninstall.py         # 卸载本项目拥有的运行时内容
│   ├── guard.py             # 统一机械检查与命令入口
│   └── upstream.py          # fork/upstream Git 状态机实现
├── skills/
│   ├── akira/               # Git submodule：Akira-TL/skills，自研 Skills + 用户文档
│   └── matt/                # Git submodule：Akira-TL/matt-skills，Matt fork
├── docs/                    # 仅保存 Lattice 基础设施与配置说明
└── .agents/adr/             # 本仓库的长期架构决策
```

遵循以下边界：

- **Core** 保留短小、稳定、跨项目且频繁使用的个人默认，例如 Git 语义、Python/前端默认、Documentation、Run & Debug、模型选择和工具路由。Git 交互节奏也在 Core 中明确：按修改目的逐阶段实现并立即提交，用户明确否定最近实现时先安全回退再重做；每次正式提交由 Guard 自动执行 staged 最低语法检查，只有大型、关键或高风险修改才按实际失败模式追加更重的验证。不要为了追求极短而把几行规则拆成额外读取。
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
commit        验证提交格式、staged 最低语法与暂存架构后执行 git commit
upstream matt 同步 Matt fork 的 upstream；显式 --push 时发布 fork 并提交 submodule pointer
check         运行当前项目适用的组合检查，并输出所有本地分支与 worktree 概览
```

`commit` 不判断 diff ownership。Agent 必须先检查 diff，再用 `git add -- <paths...>` 只暂存当前原子修改；正式提交统一交给 Guard，日常不直接执行 `git commit`。Guard 的最低语法检查读取 Git index 中真正准备提交的版本，目前直接覆盖 Python、JSON、TOML，并在本机相应解释器可用时检查 Shell、`.mjs` 与 `.cjs`；它不会把普通提交扩张成全项目 lint、typecheck、build 或 test suite。大型、关键或高风险修改仍根据实际失败模式追加 targeted test、类型检查、构建、schema/migration validator 或项目专属验证。架构阈值默认阻止新引入或加重的规模问题；确有合理理由时可在语义审查后显式使用 `--allow-architecture-warnings`。`config` 还会检查 `akira-guard`、`ask-matt` 与 `devspace-orchestration` 等 Core 依赖的运行时 Skill，并核验 `skills/matt` 的 fork/upstream 边界。`upstream matt` 的具体安全流程记录在 `core/references/matt-skills.md`。DevSpace 对 Git/MCP 宿主能力的边界记录在 `core/references/devspace.md`。

Guard 是全局入口，不要求每个项目安装全局 Git hook，因此不会与 Husky、pre-commit 或项目自有 Git hooks 抢占所有权。

## 安装与卸载

根目录提供统一安装/更新入口：

```bash
cd ~/Projects/akira-skills
./install.sh
```

该入口只执行当前项目运行时部署：建立或更新全局 Agent 提示词、references、scripts 与说明文档软链接，并通过 skills CLI 全量安装或更新当前 `skills/akira` 与 `skills/matt` 提供的 Skill。它不会清理旧 Skill、迁移历史备份、删除旧目录或修改 Matt remote；版本同步和上游维护继续由各自 Git/Guard 流程负责。

安装器需要替换同名且不属于当前项目的运行时文件时，会先把原内容集中移动到仓库的 `backup/`。该目录按用户 Home 的相对路径镜像，例如 `~/.claude/CLAUDE.md` 的备份位于 `backup/.claude/CLAUDE.md.backup.<timestamp>`。这是避免覆盖用户现有配置的安装安全措施，不会在后续安装中主动整理或清理已有备份。

统一卸载入口：

```bash
./uninstall.sh
```

卸载器只移除两类明确属于本项目的运行时内容：仍直接指向本仓库源码的 Agent 配置软链接，以及最近一次 `./install.sh` 写入安装清单且当前 `SKILL.md` 哈希仍一致的 Skill。没有安装清单时不会猜测 Skill 名称；同名 Skill 在安装后被其他内容替换时也会保留。它不会恢复或清理 `backup/`，不会删除 Agent 配置目录，也不会清理其他 Skill、插件、MCP、缓存或会话状态。

安装和卸载均不会直接维护 `.skill-lock.json`；Skill 的实际安装/移除统一通过 skills CLI 完成，因此该状态继续由 skills CLI 所有。Lattice 自有 Skill 来自本地 `skills/akira` submodule；Matt 派生 Skill 来自 `skills/matt`。Matt submodule 的 fork/upstream 维护边界记录在 `core/references/matt-skills.md`，不属于安装流程。

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
