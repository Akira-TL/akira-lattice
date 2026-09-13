# ADR 0002：按能力内聚性拆分 Skill 仓库

## Status

Accepted；其中 Skill 安装 ownership 已由 ADR 0003 取代。

## Context

原 `Akira-TL/skills` 同时承载通用生产力能力、工程扩展和完整 Akira Research。随着 Research 引入 Research Tree、`research.sqlite`、schema migration、Analysis Attempt、Literature、Interpretation 与 Communication 等共享契约，单一 Skill 仓逐渐同时承担多个产品域，导致项目安装粒度、维护边界和 Agent 理解成本不再一致。

另一方面，并非所有能力都适合继续拆分。浏览器、Word、科研/学术 PPT、Guard 语义和 harness-agnostic Agent 编排具有明显跨领域复用价值；`ask-akira` 与 Parallel 系列则直接包裹 Matt 的 Spec/Ticket/implement/TDD/code-review 流程，若脱离 Matt fork 独立发布会制造第二套工程产品边界。

## Decision

- `Akira-TL/skills` 保留为 **Akira 通用 Skill 仓**，而不是纯空壳 Router。它拥有：
  - `akira` 跨仓库能力 Router；
  - `browser-access`；
  - `general-word-document-generation`；
  - `scientific-presentation-authoring`；
  - `akira-guard`；
  - `agent-orchestration`。
- Akira Research 独立为 `Akira-TL/akira-research-skills`。Research suite 内部继续共同拥有 Research Tree、科研对象契约、`research.sqlite`、schema migration、Literature、Design、Study、Data、Analysis、Interpretation 与 Communication。
- `Akira-TL/matt-skills` 继续作为单独的 Matt fork，并同时拥有直接扩展 Matt 方法论的 Akira 工程增量：`ask-akira`、`parallel-coordinator` 与 `parallel-execution`。这些扩展保持 `in-progress` 生命周期，不因为迁仓自动升级为稳定能力。
- 不建立独立 `akira-engineering-skills` 或 `akira-productivity-skills`。
- Knowledge 只有在形成真实、高内聚工作流后才建立独立仓库；不预先维护空产品。
- Lattice 可以 pin 多个 Skill source，但 **pin 不等于全局安装**。
- Lattice 默认全局只安装最小跨域基线：`akira` Router 与 `browser-access`。Matt、Research、Word、PPT、Agent 编排等由 Router 根据当前项目真实需求，在用户明确同意后项目级安装。

## Consequences

- 科研项目可以只安装 Research suite，而不把 Matt 或全部通用交付 Skill 带入项目。
- 软件工程项目安装 Matt fork 即可同时获得 Matt 主流程以及 Akira 的特殊执行模式 / Parallel 协作扩展，不需要额外 Engineering 产品仓。
- 通用仓仍有实际能力价值；Router 可以优先补一个单一通用 Skill，而不是任何缺口都升级成整仓安装。
- 全局运行时保持较小，降低 Skill trigger 噪声；项目级 `skills-lock.json` 更接近项目真实用途。
- 旧运行时中历史上全局安装的 Matt / Research / 其他 Skill 不由新版安装器静默清理；一次性迁移必须显式执行并遵守现有安装 ownership manifest。
- Lattice Guard 需要同时理解通用仓的分类目录结构，以及 Research suite 的 `skills/<category>/<skill>/` + `docs/<category>/<skill>.md` 镜像结构。
- 第三方 Skill 仓库不作为 Lattice submodule 固定；Router 只维护可信来源、发现方式与项目级最小安装边界。
