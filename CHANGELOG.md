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

### Changed

- 收紧 Core 的语言与 Git ownership 判断：凡自然语言中出现英文术语都先按可核验的规范名称处理；提交前遇到此前会话、其他 Agent、用户或来源不明的修改时，先判断是否属于当前接手文件或已确认工作内容，只有无法确认归属时才提醒用户。
- 按能力内聚性重构 Akira Skill source：完整 Research 工作流独立到 `Akira-TL/akira-research-skills`；`Akira-TL/skills` 保留 `akira` Router、浏览器、Word、科研/学术 PPT、Guard 与通用 Agent 编排；`ask-akira`、`parallel-coordinator`、`parallel-execution` 回归 `Akira-TL/matt-skills` fork，作为 Matt 工程流程的 in-progress 扩展。Lattice 以后区分“submodule pin”与“运行时安装”：ForgeRelay 只常驻 `akira` 与 `browser-access`，由 `npx skills` 管理在 `~/.forgerelay/skills/`；Matt / Research / 其他通用 Skill 由 Router 按项目真实需求并经用户同意后项目级安装。
- 移除 Lattice 对 OpenAI `plugins` 仓库与固定 `ngs-analysis` source view 的 submodule 管理；OpenAI Plugins 改由 `akira` Router 作为外部能力来源按当前清单发现，只有具体任务需要且用户同意时才项目级安装对应 Skill。

