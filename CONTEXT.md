# Repository context

## Purpose

`akira-skills` is Akira's maintained collection of reusable agent workflows. It is a source repository, not an installation directory and not a dump of prompts copied from local agent configurations.

## Ubiquitous language

**Skill source** means the runtime instructions an agent loads. It lives in `skills/` and is authoritative for behavior.

**Skill documentation** means the human-facing explanation in `docs/`. It is an index and guide, not a second copy of runtime rules.

**User-invoked skill** means a workflow deliberately started by the user. It sets `disable-model-invocation: true` and spends user cognitive load instead of model context load.

**Model-invoked skill** means a workflow the agent may select automatically. Its description must earn its permanent context cost with precise trigger branches.

**Stable skill** means a skill whose name, invocation boundary, process, and completion criteria are suitable for use outside this repository.

**In-progress skill** means a skill still being designed or tested. It is not listed as a stable capability.

**Deprecated skill** means a previously exposed skill retained only to explain replacement or migration.

**Native Word** means constructing DOCX through Word concepts—styles, paragraphs, sections, fields, tables, captions, pagination, and character formatting—rather than reproducing Markdown or web presentation patterns.

## Current boundary

The maintained stable capabilities under `productivity` are `general-word-document-generation` and `visible-browser-form-automation`.

The repository can be consumed locally by the `skills` CLI through `npx skills add <local-path>`. A public Git remote, semantic versioning, Changesets, marketplace packaging, CI validation, and licensing remain undecided. Do not infer those decisions from the upstream repository used as structural inspiration.
