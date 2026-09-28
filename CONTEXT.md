# Repository context

## Purpose

`akira-lattice` is Akira's maintained Agent infrastructure repository for durable static Agent configuration, Guard rules, deployment, routing metadata, and pinned Skill repositories. It is not a dynamic-context or Memory system, not an installation directory, and not a dump of runtime state.

## Ubiquitous language

**Akira common Skill source** means `skills/akira` (`Akira-TL/skills`). It owns the always-installed `akira` capability Router with its built-in Guard execution/semantics layer, plus cross-domain Productivity and harness-agnostic Agent orchestration.

**Research Skill source** means `skills/research` (`Akira-TL/akira-research-skills`). It owns the complete Research workflow family and research.sqlite provenance model.

**Matt Skill source** means `skills/matt` (`Akira-TL/matt-skills`). It tracks our Matt fork and also owns the Akira engineering deltas that extend Matt directly: `ask-akira`, `parallel-coordinator`, and `parallel-execution`.

**Pinned source** means a repository recorded as a Lattice Git submodule for development, reproducibility, and Guard checks. A pinned source is not automatically part of the global runtime installation.

**Global baseline Skills** are the deliberately small set installed by Lattice for every environment. The current baseline is `akira` and `browser-access`; Guard is bundled inside `akira`. Specialised common Skills remain on-demand user capabilities, while Matt Engineering, Research, Review and Akira Knowledge are project-level workflows installed only into the target project's Skiloom `workspace` Target.

**Global configuration source** means `core/`. `core/AGENTS.md` is the always-loaded core; `core/references/` contains low-frequency facts and tool boundaries.

**Akira Guard** means the built-in `scripts/guard.py` inside the always-installed `akira` Package, exposed at `~/.agents/skills/akira/scripts/guard.py`. It is the cross-project mechanical interface for architecture, Skill-repository, staged syntax, and guarded Git commits. Lattice-specific static configuration and submodule topology checks live separately in root `scripts/lattice_check.py`. Guard does not replace semantic judgement such as diff ownership.

**Runtime configuration view** means `~/.agents` and tool-specific files such as `~/.claude/CLAUDE.md`. These expose canonical source and are not independent copies.

**本地上下文资料** 指 `~/.config/akira/` 中按任务域按需读取的长期个人资料。它不属于 Lattice 静态配置源码；Core 只维护读取边界与路由。

**Externally managed state** means `~/.agents/skills/`, `.skill-lock.json`, MCP/plugin state, caches, sessions, and similar generated state. It is not copied into this repository by default.

## Current boundary

The common repository contains `akira` (including Guard), `browser-access`, `general-word-document-generation`, `scientific-presentation-authoring`, and `agent-orchestration`. Research/Review, Matt, and Knowledge are independent product repositories with their own Primary Routers.

Project-local capability expansion is routed by `akira`: install the smallest missing common Skill when possible; install Matt Engineering, Research, Review or Akira Knowledge into the current project's / Vault's `workspace` Target only when sustained work requires that workflow family. These professional product suites are not part of the global user Target.