- 重构 Akira Research 的 Git-native 科研工作流：`main` 固定为已接受的 canonical research state，真实科研路线使用 `research/<kind>/<slug>` 分支并以保留拓扑 merge 或 annotated archival tag 收口；Analysis 新增由 Git commit 固定的独立 Attempt、`src/` 公共实现与 `scripts/analyses/` 执行入口隔离，默认采用 Python 完成统计/数据处理并由 R 独立消费结果表绘图；项目初始化写入针对机器 artifact、可重建输出和人类 convenience PDF 的 `.gitignore`。同时将人类文献区稳定为 `literature/papers/` + `collections/`，不再用 `to-read/read` 文件移动表达状态，并为阅读 Markdown 增加顶部/结尾同一状态的“我已阅读并确认当前版本”复选框及 Git content OID 版本确认 provenance。
- 扩展 Akira Research 的论文阅读协议：先按背景知识构建、前沿跟踪、方法学习、研究设计学习、证据核验或写作结构学习选择章节顺序；研究设计与方法阅读主动追踪基础工作、代表实现、后续改进和边界条件，并把被引次数、发表时间与引文网络连接度降级为发现/排序信号。人类阅读 Markdown 新增“关键图表与定位”和 `akira:user-notes` 用户专属区；Agent 不修改该区内容，用户补写自己的笔记也不会改变阅读确认的 content OID。
- 固定 Akira Research 人类论文笔记格式：新 sidecar 使用 `akira:literature-note:v1`，以原始论文题名、固定书目信息表和固定顺序的二级标题构成稳定阅读骨架；三级标题仍按论文类型自由展开，用户笔记区内标题不参与门禁。completion 只机械检查结构，不以字数、实验数或图表数制造内容填充；历史旧格式 sidecar 保持兼容。
- 扩展 Akira Research 的原始研究论文写作流程：长篇 research manuscript / thesis 先完整盘点写作材料，再按“主要结论 → Results → Discussion → 反推 Introduction → Methods → Abstract / Title → Supplement / Appendix”起草；Results 先用小标题与 Figure / Table 搭骨架并要求层层递进，Introduction 与 Results / Discussion / Conclusion 做首尾闭环。材料可以分配到主文、Supplement、Appendix 或 canonical support，但不得因不利于预期故事而静默遗漏；同时新增科研逻辑连接词、结论强度与术语一致性的受控表达参考。
- 为 Akira Research 的 Communication 增加写作类型路由：长篇正文开始前先区分原始研究论文、普通叙述性综述和系统综述/范围综述/荟萃分析；普通综述按 Review Question / Scope、材料盘点、问题导向组织、跨论文综合、真实研究缺口与 future direction 组织，不再套用原始研究论文的 Results / Discussion 流程，也不再默认要求新建 conceptual framework / taxonomy。正式证据综合研究若检索、筛选、质量评价、数据提取与综合 provenance 未完成，则返回科研流程而不是直接写稿。
- 重构 Akira Research 的长篇科研写作生成纪律：正文前先明确贡献来自经验性发现、方法、resource、evidence synthesis 还是概念本身，建立稿件术语表，并按“读者问题 → evidence → 最窄结论”组织 section / paragraph；新命名必须先核验已有术语、证明命名本身有贡献必要性、给出可操作定义并获得用户明确批准。新增生物学与生物信息学的原始研究 / 普通综述叠加层，并把写作参考收敛为 `REFERENCE.md`：只维护已核验 DOI 与阅读入口，每次开始或重新开始长篇正文前实际打开 1 篇通用结构参考和 2 篇同类型已发表论文，直接从原论文观察 section / paragraph 用语与推进方式，不复制原句，也不把 writing reference 当科学证据。
- 增加外部科研 Skill 按需使用协议：K-Dense Scientific Agent Skills 不作为 submodule 或全局默认依赖，只在当前科研任务确实需要具体专业工具、数据库或软件知识时审计单个 Skill 的来源、revision、license、脚本/网络/凭据和职责边界，再征得用户同意后用当前项目的 `.agents/skills/` 与 `skills-lock.json` 做项目级安装；第三方 Skill 只补执行知识，不接管 Akira 的科研决策与 provenance。
- 吸收可量化迭代实验的受控执行思想到 Analysis Attempt：存在稳定机械指标时，结果前固定 baseline、metric、方向、target 与 guard，每个 Attempt 只做一个主要可解释变化，并保留改善、未改善和 invalid 路线；机械 target 不替代 scientific validity，外部 controller 不接管科研 Git 历史。
- 加强 Communication 的完整性与修订审计：长篇 draft 在 reviewer-style review 前检查高风险 Claim↔source、citation support、数字/统计与 scope，实质 revision 后再做最终 drift 审查；reviewer response 按意见—验收标准—真实修改 artifact 闭环，默认先独立核验 revised manuscript / analysis / figure，再读取 response letter，避免“作者说已完成”替代可检查证据，同时加入 reverse outlining 检查 section thesis、段落主信息与 evidence 的映射。
- 继续收紧 Communication 的最终交付边界：最终 PDF / DOCX / PPTX 必须基于真实渲染页面做排版 QA；多视角 reviewer-style 自审只有在真实上下文隔离时才称独立审查，concern 同时区分最低诚实修复、更强补强方案与无可写作性补救；Title / Abstract / Highlights 等压缩表面不得删掉会改变 Claim 真值或 scope 的限定；显微图、gel/blot、医学影像等原始科研图像必须保留处理 provenance，并禁止 clone、healing、generative fill、选择性 erase 或未披露拼接改变 evidence。
- 加强 Literature 的反确认偏差与跨框架综合：当前 Active Uncertainty 已有主要判断时主动执行以推翻或限定它为目标的反证检索，真实记录 negative/null result、失败复现、边界条件、方法批评及零命中边界；跨学科综合先核对 construct、measurement、unit、population、time 与 inference target 的可比性，不可通约的证据框架并列保留，禁止制造假共识或假冲突。
- 明确受监管科研与预注册的 authority boundary：规范内容与项目适用性分开，`unknown` 不得静默变成 `not applicable`，exemption route 不等于已获豁免，多 jurisdiction / institution / funder 冲突不由 Agent 私自裁决；Akira 的结果前 Git / Design freeze 只证明内部版本冻结，不得冒充外部 preregistration、trial registration、protocol registration 或 Registered Report acceptance。
- 将第三方科研 Skill 审计升级为多轮吸收记录：为 `codex-autoresearch`、`nature-skills`、`academic-research-skills` 与 K-Dense 按需来源明确 Akira owner、已吸收方法、拒绝项和复审触发条件；固定证据金字塔、A–F 总评分、论文/数据库数量配额、固定 revision 轮次、第三方状态机与期刊专属模板继续拒绝进入 Akira 全局科研规则。
- 为 `research-tree` 增加模糊 Idea 收敛协议：当用户只有宽泛主题或现象兴趣时，不直接生成漂亮 Research Question，而是只追问会改变科研路线的研究对象、科学目标、关键未知、competing explanations、现实边界和判别性 evidence；必要时先用低成本 Literature Discovery 建立问题空间，再进入正式 Research Tree。
- 严格化 Akira Research 的核心人类可读层：Hypothesis、Design、Study、Dataset、Analysis 与 Interpretation 统一采用 owner-defined 固定 Markdown 结构和相对导航；目录索引固定提供 `Objects` 与 `Relations` 入口，completion 机械校验已知上下游关系、断链和 `.research/` 人机边界；Hypothesis / Design 在首次冻结前先完成格式与学术语言检查，历史冻结 artifact 仅在真实迁移基线且迁移后未修改时保留旧格式。
- 为 Communication 增加学科 / 目标 Venue 叠加层：先由 Document Type 决定原始研究、综述、证据综合或 Proposal 的科学写作流程，再按目标 discipline / audience / journal / conference 调整表达与审查重点；Venue 具体要求继续从当前官方 Author Instructions / reporting guideline 核验，不能反向改变 canonical evidence。
- 重构 Akira Research 的 Communication 工作区边界：`communication/<product-slug>/` 固定为人类传播视图，`.research/communication/<product-slug>/` 保存审计、追溯、验证与材料盘点等内部支持 artifact，生成/验证代码继续位于正常代码区；completion gate 同时检查两类传播目录、阻止顶层平铺和跨 Product 混放，并新增 `research-db relocate-communication-artifact`，用于在真实文件迁移后受控同步既有 artifact path，而不改写 role、timing 或 pre-communication source freeze。
- 将 Akira Research 的论文 Communication 草稿固定为 venue-neutral canonical source；只有进入真实目标期刊准备时才登记稳定期刊短代码并建立 `<journal-code>-release/` target workspace，其中只保存 manifest、配置、build/template source 与 QA 依据。DOCX/XLSX/PDF 以及被声明为生成物的 LaTeX 不作为可编辑 authority，completion 同时校验 journal registry、workspace identity、canonical source 与 build source drift，并阻止 target workspace 内出现第二份独立稿件。
- 为 Akira Research 的正式稿件增加不可变 annotated Git tag：每个 `(article, journal)` lineage 采用 `1.0 → 1.1 → …` 两段版本，新的整数 baseline 需要用户批准或显式项目决定；真实公开后才允许同 commit 的 `release-YYYYMMDD`。Tag 创建前会在临时输出目录实际重放 target build 并核验声明输出，成功创建后 completion 反查 tag object/commit，禁止移动、lightweight 重建、删除复用、非法序列和无公开依据的 release。
- 为上述 Research 人类阅读与论文发布链增加自动化端到端系统黑盒：隔离项目必须从 `RESEARCH.md` 与完整 Research Tree 可点击进入核心科研对象，保持并列假设为同根 sibling，并完整走通 venue-neutral manuscript、目标期刊 workspace、可重放 build、`1.0 → 1.1` checkpoint、真实公开 release 及非法 `final`/生成物漂移的 fail-closed 检查。
- 统一 Akira Research 的 Literature 人类阅读格式：单篇论文 note 改用无版本号的 `akira:literature-note` 类型标记，`literature/README.md` 与 Collection 使用固定可跳转结构，并机械校验论文文件命名、同名 PDF、本地链接和完整索引；旧 marker 仅在 schema migration 中确定性替换，历史正文和用户笔记保持不变。
- 为 Literature 增加长期文献监测（Living Literature Monitoring）：围绕 Research Question / Active Uncertainty 保存周期性 update search，并复用既有 Search Run、Candidate、Paper、去重和 Evidence Gate；普通新增默认静默，只有新的 contradiction、boundary、method、replication、guideline 等会改变科研判断的变化才主动通知，当前 harness 没有 scheduler 时不伪装后台持续运行。
- 增加 Zotero 推荐阅读出口：默认把 `core/high + relevant` 文献导向 `Akira Recommended Reading` collection，使用 Zotero 10+ 官方 Local API 时限制为单次 probe、每次调用最多一次授权请求，并保守去重已有 DOI / title-year；Local API 不可达、未启用、用户拒绝或 WSL/Windows 网络不通时立即生成标准 RIS fallback，不扫描端口、不做 GUI 自动化、不写 `zotero.sqlite`，且不接管用户自己的 Zotero 分类体系。
- 调整 Core 的用户可见回复规则：复杂任务允许先完整展开，但必须在末尾以独立“结论”收束当前最重要的新发现、状态变化、关键证据、需查看的产物路径与真正下一步；过程性记录和常规校验不再默认进入结论。
- 将多 Agent 执行边界改为 harness-agnostic：Parallel / Ask-Akira 不再依赖固定执行产品或执行器 Skill；Codex、Claude Code 或其他 harness 都只作为实现载体，具体子 Agent、进程、模型与 worktree 能力以当前工具契约为准。
- 将原环境绑定的多 Agent 执行 Skill 迁移为可选的 `agent-orchestration`，移除固定 CLI 与模型名称假设，并从 Core 必需运行时 Skill 检查中删除该执行层依赖。
- 收窄运行时安装职责：安装只建立或更新本项目的静态 Agent 配置软链接，并通过 `npx skills` 在 `~/.forgerelay/skills/` 维护 `akira` + `browser-access` 两个 ForgeRelay 常驻基线；不再管理 `~/.agents/skills/`，也不常驻安装 Matt、Research、Word、PPT 或 Agent 编排。卸载由独立入口按 manifest 与内容哈希判断所有权。
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
