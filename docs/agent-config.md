# Agent 静态配置管理

本仓库维护 Akira 的自定义 Skill、跨项目静态 Agent 规则和机械 Guard。`~/.agents` 只是运行时入口，不是第二份源码仓库。

本仓库**不负责项目上下文、动态上下文或 Memory 管理**：项目知识继续按 Matt flow 使用项目内 `CONTEXT.md`、ADR 等文件维护；未来动态上下文与 Memory 统一交给 `contextd`。

## 分层

```text
akira-skills/
├── core/
│   ├── AGENTS.md            # 短小、稳定、跨项目的默认规则与路由
│   └── references/          # 少量低频工具事实与边界
├── scripts/
│   ├── install.py           # 跨平台部署运行时入口
│   └── guard.py             # 确定性机械检查
├── skills/                  # 大型规则、多步骤流程与可复用能力
└── .agents/adr/             # 本仓库的长期架构决策
```

遵循以下边界：

- **Core** 保留短小、稳定、跨项目且频繁使用的个人默认，例如 Git 语义、Python/前端默认、Documentation、Run & Debug、模型选择和工具路由。不要为了追求极短而把几行规则拆成额外读取。
- **Reference** 只放低频且有独立阅读价值的事实、边界或长说明。当前典型例子是 DevSpace/worktree 语义。
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
skills        检查 akira-skills 的 Skill 结构和文档映射
commit        验证提交格式、暂存架构后执行 git commit
check         运行当前项目适用的组合检查，并输出所有本地分支与 worktree 概览
```

`commit` 不判断 diff ownership。Agent 必须先检查 diff 并选择性暂存当前原子修改，再交给 Guard 做机械校验和提交。架构阈值默认阻止新引入或加重的规模问题；确有合理理由时可在语义审查后显式使用 `--allow-architecture-warnings`。

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

安装器不会直接管理 `~/.agents/skills/`、`.skill-lock.json`。对于仓库自身且被 Core 直接引用的 Skill，它只调用 `npx skills` 完成安装，因此状态所有权仍属于 skills CLI。外部 Skill（例如 `ask-matt`）按其自身来源安装，Guard 会检查这些运行时依赖是否存在。

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
