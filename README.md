# Akira Skills

Akira 的个人 Agent Skill 仓库。这里维护的是可组合、可检查、可迭代的工作流，而不是一组彼此孤立的长提示词。

仓库借鉴 `mattpocock/skills` 的管理思路：Skill 源码与面向用户的说明分离，按领域组织，并明确区分稳定、开发中和弃用状态。具体 Skill 内容由本仓库独立设计，不直接复制上游实现。

## Repository layout

```text
akira-skills/
├── skills/                 # Agent 实际读取的 Skill 源码
│   ├── productivity/       # 通用生产力与文档工作流
│   ├── in-progress/        # 尚未稳定、不可作为正式能力发布
│   └── deprecated/         # 已弃用但暂时保留迁移说明的 Skill
├── docs/                   # 面向使用者的说明，不作为 Skill 执行正文
├── .agents/adr/            # 影响仓库长期维护的架构决策
├── AGENTS.md               # Agent 在本仓库中的维护规则
├── CONTEXT.md              # 仓库术语与边界
└── CHANGELOG.md            # 面向使用者的变更记录
```

## Current skills

### Productivity

`general-word-document-generation`：从空白 DOCX 生成正式、克制、可打印的 Word 文档，按 Word 原生样式、段落、分页、表格、题注和字符级格式组织内容，避免 Markdown 视觉习惯污染成品。

## Status

仓库当前处于初始化阶段。发布方式、许可证、自动校验、Changesets 和 Agent 插件分发将在需求明确后分别决策，不在初始化阶段预设。
