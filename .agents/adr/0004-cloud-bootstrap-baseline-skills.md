# ADR 0004：Lattice 根安装器只从云端 bootstrap 基础 Skills

## Status

Accepted

## Context

`akira` Router 拥有通用 Skill 生命周期，但新机器在 `akira` 尚未安装时无法调用它自己的安装器。如果把完整 Skill manager 重新放回 Lattice 根仓，会再次造成双重 owner；如果要求人工先安装 `akira`，则根安装入口不能完成最小可用环境初始化。

## Decision

- `./install.sh` 除部署 Core 静态配置外，负责 bootstrap 两个基础 Skill：`akira` 与 `browser-access`。
- bootstrap 只从 `https://github.com/Akira-TL/skills.git` 获取，不从 Lattice 本地 `skills/akira` submodule 安装。
- 根安装器不复制 Akira 的 Skill manager 实现。它创建临时 Git checkout，执行该云端 checkout 中 `routing/akira/scripts/skills.py`，由 `akira` 自己的安装实现完成 canonical source、manifest 与机器级软链接注册。
- bootstrap 完成后，所有其他 Skill 的发现、安装、更新、删除与诊断仍由已经安装的 `akira` Router 负责。
- Lattice 根卸载器不反向猜测或清理机器级 Skill 状态；Skill 生命周期继续通过 `akira` 安装器显式处理。

## Consequences

- `./install.sh` 可以把新机器带到最小可用状态，同时不建立第二套通用 Skill installer。
- 基础 Skill 的实体仍来自远端 GitHub checkout；Lattice submodule 继续只用于开发、review 与 revision 固定。
- 根安装需要 GitHub 网络访问和 Git；云端 bootstrap 获取失败时安装明确失败，不退化为本地 submodule 安装。
