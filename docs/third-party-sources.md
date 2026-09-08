# 第三方 Skill / Plugin 来源

本文件记录由 Akira Lattice 固定、但不属于 Akira 自研 Skill 正文的第三方 Agent 能力源码。第三方源码保持独立 Git history 与 ownership；Akira 只在自身 Skill 中维护适配、路由和覆盖规则。

## OpenAI plugins / ngs-analysis

```text
Repository: https://github.com/openai/plugins.git
Submodule: skills/openai-plugins
Plugin: plugins/ngs-analysis
Initial pinned commit: 1e285826e604f66f7208f7ac4dba0fe8341d1f57
Plugin version at initial pin: 1.0.3
Author: OpenAI
Declared license: MIT
Runtime source view: ~/.agents/external/ngs-analysis
```

官方源码的 `.codex-plugin/plugin.json` 是 plugin identity、version 与 license 声明的直接来源。Lattice 不把其中 `skills/` 正文复制进 `skills/akira`，也不把这些 upstream Skill 作为独立全局 Skill 自动安装。

Akira 自研 `research/ngs` 负责科研语义适配：`study` 继续拥有真实建库/测序实施，`data` 拥有 Dataset identity、QC/exclusion 与 freeze，`analysis` 拥有 estimand、统计方法、contrast 与 sensitivity，`interpretation` 拥有科学 Claim。OpenAI `ngs-analysis` 主要提供 assay-specific guidance、runner、preflight、reference/database/resource gate 与 run envelope。

更新第三方版本时应显式检查 upstream diff、plugin version、runner/registry 变化和 Akira adapter compatibility，再提交新的 submodule pointer；不得让运行时 source 自动跟随 upstream `main` 漂移。第三方 submodule 的 push URL 在本机安装/检查流程中设为 `DISABLED`，避免误向 upstream 写入。
