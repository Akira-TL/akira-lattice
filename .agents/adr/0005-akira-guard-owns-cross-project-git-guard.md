# ADR 0005：跨项目 Git Guard 由 `akira-guard` Skill 持有

## Status

Accepted

## Context

此前 Akira Guard 的使用语义位于 `skills/akira/engineering/akira-guard/`，而实际 `guard.py` 与 staged syntax 实现位于 Lattice 根 `scripts/`。这造成同一能力被两个仓库共同拥有：Skill 负责解释，Lattice 负责执行；同时所有项目的正式 Git 提交依赖 Lattice checkout 的运行时软链接。

`akira-guard` 本身是跨项目基础能力，不依赖 Research、Matt 或某个执行器，也不应要求目标项目了解 Lattice 的 submodule 与静态配置拓扑。Lattice 自身的配置检查则相反，只对本仓有效，不属于通用 Guard。

## Decision

- `Akira-TL/skills` 的 `engineering/akira-guard/` 成为跨项目 Guard 的唯一 canonical owner。
- `akira-guard/scripts/guard.py` 提供 `architecture`、`skills`、`commit` 与 `check`；`staged_syntax.py` 与对应测试随同一 Skill 维护。
- 正式 Git 提交入口改为 `uv run ~/.agents/skills/akira-guard/scripts/guard.py commit -m '<message>'`。
- Lattice 根仓删除跨项目 `scripts/guard.py`、`scripts/staged_syntax.py` 及其重复测试，只保留 `scripts/lattice_check.py` 检查本仓静态配置、submodule revision 与 remote ownership。
- `akira-guard` 加入 Lattice 的基础云端 bootstrap，与 `akira`、`browser-access` 一起默认安装。
- 不增加全局 Git Hook；Guard 仍由 Agent 在需要时显式调用，不抢占项目自己的 Husky、pre-commit、lefthook 或其他 hook。

## Consequences

- Guard 的说明、执行脚本与测试具有单一 owner，可随 Skill source 一起更新和安装。
- 普通项目不再依赖 Lattice checkout 才能使用受控 Git commit 与 staged syntax 检查。
- Lattice 的仓库拓扑检查与跨项目 Guard 解耦；前者是项目维护工具，后者是默认基础 Skill。
- 新机器运行 `./install.sh` 后立即具备 Router、浏览器访问和 Guard 三项基础能力。
