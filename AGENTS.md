# Repository instructions

This repository is the source of truth for Akira's maintained global static Agent configuration, Guard, deployment, cross-repository routing, and pinned Skill repositories.

## Source and ownership

Akira Skill source is intentionally split by cohesion rather than stored in one monorepo:

- `skills/akira` → `Akira-TL/skills`：通用 Akira Skills 与 `akira` 能力 Router。保留 Productivity、Akira Guard 和通用 Agent 编排。
- `skills/research` → `Akira-TL/akira-research-skills`：完整 Research 产品族，拥有自己的 `skills/`、`docs/`、scripts、tests 与 research.sqlite 契约。
- `skills/matt` → `Akira-TL/matt-skills`：Matt fork。Matt 工程方法以及 Akira 的 `ask-akira` / Parallel 系列工程扩展都在这里维护。
- `skills/openai-plugins`：只读第三方源码 pin，不属于 Akira 自研 Skill 正文。

不要为了路由方便复制产品正文。未来只有当 Knowledge 等能力形成独立、高内聚产品族时才新增子仓。

Lattice `docs/` 只保存基础设施、部署、仓库拓扑和第三方 source 说明；Skill 的人类文档跟随其 owning repository。

Global static Agent configuration lives under `core/`. Deterministic checks and deployment live under `scripts/`. `~/.agents` and tool-specific prompt paths are runtime views, never canonical source.

## Installation boundary

Global installation is deliberately small. Lattice installs only `akira` Router and the explicitly declared cross-domain baseline from `skills/akira`; Matt, Research and non-baseline common Skills are installed project-locally when the Router identifies a real need and the user explicitly agrees.

Being pinned as a Lattice submodule does not mean a Skill repository is globally installed.

## Authoring discipline

Choose user-invoked vs model-invoked before writing a Skill. Keep ordered work checkable, disclose branch-specific material through explicit references, and keep one source of truth for each rule.

Stable Skill behaviour changes require the owning repository's docs to change in the same semantic stage. Do not copy third-party Skill text without checking licence and attribution.

## Agent 间交接

凡是主要用于让用户复制给另一个 Agent、另一个会话或其他 Agent harness 的完整内容，例如 handoff、黑盒验收提示词、独立复核说明、Worker briefing 或长篇执行指令，统一先写入操作系统 `/tmp/` 下的描述性 Markdown 文件。用户回复中只提供文件路径和最短可执行提示词。

普通面向用户阅读的解释、结论和讨论不适用这条规则。

## Changes

修改 Skill 时先在 owning child repository 完成、验证并提交，再回到 Lattice 更新对应 submodule pointer。Router / 通用 Skill 修改属于 `skills/akira`；Research 修改属于 `skills/research`；Matt workflow、`ask-akira` 和 Parallel 修改属于 `skills/matt`。

Core、Guard、安装器、Router 产品目录或 submodule 集成变化需要记录 Lattice `CHANGELOG.md`，并在提交后运行适用的 Guard / targeted tests。

Do not add release tooling, package metadata, CI, marketplace manifests, or a license by assumption. Treat each as a separate repository decision.
