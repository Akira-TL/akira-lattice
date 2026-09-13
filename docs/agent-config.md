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
│   ├── matt/                # Matt fork + Akira engineering extensions
│   └── openai-plugins/      # 第三方只读 source pin
├── docs/
└── .agents/adr/
```

边界：

- **Core**：短小、稳定、跨项目并需要常驻的默认规则。
- **Akira common Skills**：跨领域可复用能力和安装 Router；Productivity、Akira Guard、通用 Agent 编排留在 `skills/akira`。
- **Matt Engineering**：软件工程方法与其 Akira delta 同仓。`ask-akira`、`parallel-coordinator`、`parallel-execution` 属于 `skills/matt`，因为它们直接扩展 Matt 的 Spec/Ticket/implement/TDD/review 流程。
- **Research**：共享 Research Tree、schema、migration、research.sqlite 与科研对象契约，作为独立 `skills/research` 产品仓。
- **Guard**：机械可判断的约束；不复制业务/科研语义。
- **Runtime state**：`~/.agents/skills/`、`.skill-lock.json`、MCP/plugin state、缓存与会话继续由对应软件管理。

## 运行时拓扑

```text
~/Projects/akira-skills/core/AGENTS.md
          ├──→ ~/.agents/AGENTS.md
          ├──→ ~/.codex/AGENTS.md
          ├──→ ~/.claude/CLAUDE.md
          └──→ ~/.config/opencode/AGENTS.md
```

`~/.agents/references` 指向 `core/references/`，`~/.agents/scripts` 指向根 `scripts/`。OpenAI `ngs-analysis` 继续通过 `~/.agents/external/ngs-analysis` 暴露固定 source view；它不是默认全局 Skill 集。

## 默认安装策略

根目录：

```bash
./install.sh
```

Lattice pin 住多个 Skill 仓是为了开发、版本与 provenance，不代表全部进入全局 runtime。默认全局 Skill 基线只有：

```text
akira
browser-access
```

`akira` 负责能力路由；`browser-access` 是 Research、Knowledge、工程与通用资料获取经常共同需要的跨域执行能力。其余通用 Skill 以及 Matt / Research 按真实项目需求项目级安装。

软件工程项目若尚未安装 `ask-matt`，Core 会先交给 `akira` Router；Router 说明需要 `Akira-TL/matt-skills` 的原因并获得用户明确同意后，再在当前项目安装 Matt suite。`ask-akira` 和 Parallel 系列随 Matt fork 提供，不存在独立 Engineering 产品仓。

科研项目由 Router 指向 `Akira-TL/akira-research-skills`。在新远端尚未正式发布前，Catalog 必须保持 `local-ready / remote-pending`，不能伪造可执行的远端安装来源。

Word、科研/学术 PPT、Guard Skill 或 `agent-orchestration` 只在任务真正需要时从 `Akira-TL/skills` 安装对应单一 Skill。

安装器不会为了新基线主动清理历史全局 Skill。旧 runtime 的一次性迁移应由用户显式触发，通过现有安装 manifest 与 skills CLI 安全处理，避免误删其他来源的同名 Skill。

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
- 产品仓的 `skills/<skill>/SKILL.md` + `docs/<skill>.md`。

普通提交不默认运行全项目 lint/typecheck/build/test；大型、关键或高风险修改按失败模式追加 targeted tests、schema/migration validation 等。

## Submodule ownership

受管 first-party source：

```text
skills/akira     → git@github.com:Akira-TL/skills.git
skills/research  → git@github.com:Akira-TL/akira-research-skills.git
skills/matt      → git@github.com:Akira-TL/matt-skills.git
```

第三方：

```text
skills/openai-plugins → https://github.com/openai/plugins.git
```

修改 Skill 时先在 child repository 提交，再更新 Lattice pointer。Research、Matt 与通用 Akira 仓之间不通过相对路径偷读彼此正文；共享能力通过安装后的 Skill/capability 契约协作。

## 卸载

`./uninstall.sh` 只移除仍明确属于最近一次 Lattice 安装 manifest 且内容哈希未被其他来源替换的运行时 Skill，以及直接指向本仓库的静态配置软链接。它不会猜测项目级 Matt / Research Skill，也不会清理其他软件状态。
