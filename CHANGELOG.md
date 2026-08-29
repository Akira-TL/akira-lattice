# Changelog

All user-visible changes to stable skills will be documented in this file.

## Unreleased

### Added

- Initialized the `akira-skills` repository structure.
- Added the first productivity skill, `general-word-document-generation`.
- Added `visible-browser-form-automation` for WSL-to-Windows Chrome CDP automation, dynamic form inspection, human-visible review, upload handoff, and explicit pre-submit safety boundaries.
- Added separate runtime source, user documentation, lifecycle directories, repository instructions, and shared terminology.
- Documented local installation through `npx skills` for Codex, Claude Code, OpenCode, Hermes Agent, and other supported agents.
- Added canonical global static Agent configuration under `core/`, with on-demand references and runtime links.
- Added `devspace-orchestration` for choosing Claude native Agent, tmux, and Git worktree isolation in multi-Agent DevSpace tasks.
- Added `scientific-presentation-authoring` for structuring scientific presentations, writing evidence-bounded result slides, adapting reference-deck design rules without copying template content, and applying `humanizer-zh` to Chinese slide text.
- Added cross-platform `scripts/guard.py` and `scripts/install.py` entry points for static configuration deployment, architecture thresholds, Skill structure validation, and guarded Git commits.
- Added `core/references/matt-skills.md` to record ownership and upstream-merge rules for the maintained `Akira-TL/matt-skills` fork.
- Added `guard.py upstream matt` to fetch, compare and merge Matt upstream safely; explicit `--push` publishes our fork and commits the updated Lattice submodule pointer.

### Changed

- 收紧 Core 的专业与学术表述规范：专业术语首次出现默认采用“规范中文名（English Full Term, ACRONYM）”格式，术语与缩写须能由严谨专业来源核验；禁止自造术语、缩写、分类名或概念名，新的概念与命名须先经用户明确同意。
- Made `ask-akira-research` legacy Analysis provenance reads schema-aware: `research-db analyses` now reads v13/v14 projects without touching later-only fields and reports unavailable provenance dimensions through `schema_capabilities` instead of leaking low-level SQLite row errors.
- Renamed `visible-browser-form-automation` to `browser-access` and generalized it into a harness-first browser access layer with one-time user-browser authorization, persistent Profile reuse, authenticated page access, network resource resolution, and the existing dynamic-form safety behavior.
- Clarified the color boundary in `general-word-document-generation`: inserted images may retain color, while tables, text, shapes, borders, and other Word-native non-image content remain limited to black, white, and necessary grayscale unless the user explicitly requests color.
- Rebalanced global Agent configuration: short stable engineering defaults stay in the Core, large procedures stay in Skills, low-frequency facts stay in references, and mechanically decidable rules move to the Guard.
- 为 Akira 的本地长期上下文增加按资料域路由：基础资料、学术履历、项目经历和系统配置分别按需加载，不再继续堆叠到单一用户资料中。
- Renamed the static configuration source from `context/` to `core/` so project context remains exclusively owned by the Matt flow and future dynamic context/Memory remains reserved for `contextd`.
- Changed Claude, Codex, OpenCode, and the generic Agent prompt entry points to direct symlinks from their native prompt filenames to `core/AGENTS.md`, eliminating intermediate prompt forwarding.
- Standardized Git submission on `guard.py commit`: agents may selectively stage with `git add -- <paths...>`, but normal commits go through the Guard; documented that GPT/MCP hosts may impose stricter shell constraints than DevSpace itself.
- Made the per-turn Git development cadence explicit in Core: decide whether the previous atomic change should be committed, plan the next change, implement, run minimum syntax checks, show all local branches/worktrees, then optionally surface broader build or check commands.
- Centralized installer-created Agent configuration backups under the Git-ignored `backup/` mirror tree and migrate legacy adjacent backups from managed prompt paths.
- Changed Matt-derived runtime Skills to install from the `skills/matt` Git submodule, whose `origin` is the maintained `Akira-TL/matt-skills` fork while Matt's repository remains fetch-only `upstream`; Guard now verifies this ownership boundary.
- Split Akira-authored Skills into the independent `Akira-TL/skills` repository and mount it at `skills/akira`, leaving Lattice to pin both self-authored and Matt-derived Skill repositories as separate submodules.
- Moved Akira Skill user documentation into `skills/akira/docs/`, so Skill source and its documentation now share one independent repository and Lattice no longer keeps duplicate Skill docs.
