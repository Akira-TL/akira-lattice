# ADR 0003：Skill 安装能力由 `akira` Router 持有

## Status

Accepted；首次 bootstrap 边界由 ADR 0004 补充。

## Context

Lattice 根仓同时承担静态 Agent 配置部署和机器级 Skill 生命周期后，`scripts/install.py`、`scripts/skills.py`、`scripts/skill_manager.py`、`scripts/uninstall.py` 与 `scripts/guard.py` 都需要理解 `~/.agents/sources/`、`~/.agents/skills/` 和 Skill manifest。这样会把“当前任务缺什么能力、是否应安装、安装哪一组 Skill”的 Router 语义与根仓静态配置部署耦合。

Skill 安装实际只在 Agent 已识别能力缺口并决定补充能力时发生。来源、安装粒度、用户授权和 owner 交接本来就由 `akira` Router 决定，因此机械安装实现也应随 Router 一起发布。

## Decision

- `akira` Router 同时拥有 Skill 发现后的机器级安装能力。
- 安装实现位于 `routing/akira/scripts/`，随 `Akira-TL/skills` 发布；对应测试与 Router 同仓维护。
- Router 已经可用后，Agent 按“当前会话 → `~/.agents/skills/` → Catalog / 外部来源”判断能力缺口，取得用户明确同意后主动调用 `~/.agents/skills/akira/scripts/skills.py`。
- 机器级 source、注册表与 manifest 仍分别使用 `~/.agents/sources/`、`~/.agents/skills/` 和 `~/.agents/akira-skills.json`。
- Lattice 根仓不实现通用 Skill 生命周期；根 Guard 只检查 Lattice 配置、仓库结构与 Git 约束，不检查机器级 Skill 注册状态。
- Lattice 的 Skill submodule 只用于开发、review、provenance 与固定 revision，不作为运行时安装源。
- `akira` 本体的首次 bootstrap 由 ADR 0004 定义为根安装器的窄例外：只从云端执行 `akira` 自带安装器并保证基础 Skill 存在。

## Consequences

- Skill 的路由决策、安装命令、实现和测试具有单一 owner，不再跨 Lattice 根仓与 Router 仓维护。
- 根安装只会显式 bootstrap ADR 0004 定义的基础 Skill；除此之外不会隐式增加或删除 Skill。根卸载不负责通用 Skill 生命周期。
- Research、Matt 与外部能力只需要遵守 `akira` Router 的安装契约，不依赖 Lattice 根脚本路径。
- 新机器首次获得 `akira` Router 的 bootstrap 与后续按需 Skill 生命周期保持明确分离。
