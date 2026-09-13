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

## ForgeRelay 运行时安装

统一入口：

```bash
./install.sh
```

Lattice 只在 ForgeRelay 运行时常驻极小基线：

```text
akira
browser-access
```

Skill source 由 Lattice 自带安装器直接从 GitHub clone/fetch 到 `~/.agents/sources/`；`~/.agents/skills/` 是全局软链接视图，`~/.forgerelay/skills/` 再链接到其中的 ForgeRelay 常驻基线。Skill 内容不复制，安装器只依赖 Python 标准库与 Git，不依赖第三方 Skill package manager。

同时部署 Core、references 与 Guard scripts。Matt、Research、Word、PPT、Agent 编排以及第三方专业能力都不常驻；当前项目真实需要时，由 `akira` Router 说明来源和用途、取得用户明确同意后项目级安装。

例如软件工程项目由 Router 按 Catalog 推荐 `Akira-TL/matt-skills` 的 promoted suite；科研项目则项目级安装完整 Research suite。二者都使用：

```bash
python3 ~/.agents/scripts/skills.py install <github-source> ... --project .
```

精确 source、目录范围和额外 Skill 以 `akira` 的 `CATALOG.md` 为准。

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
