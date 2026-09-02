# Repository instructions

This repository is the source of truth for Akira's agent skills and maintained global static Agent configuration.

## Source and documentation

Akira-maintained Skill runtime source lives in the `skills/akira` Git submodule under `<category>/<skill-name>/`. Each stable skill has one canonical `SKILL.md`; optional sibling reference files are loaded through explicit context pointers. `skills/matt` is a separate submodule for the maintained Matt skills fork and is not part of Akira-authored Skill source.

Akira-maintained Skill user documentation lives with its source under `skills/akira/docs/<category>/<skill-name>.md`. Lattice `docs/` is reserved for this repository's infrastructure and configuration documentation; it must not keep a second copy of Skill-specific docs.

Global static Agent configuration lives under `core/`. `core/AGENTS.md` contains short stable cross-project defaults and routing; `core/references/` contains low-frequency facts and boundaries. Deterministic checks and deployment live under `scripts/`. `~/.agents` and tool-specific prompt paths are runtime views, never canonical source.

Keep large procedures in skills, small stable defaults in the core, and mechanically decidable rules in the Guard. Project knowledge stays with the Matt flow's project context; dynamic context and Memory are outside this repository. Keep software-managed state such as skill installation locks, MCP configuration, plugin state, caches, and sessions outside this repository unless ownership is explicitly changed.

## Lifecycle

Stable skills live in a named category such as `productivity` or `engineering`.

Unsettled Akira skills live under `skills/akira/in-progress/` and must not be advertised as stable.

Retired Akira skills move to `skills/akira/deprecated/` with a migration note. Do not silently delete a published skill name.

## Authoring discipline

Choose whether a skill is user-invoked or model-invoked before writing its body. A user-invoked skill sets `disable-model-invocation: true`; a model-invoked skill uses a concise description containing only distinct invocation branches.

Write ordered work as checkable steps. Keep durable rules near the behavior they govern. Push branch-specific or long reference material into clearly named sibling files and link it with an explicit context pointer.

Keep one source of truth for each rule. Remove duplication, stale sediment, generic no-op advice, and accidental prompt sprawl. Prefer positive target behavior; retain prohibitions only for hard guardrails.

Skill directory names and frontmatter `name` values use lowercase kebab-case and should match.

## Agent 间交接

凡是主要用于让用户复制给另一个 Agent、另一个会话或其他 Agent harness 的完整内容，例如 handoff、黑盒验收提示词、独立复核说明、Worker briefing 或长篇执行指令，统一先写入操作系统 `/tmp/` 下的描述性 Markdown 文件。用户回复中不再内联整段正文，只提供文件路径和一条最短可执行提示词，例如：`请读取 /tmp/<file>.md，并严格按照其中要求执行。` 这样把长上下文交给文件传递，用户只需复制短提示词。

普通面向用户阅读的解释、结论和讨论不适用这条规则。只有目标内容本身是给另一个 Agent 消费时才写入 `/tmp/`；完整内容必须先成功落盘后，才能把短提示词交给用户。

## Changes

When an Akira Skill changes behavior, update its documentation inside `skills/akira` and commit that child repository before updating the Lattice submodule pointer. Record Lattice-visible infrastructure changes in `CHANGELOG.md`. After changing Core rules, Guard rules, or submodule integration, run `uv run scripts/guard.py check .` before considering the repository change complete.

Do not add release tooling, package metadata, CI, marketplace manifests, or a license by assumption. Treat each as a separate repository decision.

Do not copy third-party skill text into this repository without checking its license and recording attribution where required.
