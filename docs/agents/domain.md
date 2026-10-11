# 领域文档约定

## 阅读顺序

理解项目或定位修改边界前，先读取根目录 `CONTEXT.md`，再读取与当前主题有关的架构决策记录（Architecture Decision Record, ADR）。

本仓库使用根目录单一上下文；子仓库保留各自的上下文与决策归属。固定多个技能子仓库不意味着另建根目录多上下文布局。进入子仓库修改时，还应遵守其 Agent 指令及相关文档。

若后续明确采用 `CONTEXT-MAP.md`，先读取该索引，再读取当前主题涉及的上下文。上下文或相关决策文档不存在时直接继续，不提前要求创建；通过 `domain-modeling` 在术语或决策真正确定后按需记录。

## 现有 ADR 约定

权威目录为根目录 `.agents/adr/`，约定见 `.agents/adr/README.md`。保留现有顺序编号与 `NNNN-short-decision-title.md` 命名方式；记录包含背景、决策、后果和状态。适用于难以撤回或影响多个技能的决定，例如调用方式、分发、版本、许可证、验证和仓库级命名。

不另建并行的 `docs/adr/`，不把子仓库拥有的技能设计正文复制到 Lattice。

当前结构：

```text
CONTEXT.md
.agents/adr/
  README.md
  NNNN-short-decision-title.md
docs/agents/
  issue-tracker.md
  triage-labels.md
  domain.md
```

## 使用已确定的术语

领域概念遵循 `CONTEXT.md` 中的含义，不随意改写为语义不同的近义词。用户可见说明用中文；首次需要对应项目原文时附原名称，必须逐字匹配的路径、命令和代码标识符保留原文。

只有已确定且反复使用的领域概念进入上下文。未知概念交由 `domain-modeling` 判断，不将一般基础设施词汇或临时实现步骤加入术语表。

## 决策冲突

拟议修改与现有 ADR 冲突时，明确指出相关记录、冲突内容及重新讨论的理由，不默默覆盖既有决定。
