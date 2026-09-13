# Akira Lattice

Akira 的个人 Agent 基础设施与 Skill source control 仓库。这里维护跨项目 Core、Guard、部署、能力 Router，以及各独立 Skill 仓库的固定版本；`~/.agents` 只作为运行时视图。

## Repository layout

```text
akira-lattice/
├── core/                    # 全局静态 Agent 配置
├── scripts/                 # Guard / install / uninstall / upstream
├── skills/
│   ├── akira/               # Akira-TL/skills：通用 Skills + akira Router
│   ├── research/            # Akira-TL/akira-research-skills
│   └── matt/                # Akira-TL/matt-skills：Matt + Akira engineering extensions
├── docs/                    # Lattice 基础设施说明
└── .agents/adr/             # 长期架构决定
```

## Capability model

仓库边界按高内聚能力域划分：

- **Akira common**：Router、浏览器、Word、科研/学术 PPT、Guard 语义和通用 Agent 编排。
- **Matt Engineering**：Matt 工程工作流；`ask-akira`、`parallel-coordinator`、`parallel-execution` 作为本 fork 的工程扩展与 Matt 同仓。
- **Akira Research**：完整科研生命周期与 `research.sqlite` provenance，单独成仓。
- **Akira Knowledge**：待形成真实知识工作流后再单独建仓，不维护空产品。

Lattice pin 某个 source 不等于把它全局安装。

## 机器级 Skill 安装

统一入口：

```bash
./install.sh
```

Lattice 默认保证以下机器级基础 Skill 已注册：

```text
akira
browser-access
```

Skill source 由 Lattice 自带安装器直接从 GitHub clone/fetch 到 `~/.agents/sources/`；`~/.agents/skills/` 是机器级已安装 Skill 注册表，只保存指向 Git checkout 的软链接。Skill 内容不复制，安装器只依赖 Python 标准库与 Git，不依赖第三方 Skill package manager。

同时部署 Core、references 与 Guard scripts。Matt、Research、Word、PPT、Agent 编排以及第三方专业能力只在真实任务需要时由 `akira` Router 先检查机器级注册表；机器级缺失时再说明来源和用途、取得用户明确同意后从远端安装。

例如软件工程任务由 Router 按 Catalog 推荐 `Akira-TL/matt-skills` 的 promoted suite；科研任务则安装完整 Research suite：

```bash
python3 ~/.agents/scripts/skills.py install <github-source> ...
```

ForgeRelay、Claude Code、Codex 等执行器如何暴露 Skill，由各执行器自己的机制负责，不属于 Akira Skill 安装器。执行器需要自己的 Skill 目录时，应由执行器自行建立指向 `~/.agents/skills/<name>` 的软链接；不得复制 Skill 内容或维护第二份 source checkout。精确 source、目录范围和额外 Skill 以 `akira` 的 `CATALOG.md` 为准。

## Guard

```bash
uv run scripts/guard.py config
uv run scripts/guard.py skills ./skills/akira
uv run scripts/guard.py skills ./skills/research
uv run scripts/guard.py check .
```

`commit` 仍是正式 Git 提交入口；项目自身测试、schema validator 和高风险验证按实际修改追加。

## Source ownership

修改 Skill 时先在 owning submodule 提交，再更新 Lattice pointer：

- 通用 / Router → `skills/akira`
- Research → `skills/research`
- Matt / Ask Akira / Parallel → `skills/matt`

Matt upstream 同步继续使用：

```bash
uv run scripts/guard.py upstream matt
```
