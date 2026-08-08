# Repository context

## Purpose

`akira-skills` is Akira's maintained source repository for reusable agent workflows and durable static Agent configuration. It is not a dynamic-context or Memory system, not an installation directory, and not a dump of local runtime state.

## Ubiquitous language

**Skill source** means the runtime instructions an agent loads for a reusable workflow. It lives in `skills/` and is authoritative for that workflow.

**Global configuration source** means the maintained cross-project static instructions under `core/`. `core/AGENTS.md` is the always-loaded core; `core/references/` contains low-frequency facts and tool boundaries.

**Guard** means `scripts/guard.py`, the single mechanical interface for deterministic configuration, architecture, Skill, and commit checks. It does not replace Agent judgement such as diff ownership or architectural intent.

**Runtime configuration view** means `~/.agents` and tool-specific files such as `~/.claude/CLAUDE.md`. These paths expose canonical source through links and are not edited as independent copies.

**Externally managed state** means files owned by another tool, including `~/.agents/skills/`, `.skill-lock.json`, MCP state, plugin state, caches, sessions, and similar generated configuration. It is not copied into this repository by default.

**Skill documentation** means the human-facing explanation in `docs/`. It is an index and guide, not a second copy of runtime rules.

**User-invoked skill** means a workflow deliberately started by the user. It sets `disable-model-invocation: true` and spends user cognitive load instead of model context load.

**Model-invoked skill** means a workflow the agent may select automatically. Its description must earn its permanent context cost with precise trigger branches.

**Stable skill** means a skill whose name, invocation boundary, process, and completion criteria are suitable for use outside this repository.

**In-progress skill** means a skill still being designed or tested. It is not listed as a stable capability.

**Deprecated skill** means a previously exposed skill retained only to explain replacement or migration.

**Native Word** means constructing DOCX through Word concepts—styles, paragraphs, sections, fields, tables, captions, pagination, and character formatting—rather than reproducing Markdown or web presentation patterns.

## Current boundary

The maintained stable capabilities are `engineering/devspace-orchestration`, `productivity/general-word-document-generation`, and `productivity/visible-browser-form-automation`.

The repository can be consumed locally by the `skills` CLI through `npx skills add <local-path>`. Static global configuration is deployed through `uv run scripts/install.py`, which links runtime entry points back to the canonical source without taking ownership of externally managed state. Deterministic checks are exposed through `uv run scripts/guard.py <command>`.

A public Git remote, semantic versioning, Changesets, marketplace packaging, CI validation, and licensing remain undecided. Do not infer those decisions from the upstream repositories used as structural inspiration.
