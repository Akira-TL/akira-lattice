# Agent 静态配置管理

本仓库维护 Akira 的全局静态 Agent 规则、运行时部署、Lattice 自检和各 Skill 仓的固定开发 revision；跨项目机械 Guard 由 `akira-guard` Skill 维护。`~/.agents` 只是运行时入口，不是第二份源码仓库。

## 分层

```text
akira-lattice/
├── core/
│   ├── AGENTS.md
│   └── references/
├── scripts/
│   ├── install.py
│   ├── uninstall.py
│   └── lattice_check.py
├── skills/
│   ├── akira/               # 通用 Akira Skills + akira Router
│   ├── research/            # 独立 Research suite
│   └── matt/                # Matt fork + Akira engineering extensions
├── docs/
└── .agents/adr/
```

边界：

- **Core**：短小、稳定、跨项目并需要常驻的默认规则。
- **Akira common Skills**：跨领域可复用能力和安装 Router；Productivity、Akira Guard、通用 Agent 编排留在 `skills/akira`。
- **Matt Engineering**：软件工程方法与其 Akira delta 同仓。`ask-akira`、`parallel-coordinator`、`parallel-execution` 属于 `skills/matt`，因为它们直接扩展 Matt 的 Spec/Ticket/implement/TDD/review 流程。
- **Research**：共享 Research Tree、schema、migration、research.sqlite 与科研对象契约，作为独立 `skills/research` 产品仓。
- **Akira Guard**：跨项目 Git 提交、暂存语法、架构与 Skill 结构机械检查，由默认安装的 `akira-guard` Skill 持有。Lattice 根仓只保留自身静态配置与 submodule 拓扑检查。
- **Runtime state**：Skill 运行时状态由 `akira` Router 自带安装器管理：远端 source 位于 `~/.agents/sources/`，机器级注册表位于 `~/.agents/skills/`，manifest 位于 `~/.agents/akira-skills.json`。Lattice 根安装器只有一个 bootstrap 例外：从云端获取 `akira` 安装器并确保 `akira`、`browser-access`、`akira-guard` 三个基础 Skill 已注册。机器级注册表不会自动投影到项目或执行器自己的 Skill 目录；具体执行器的缓存/profile 与项目级 Skill view 仍由对应执行器/项目显式管理。`<project>/.agents/skills/` 是允许的开放 Agent Skills 项目级 view，Agent 可以在项目确实需要时显式建立指向 `~/.agents/skills/<name>` 的软链接；ForgeRelay 不负责把机器级注册表自动兼容成这些项目链接，但项目中已经存在的 `.agents/skills/` 仍可由 ForgeRelay 按项目 Skill 入口正常读取。

## 运行时拓扑

```text
~/Projects/akira-skills/core/AGENTS.md
          ├──→ ~/.agents/AGENTS.md
          ├──→ ~/.codex/AGENTS.md
          ├──→ ~/.claude/CLAUDE.md
          └──→ ~/.config/opencode/AGENTS.md
```

`~/.agents/references` 指向 `core/references/`，`~/.agents/scripts` 指向根 `scripts/`。根 `scripts/` 只提供 Lattice 静态配置部署、基础 Skill bootstrap 与 Lattice 自检；跨项目 Guard 脚本跟随 `akira-guard` Skill 发布，通用 Skill 安装脚本跟随 `akira` Skill 发布。第三方 Skill 仓不作为 Lattice submodule 或运行时 source view，需要时由 `akira` Router 从登记来源发现并安装。

## Skill 安装边界

根目录：

```bash
./install.sh
```

该命令部署 Core、references 与其他静态配置链接，并从远端 `Akira-TL/skills` bootstrap `akira`、`browser-access` 与 `akira-guard` 三个基础 Skill。bootstrap 不使用 Lattice 本地 submodule，而是临时 clone 云端仓库并执行其中的 `akira` 安装器。Lattice pin 住的其他 Skill 仓仍只用于开发、review、provenance 与固定 source revision。

基础 bootstrap 完成后，Skill 生命周期由 `akira` Router 自己负责。Router 按“当前会话 → 机器级注册表 → 远端 source”判断能力缺口；需要新增能力时先说明来源、用途与最小集合并取得用户明确同意，再调用：

```bash
uv run python ~/.agents/skills/akira/scripts/skills.py <command> ...
```

该脚本独立管理 `~/.agents/akira-skills.json`、`~/.agents/sources/` 与 `~/.agents/skills/`。Matt、Research、Word、科研/学术 PPT、`akira-guard`、`agent-orchestration` 与外部专业能力都遵循同一机制。Lattice 根安装器只触发基础 bootstrap，不实现通用 Skill 生命周期；根卸载器与 `lattice_check.py` 不读取或修改这些状态。

## Guard

跨项目统一入口：

```bash
uv run ~/.agents/skills/akira-guard/scripts/guard.py <command>
```

Lattice 自身配置与 submodule 拓扑检查：

```bash
uv run ~/.agents/scripts/lattice_check.py
```

主要命令：

```text
architecture  检查代码与目录规模
skills PATH   检查指定 Skill 仓的结构与稳定 Skill 文档映射
commit        检查提交信息、staged 语法和架构门禁后正式提交
check PATH    运行通用机械检查并显示 Git/worktree 状态
```

`skills` 同时支持两种自研仓布局：

- 通用仓的 `<category>/<skill>/SKILL.md` + `docs/<category>/<skill>.md`；
- 产品仓的 `skills/<category>/<skill>/SKILL.md` + `docs/<category>/<skill>.md`，并兼容旧的 `skills/<skill>/SKILL.md` + `docs/<skill>.md`。

普通提交不默认运行全项目 lint/typecheck/build/test；大型、关键或高风险修改按失败模式追加 targeted tests、schema/migration validation 等。

## Submodule ownership

受管 first-party source：

```text
skills/akira     → git@github.com:Akira-TL/skills.git
skills/research  → git@github.com:Akira-TL/akira-research-skills.git
skills/matt      → git@github.com:Akira-TL/matt-skills.git
```

第三方 Skill 来源不作为 Lattice submodule。当前可信外部来源及发现方式由 `skills/akira` 中的 `akira` Router 维护；需要时只安装当前任务对应的具体 Skill。

修改 Skill 时先在 child repository 提交，再更新 Lattice pointer。Research、Matt 与通用 Akira 仓之间不通过相对路径偷读彼此正文；共享能力通过安装后的 Skill/capability 契约协作。

## 卸载

`./uninstall.sh` 只移除直接指向本仓库的静态配置软链接。所有 Skill 注册项、manifest、Git source checkout 与执行器自己的 Skill 引用都保持不变。
