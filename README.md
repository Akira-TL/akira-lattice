# Akira Lattice

Akira 的个人 Agent 基础设施与 Skill source control 仓库。这里维护跨项目 Core、Guard、部署、能力 Router，以及各独立 Skill 仓库的固定版本；`~/.agents` 只作为运行时视图。

## Repository layout

```text
akira-lattice/
├── core/                    # 全局静态 Agent 配置
├── scripts/                 # Lattice install / uninstall / repository check
├── skills/
│   ├── akira/               # Akira-TL/skills：通用 Skills + akira Router
│   ├── research/            # Akira-TL/akira-research-skills
│   ├── matt/                # Akira-TL/matt-skills：Matt + Akira engineering extensions
│   └── knowledge/           # Akira-TL/akira-knowledge-skills：Akira Knowledge
├── docs/                    # Lattice 基础设施说明
└── .agents/adr/             # 长期架构决定
```

## Capability model

仓库边界按高内聚能力域划分：

- **Akira common**：Router、浏览器、Word、科研/学术 PPT、Guard 语义和通用 Agent 编排。
- **Matt Engineering**：`ask-akira` 作为软件工程 Primary Router；`standard` 按需进入 `ask-matt` 的 Matt 标准工程流，Parallel 系列负责正式多 Agent coordination。
- **Akira Research**：完整科研生命周期与 `research.sqlite` provenance，单独成仓。
- **Akira Knowledge**：独立产品仓；`akira-knowledge` 为 Primary Router，Capture / Curate / Maintain / Retrieve 由 Package dependency graph 组织。

Lattice pin 某个 source 不等于把它全局安装。

## 静态配置部署与 Skill 安装边界

根目录入口：

```bash
./install.sh
```

该入口要求 `skiloom >= 0.8.15`，部署 Lattice 的 Core、references 与静态运行时链接；Skill bootstrap 先以 Git `main` 安装 `akira-tl/skiloom/skiloom`，再通过同一 public CLI 安装 Akira 最小用户级基线：`akira-tl/skills/akira` 与 `akira-tl/skills/browser-access`。Guard 已内置在必装 `akira` Package 中。Lattice 本地 `skills/*` submodule 只用于开发、review 与固定 revision，不是运行时安装源。

后续由 `akira` Router 判断当前任务需要哪个入口 Package；完整 dependency closure、source resolution、exact revision、Registry / Store / Target ownership、安装、更新、移除、同步、修复与恢复全部由 Skiloom 管理。当前 first-party source mode 使用 Git `main`。

典型流程：

```text
skiloom install <coordinate> --git main --scope user --plan --json
skiloom install <coordinate> --git main --scope user --yes --json
```

Akira 不再维护 `~/.agents/akira-skills.json`、`~/.agents/sources/` 或自己的 Git + symlink installer，也没有 Skiloom 失败后的 fallback 路径。

## Guard

跨项目 Guard 内置在默认安装的 `akira` Package 中：

```bash
uv run ~/.agents/skills/akira/scripts/guard.py skills ./skills/akira
uv run ~/.agents/skills/akira/scripts/guard.py skills ./skills/research
uv run ~/.agents/skills/akira/scripts/guard.py check .
```

Lattice 自身的静态配置与 submodule 拓扑检查单独运行：

```bash
uv run scripts/lattice_check.py
```

`akira/scripts/guard.py commit` 是正式 Git 提交入口；项目自身测试、schema validator 和高风险验证按实际修改追加。

## Source ownership

修改 Skill 时先在 owning submodule 提交，再更新 Lattice pointer：

- 通用 / Router → `skills/akira`
- Research → `skills/research`
- Matt / Ask Akira / Parallel → `skills/matt`
- Knowledge → `skills/knowledge`

Matt 系列由 `Akira-TL/matt-skills` 独立维护；原 `mattpocock/skills` 只作为选择性参考 upstream，不再整体 merge。具体规则见 `core/references/matt-skills.md`。
