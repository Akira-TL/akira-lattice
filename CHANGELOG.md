# Changelog

All user-visible changes to stable skills will be documented in this file.

## Unreleased

### Added

- Initialized the `akira-skills` repository structure.
- Added the first productivity skill, `general-word-document-generation`.
- Added `visible-browser-form-automation` for WSL-to-Windows Chrome CDP automation, dynamic form inspection, human-visible review, upload handoff, and explicit pre-submit safety boundaries.
- 为 `browser-access` 增加可复用的 Chrome DevTools Protocol 控制 CLI，统一 Agent Chrome 生命周期、target 选择、DOM 操作、文件上传与网络观察，并要求优先复用该执行层而不是临时编写 WebSocket/CDP 包装脚本。
- Added separate runtime source, user documentation, lifecycle directories, repository instructions, and shared terminology.
- Documented local installation through `npx skills` for Codex, Claude Code, OpenCode, Hermes Agent, and other supported agents.
- Added canonical global static Agent configuration under `core/`, with on-demand references and runtime links.
- Added the harness-agnostic `agent-orchestration` Skill for mapping already-defined work units onto execution primitives actually provided by the current Agent harness, without making it a Parallel protocol dependency.
- Added `scientific-presentation-authoring` for structuring scientific presentations, writing evidence-bounded result slides, adapting reference-deck design rules without copying template content, and applying `humanizer-zh` to Chinese slide text.
- Added cross-platform `scripts/guard.py` and `scripts/install.py` entry points for static configuration deployment, architecture thresholds, Skill structure validation, and guarded Git commits.
- Added `core/references/matt-skills.md` to record ownership and upstream-merge rules for the maintained `Akira-TL/matt-skills` fork.
- Added `guard.py upstream matt` to fetch, compare and merge Matt upstream safely; explicit `--push` publishes our fork and commits the updated Lattice submodule pointer.
- Added root `install.sh` and `uninstall.sh` as the unified human-facing runtime installation/update and uninstall entry points.
- Added the official OpenAI `plugins` repository as a read-only third-party submodule and exposed only `ngs-analysis` through `~/.agents/external/ngs-analysis`, while Akira's own `research/ngs` Skill retains scientific routing and method authority.

### Changed

