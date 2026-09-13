# 第三方 Skill 来源

Akira Lattice 不再把第三方 Skill 仓库作为 submodule 固定。

外部来源、发现方式和安装边界由 `skills/akira/routing/akira/references/EXTERNAL-SOURCES.md` 维护。需要外部能力时，`akira` Router 查询当前 Skill 清单，只推荐与任务相关的候选，并在用户同意后进行项目级安装。

## OpenAI Plugins

OpenAI 官方 `openai/plugins` 是登记来源之一，但不属于 Akira 仓库。Akira Research 的 `ngs` 可以按需使用其中的 NGS 能力；Research 仍负责科研状态、分析身份和证据边界。

历史上 Lattice 曾固定该仓库；现在不再把它作为 Research 的安装前提。
