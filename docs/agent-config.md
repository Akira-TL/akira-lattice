# Agent 静态配置管理

本仓库维护 Akira 的全局静态 Agent 规则、运行时部署、Lattice 自检和各 Skill 仓的固定开发 revision；跨项目机械 Guard 内置在必装 `akira` Package 中。`~/.agents` 只是运行时入口，不是第二份源码仓库。

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
│   ├── matt/                # Matt fork + Akira engineering extensions
│   └── knowledge/           # Akira Knowledge
├── docs/
└── .agents/adr/
```

边界：

- **Core**：短小、稳定、跨项目并需要常驻的默认规则。
- **Akira common Skills**：跨领域可复用能力和能力 Router；Productivity、Akira Guard、通用 Agent 编排留在 `skills/akira`。Skill 生命周期不再由 Akira 自建安装器实现。
- **Matt Engineering**：软件工程方法与其 Akira delta 同仓。`ask-akira`、`parallel-coordinator`、`parallel-execution` 属于 `skills/matt`，因为它们直接扩展 Matt 的 Spec/Ticket/implement/TDD/review 流程。
- **Research**：共享 Research Tree、schema、migration、research.sqlite 与科研对象契约，作为独立 `skills/research` 产品仓。
- **Akira Guard**：跨项目 Git 提交、暂存语法、架构与 Skill 结构机械检查，作为必装 `akira` Package 的内置执行能力持有。Lattice 根仓只保留自身静态配置与 submodule 拓扑检查。
- **Runtime state**：Skill Package 的 Registry、Store、Target identity、accepted exact state、managed projection 与 recovery 统一由 Skiloom 拥有。`akira` 只选择入口 Package与默认 scope；旧 `~/.agents/akira-skills.json` 与 `~/.agents/sources/` 不再是 lifecycle authority。Lattice 默认 bootstrap 使用 Skiloom `--scope user` Target；Matt Engineering、Research、Review 与 Akira Knowledge 使用目标项目 / Vault 工作目录下的 `--scope workspace` Target，并不进入用户级 `~/.agents/skills`。

## 运行时拓扑

```text
~/Projects/akira-skills/core/AGENTS.md
          └──→ ~/.agents/AGENTS.md
```

`~/.agents/AGENTS.md` 是全局规则入口；其他运行环境需要自己的规则入口时，由部署层建立指向同一 canonical source 的兼容引用，不在全局规则或架构文档中枚举具体产品。`~/.agents/references` 指向 `core/references/`，`~/.agents/scripts` 指向根 `scripts/`。根 `scripts/` 只提供 Lattice 静态配置部署、Skiloom 基础 Package bootstrap 与 Lattice 自检；跨项目 Guard 脚本随必装 `akira` Package 发布。外部 Skill 仓不作为 Lattice submodule，需要时由 `akira` Router 选择候选并交给 Skiloom。

## Skill 安装边界

根目录：

```bash
./install.sh
```

该命令先确认 `skiloom >= 0.8.15`，再部署 Core、references 与其他静态配置链接。Skill bootstrap 先以显式 Git `main` 安装 `akira-tl/skiloom/skiloom`，随后通过同一 public CLI 把 `akira-tl/skills/akira` 与 `akira-tl/skills/browser-access` 作为 Akira 基础 direct requirements 安装到用户级 Target。Guard 已内置在 `akira` Package 中。Lattice 本地 submodule 仍只用于开发、review、provenance 与固定 source revision。

基础 bootstrap 完成后，`akira` Router 只负责判断能力缺口、选择入口 Package coordinate 与 Catalog 登记的默认 scope；Skiloom 负责完整 Candidate Graph、dependency closure、source authorization、exact revision、Store、Target ownership 与生命周期状态。Matt / Research / Review / Knowledge 必须从目标项目 / Vault 对应工作目录使用 `workspace` scope；新增能力时先生成 `--plan --json`，用户明确授权后才用 `--yes --json` 提交。

根卸载器只移除 Lattice 静态配置链接，不直接修改 Skiloom Target；Skill Package 的移除、修复或清理由 Skiloom 生命周期命令单独完成。

## Guard

跨项目统一入口：

```bash
uv run ~/.agents/skills/akira/scripts/guard.py <command>
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
skills/knowledge → git@github.com:Akira-TL/akira-knowledge-skills.git
```

第三方 Skill 来源不作为 Lattice submodule。当前可信外部来源及发现方式由 `skills/akira` 中的 `akira` Router 维护；需要时只安装当前任务对应的具体 Skill。

修改 Skill 时先在 child repository 提交，再更新 Lattice pointer。Research、Matt 与通用 Akira 仓之间不通过相对路径偷读彼此正文；共享能力通过安装后的 Skill/capability 契约协作。

## 卸载

`./uninstall.sh` 只移除直接指向本仓库的静态配置软链接。Skiloom Registry、Store、Target 与 accepted Package state 保持不变；需要删除 Skill Package 时另行使用 Skiloom。
