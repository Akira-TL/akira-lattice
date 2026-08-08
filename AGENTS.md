# Repository instructions

This repository is the source of truth for Akira's agent skills and maintained global static Agent configuration.

## Source and documentation

Skill runtime source lives under `skills/<category>/<skill-name>/`. Each stable skill has one canonical `SKILL.md`; optional sibling reference files are loaded through explicit context pointers.

Human-facing explanations live under `docs/<category>/<skill-name>.md`. Documentation explains what a skill does, when to use it, and how to install it. It must not duplicate the entire runtime source.

Global static Agent configuration lives under `core/`. `core/AGENTS.md` contains short stable cross-project defaults and routing; `core/references/` contains low-frequency facts and boundaries. Deterministic checks and deployment live under `scripts/`. `~/.agents` and tool-specific prompt paths are runtime views, never canonical source.

Keep large procedures in skills, small stable defaults in the core, and mechanically decidable rules in the Guard. Project knowledge stays with the Matt flow's project context; dynamic context and Memory are outside this repository. Keep software-managed state such as skill installation locks, MCP configuration, plugin state, caches, and sessions outside this repository unless ownership is explicitly changed.

## Lifecycle

Stable skills live in a named category such as `productivity` or `engineering`.

Unsettled skills live under `skills/in-progress/` and must not be advertised as stable.

Retired skills move to `skills/deprecated/` with a migration note. Do not silently delete a published skill name.

## Authoring discipline

Choose whether a skill is user-invoked or model-invoked before writing its body. A user-invoked skill sets `disable-model-invocation: true`; a model-invoked skill uses a concise description containing only distinct invocation branches.

Write ordered work as checkable steps. Keep durable rules near the behavior they govern. Push branch-specific or long reference material into clearly named sibling files and link it with an explicit context pointer.

Keep one source of truth for each rule. Remove duplication, stale sediment, generic no-op advice, and accidental prompt sprawl. Prefer positive target behavior; retain prohibitions only for hard guardrails.

Skill directory names and frontmatter `name` values use lowercase kebab-case and should match.

## Changes

Update the matching user documentation when behavior visible to users changes. Record published behavior changes in `CHANGELOG.md`. After changing Core rules, Guard rules, or stable skills, run `uv run scripts/guard.py check .` before considering the repository change complete.

Do not add release tooling, package metadata, CI, marketplace manifests, or a license by assumption. Treat each as a separate repository decision.

Do not copy third-party skill text into this repository without checking its license and recording attribution where required.