- 调整 Core 的用户可见回复规则：复杂任务允许先完整展开，但必须在末尾以独立“结论”收束当前最重要的新发现、状态变化、关键证据、需查看的产物路径与真正下一步；过程性记录和常规校验不再默认进入结论。
- 将多 Agent 执行边界改为 harness-agnostic：Parallel / Ask-Akira 不再依赖固定执行产品或执行器 Skill；Codex、Claude Code 或其他 harness 都只作为实现载体，具体子 Agent、进程、模型与 worktree 能力以当前工具契约为准。
- 将原环境绑定的多 Agent 执行 Skill 迁移为可选的 `agent-orchestration`，移除固定 CLI 与模型名称假设，并从 Core 必需运行时 Skill 检查中删除该执行层依赖。
- 收窄运行时安装职责：安装只建立或更新本项目的全局 Agent 配置软链接并安装当前 Akira/Matt Skills，不再自动清理旧 Skill、迁移历史备份、删除旧目录或修改 Matt remote；卸载由独立入口按项目所有权执行。
- 明确 Core 的发布 tag 可变性边界：仅推送 tag、尚未产生 GitHub Release、包仓库版本或其他不可撤回正式发布产物时，允许修复后删除并重建同名 tag、继续使用原版本号；正式发布后 tag 与版本内容才进入不可变状态。
- 将 Akira Guard 明确分成 Core 路由、`akira-guard` Skill 与 `scripts/guard.py` 执行层；`guard.py commit` 现在自动检查 staged Python/JSON/TOML 及可用解释器支持的 Shell/Node 语法，普通提交不再默认扩张为全量 lint/typecheck/build/test，重型验证仅用于大型、关键或高风险修改。
- 细化 Core 的 Git 提交节奏与回退语义：以“一次明确修改目的”作为默认原子提交单位，每个完成阶段立即提交而不等待用户确认；有先后依赖的状态变化必须通过独立提交保留真实顺序；用户明确否定当前 Agent 最近实现时，在 ownership 与工作树安全前提下先 reset 被否定提交，再重新实现，避免在已否定历史上继续叠加修正。
- 收紧独立 Agent 验收流程：需要黑盒验收、独立复核或最终 Agent 验收时，当前 Agent 不再自行启动验收 Agent，而是先向用户提供完整可复制的验收提示词，由用户新开独立会话执行；当前 Agent 仅在用户回传结果后负责审计、归因和修复。
- 扩展 Core 的本地上下文读取边界：仅在确需本机系统、服务部署、端口、反向代理或开发环境信息时，允许按既有路由读取 `~/.config/akira/`，无关任务仍禁止读取。
- 收紧 Core 的中英文与专业学术表述规范：面向用户的自然语言以中文为主体，专业术语首次出现默认采用“规范中文名（English Full Term, ACRONYM）”格式，后续仅使用规范中文名或公认缩写并保持权威来源规定的拼写与大小写；专有名词、程序、命令、工具、库、框架、产品、项目及技术字面量按官方原名保留，禁止为中文化强行直译；同时继续禁止自造术语、缩写、分类名或概念名。
- Made `ask-akira-research` legacy Analysis provenance reads schema-aware: `research-db analyses` now reads v13/v14 projects without touching later-only fields and reports unavailable provenance dimensions through `schema_capabilities` instead of leaking low-level SQLite row errors.
- Renamed `visible-browser-form-automation` to `browser-access` and generalized it into a harness-first browser access layer with one-time user-browser authorization, persistent Profile reuse, authenticated page access, network resource resolution, and the existing dynamic-form safety behavior.
- Clarified the color boundary in `general-word-document-generation`: inserted images may retain color, while tables, text, shapes, borders, and other Word-native non-image content remain limited to black, white, and necessary grayscale unless the user explicitly requests color.
- Rebalanced global Agent configuration: short stable engineering defaults stay in the Core, large procedures stay in Skills, low-frequency facts stay in references, and mechanically decidable rules move to the Guard.
- 为 Akira 的本地长期上下文增加按资料域路由：基础资料、学术履历、项目经历和系统配置分别按需加载，不再继续堆叠到单一用户资料中。
- Renamed the static configuration source from `context/` to `core/` so project context remains exclusively owned by the Matt flow and future dynamic context/Memory remains reserved for `contextd`.
- Changed Claude, Codex, OpenCode, and the generic Agent prompt entry points to direct symlinks from their native prompt filenames to `core/AGENTS.md`, eliminating intermediate prompt forwarding.
- Standardized Git submission on `guard.py commit`: agents may selectively stage with `git add -- <paths...>`, but normal commits go through the Guard; documented that an Agent harness or tool contract may impose stricter shell constraints than the repository itself.
- Made the per-turn Git development cadence explicit in Core: decide whether the previous atomic change should be committed, plan the next change, implement, run minimum syntax checks, show all local branches/worktrees, then optionally surface broader build or check commands.
- Centralized installer-created Agent configuration backups under the Git-ignored `backup/` mirror tree and migrate legacy adjacent backups from managed prompt paths.
- Changed Matt-derived runtime Skills to install from the `skills/matt` Git submodule, whose `origin` is the maintained `Akira-TL/matt-skills` fork while Matt's repository remains fetch-only `upstream`; Guard now verifies this ownership boundary.
- Split Akira-authored Skills into the independent `Akira-TL/skills` repository and mount it at `skills/akira`, leaving Lattice to pin both self-authored and Matt-derived Skill repositories as separate submodules.
- Moved Akira Skill user documentation into `skills/akira/docs/`, so Skill source and its documentation now share one independent repository and Lattice no longer keeps duplicate Skill docs.
