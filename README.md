# Akira Lattice

Akira 的个人 Agent 基础设施仓库。这里维护跨项目长期生效的 Core、Guard、部署与运行时边界，并通过独立 Git submodule 管理自研 Skills 与 Matt skills fork；本地 Agent 目录只作为运行时入口，不再维护第二份正文。

仓库保持单一 canonical source：短小稳定规则常驻 Core，大型流程进入 Skill，低频事实进入 Reference，可机械判断的约束进入 Python Guard。项目知识由 Matt flow 管理，动态上下文与 Memory 不在本仓库处理。

## Repository layout

```text
akira-lattice/
├── core/                   # 个人全局静态 Agent 配置 canonical source
│   ├── AGENTS.md           # 每次会话加载的 Core
│   └── references/         # 低频事实与工具边界
├── scripts/                # Python Guard 与运行时安装
├── skills/
│   ├── akira/              # submodule → Akira-TL/skills.git，自研 Skills
│   └── matt/               # submodule → Akira-TL/matt-skills.git
├── docs/                   # Lattice 基础设施与配置说明
├── .agents/adr/            # 影响仓库长期维护的架构决策
├── AGENTS.md               # Agent 在本仓库中的维护规则
├── CONTEXT.md              # 仓库术语与边界
└── CHANGELOG.md            # 面向使用者的变更记录
```

## Global static configuration

`core/AGENTS.md` 是全局提示词唯一源码。统一安装或更新入口：

```bash
./install.sh
```

该入口只负责安装或更新本项目拥有的运行时内容：将 `~/.agents/AGENTS.md` 以及 Claude 的 `CLAUDE.md`、Codex/OpenCode 的 `AGENTS.md` 等原生入口**直接软链接**到当前源码，并通过 `npx skills` 安装或更新 `skills/akira` 与 `skills/matt` 当前提供的 Skill。安装过程中不会清理旧 Skill、迁移历史备份或修改 Matt remote；需要替换的同名非项目运行时文件会先备份到 Git 忽略的 `backup/`。`~/.agents/skills/` 与 `.skill-lock.json` 继续由 skills CLI 管理。

统一卸载入口：

```bash
./uninstall.sh
```

它只移除仍明确指向本仓库的运行时软链接，以及最近一次 `./install.sh` 记录且运行时内容仍与该安装记录一致的 Skill；不会按当前仓库目录猜测卸载对象，也不会清理 `backup/`、Agent 配置目录或其他软件状态。使用统一 Python Guard 检查配置：

```bash
uv run scripts/guard.py config
```

日常项目也可直接调用 `uv run ~/.agents/scripts/guard.py architecture`、`commit` 或 `check`，无需为每个项目单独安装 Git hook。完整设计见 `docs/agent-config.md`。

## Current skills

自研 Skill 的正文、README 与详细用户文档都由 `skills/akira` 子模块中的 `Akira-TL/skills` 独立维护；Lattice 只锁定其 commit，不保留第二份 Skill 文档。当前主要能力包括 `devspace-orchestration`、`general-word-document-generation` 和 `browser-access`。

Matt 派生 Skill 则由 `skills/matt` 对应的 `Akira-TL/matt-skills` fork 独立维护。

## 单独安装 Skill

正常情况下使用根目录 `./install.sh` 统一安装或更新全部项目运行时内容。只有需要单独安装某个 Skill 时，才直接使用 `npx skills`。例如安装通用浏览器访问 Skill 到 Codex：

```bash
npx skills add ./skills/akira --skill browser-access --agent codex -g -y
```

同时安装到多个 Agent：

```bash
npx skills add ./skills/akira \
  --skill browser-access \
  -g \
  -a codex \
  -a claude-code \
  -a opencode \
  -a hermes-agent \
  -y
```

安装到 CLI 检测到的所有 Agent：

```bash
npx skills add ./skills/akira --skill browser-access --agent '*' -g -y
```

查看自研仓库中可安装的 Skill：

```bash
npx skills add ./skills/akira --list
```

也可以直接从 GitHub 安装：`npx skills add Akira-TL/skills ...`。Matt 派生 Skills 则来自 `skills/matt`，其 GitHub origin 为 `Akira-TL/matt-skills`。

同步 Matt 上游时使用受控入口：

```bash
uv run scripts/guard.py upstream matt
# 确认结果后，如需发布 fork 并提交新的 submodule pointer：
uv run scripts/guard.py upstream matt --push
```

## Status

仓库当前处于初始化阶段。许可证、自动校验、Changesets 和正式远程发布仍将在需求明确后分别决策；本地 `npx skills` 安装已经可用。
