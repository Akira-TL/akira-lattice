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
│   └── matt/                # Akira-TL/matt-skills：Matt + Akira engineering extensions
├── docs/                    # Lattice 基础设施说明
└── .agents/adr/             # 长期架构决定
```

## Capability model

仓库边界按高内聚能力域划分：

- **Akira common**：Router、浏览器、Word、科研/学术 PPT、Guard 语义和通用 Agent 编排。
- **Matt Engineering**：`ask-akira` 作为软件工程 Primary Router；`standard` 按需进入 `ask-matt` 的 Matt 标准工程流，Parallel 系列负责正式多 Agent coordination。
- **Akira Research**：完整科研生命周期与 `research.sqlite` provenance，单独成仓。
- **Akira Knowledge**：待形成真实知识工作流后再单独建仓，不维护空产品。

Lattice pin 某个 source 不等于把它全局安装。

## 静态配置部署与 Skill 安装边界

根目录入口：

```bash
./install.sh
```

该入口部署 Lattice 的 Core、references 与静态运行时链接，并从远端 `https://github.com/Akira-TL/skills.git` bootstrap 最小机器级基线：`akira`、`browser-access` 与 `akira-guard`。bootstrap 使用临时 GitHub checkout 中的 `akira` 安装器执行，不从 Lattice 本地 `skills/akira` submodule 安装 Skill。

除这三个基础 Skill 的首次/重复 bootstrap 外，Skill 生命周期由 `akira` Router 自己拥有。Router 已经可用后，Agent 先复用当前会话能力，再检查机器级 `~/.agents/skills/`；确有缺口时读取 Catalog，向用户说明来源、用途和最小安装范围，取得明确同意后调用：

```bash
uv run python ~/.agents/skills/akira/scripts/skills.py <command> ...
```

该脚本负责远端 Git source、`~/.agents/sources/`、`~/.agents/skills/` 和机器级 manifest。Lattice 中的 `skills/akira`、`skills/research`、`skills/matt` 只用于开发、review 与固定 revision，不是运行时安装源。

根安装器只负责 bootstrap `akira`、`browser-access` 与 `akira-guard`；后续通用 Skill、Matt、Research 与外部能力都由 `akira` Router 按真实任务主动安装。

## Guard

跨项目 Guard 由默认安装的 `akira-guard` Skill 提供：

```bash
uv run ~/.agents/skills/akira-guard/scripts/guard.py skills ./skills/akira
uv run ~/.agents/skills/akira-guard/scripts/guard.py skills ./skills/research
uv run ~/.agents/skills/akira-guard/scripts/guard.py check .
```

Lattice 自身的静态配置与 submodule 拓扑检查单独运行：

```bash
uv run scripts/lattice_check.py
```

`akira-guard ... commit` 是正式 Git 提交入口；项目自身测试、schema validator 和高风险验证按实际修改追加。

## Source ownership

修改 Skill 时先在 owning submodule 提交，再更新 Lattice pointer：

- 通用 / Router → `skills/akira`
- Research → `skills/research`
- Matt / Ask Akira / Parallel → `skills/matt`

Matt 系列由 `Akira-TL/matt-skills` 独立维护；原 `mattpocock/skills` 只作为选择性参考 upstream，不再整体 merge。具体规则见 `core/references/matt-skills.md`。
