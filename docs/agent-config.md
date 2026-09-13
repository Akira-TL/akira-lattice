# Agent 静态配置管理

本仓库维护 Akira 的全局静态 Agent 规则、机械 Guard、运行时部署和受管 Skill source。`~/.agents` 只是运行时入口，不是第二份源码仓库。

## 分层

```text
akira-lattice/
├── core/
│   ├── AGENTS.md
│   └── references/
├── scripts/
│   ├── install.py
│   ├── uninstall.py
│   ├── guard.py
│   └── upstream.py
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
- **Guard**：机械可判断的约束；不复制业务/科研语义。
- **Runtime state**：远端 Skill source 统一 clone/fetch 到 `~/.agents/sources/`；机器级 `~/.agents/skills/` 保存指向 source checkout 的受管软链接。这两层是 Akira 管理的唯一 Skill source 与机器级注册层。具体执行器自己的 Skill 目录、缓存、profile 与项目级引用由对应执行器管理；需要持久暴露 Skill 时，由执行器自行建立指向 `~/.agents/skills/<name>` 的软链接，不维护第二份 source checkout。

## 运行时拓扑

```text
~/Projects/akira-skills/core/AGENTS.md
          ├──→ ~/.agents/AGENTS.md
          ├──→ ~/.codex/AGENTS.md
          ├──→ ~/.claude/CLAUDE.md
          └──→ ~/.config/opencode/AGENTS.md
```

`~/.agents/references` 指向 `core/references/`，`~/.agents/scripts` 指向根 `scripts/`。第三方 Skill 仓不再由 Lattice 固定为 submodule 或运行时 source view；需要时由 `akira` Router 从登记来源发现并安装到机器级 `~/.agents/skills/`。

## 默认安装策略

根目录：

```bash
./install.sh
```

Lattice pin 住多个 Skill 仓是为了开发、版本与 provenance，不代表全部进入机器级注册表。根安装器默认保证以下基础 Skill 已注册：

```text
akira
browser-access
```

`akira` 负责能力路由；`browser-access` 是 Research、Knowledge、工程与通用资料获取经常共同需要的跨域执行能力。根安装器保证这两个 Skill 注册到 `~/.agents/skills/`。机器上后续真实使用过的 Matt、Research 或其他通用 Skill 也可以继续保留在该机器级注册表。

软件工程任务缺少 `ask-matt` 时，Core 会先交给 `akira` Router。Router 先检查 `~/.agents/skills/`；已有 Matt suite 时不重复安装，缺失时在用户同意后从 `Akira-TL/matt-skills` 远端安装到机器级注册表。`ask-akira` 和 Parallel 系列随 Matt fork 提供，不存在独立 Engineering 产品仓。

科研任务同样先复用机器级已有 Research suite；缺失时才从已发布的 `Akira-TL/akira-research-skills` 安装。Word、科研/学术 PPT、Guard Skill 或 `agent-orchestration` 也遵循相同的“当前会话 → 机器级注册表 → 远端 source”发现顺序。

安装器只管理机器级 manifest `~/.agents/akira-skills.json`、`~/.agents/sources/` checkout 与 `~/.agents/skills/` 软链接。更新只更新共享 Git checkout；卸载只删除受管机器级注册项；未知普通目录和其他来源的软链接 fail closed。具体执行器只管理自己的 Skill 视图，需要时自行软链接到 `~/.agents/skills/<name>`；Akira 安装器不写这些执行器目录。

## Guard

统一入口：

```bash
uv run ~/.agents/scripts/guard.py <command>
```

主要命令：

```text
config        检查静态配置、默认运行时基线与受管 submodule
architecture  检查代码与目录规模
skills PATH   检查指定 Akira Skill 仓的结构与稳定 Skill 文档映射
commit        检查提交信息、staged 语法和架构门禁后正式提交
upstream matt 同步 Matt fork upstream；显式 --push 时才发布
check PATH    组合运行当前路径适用检查并显示 Git/worktree 状态
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

`./uninstall.sh` 只移除机器级 manifest 中登记的 `akira` / `browser-access` 基线软链接，以及直接指向本仓库的静态配置软链接。机器级注册的其他 Matt / Research / 通用 Skill、各执行器自己的引用和 `~/.agents/sources/` Git checkout 都不会被猜测性清理。
