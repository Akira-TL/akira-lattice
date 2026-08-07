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

`visible-browser-form-automation`：让 Agent 在 WSL 等自动化环境中通过 CDP 控制用户可见的 Windows Chrome，适合问卷、报销、申请和报名表等需要“自动填写、人工复核、明确确认后再提交”的工作流。

## Install with npx skills

在本仓库根目录可以直接安装本地 Skill。例如安装可视化表单自动化 Skill 到 Codex：

```bash
npx skills add . --skill visible-browser-form-automation --agent codex -g -y
```

同时安装到多个 Agent：

```bash
npx skills add . \
  --skill visible-browser-form-automation \
  -g \
  -a codex \
  -a claude-code \
  -a opencode \
  -a hermes-agent \
  -y
```

安装到 CLI 检测到的所有 Agent：

```bash
npx skills add . --skill visible-browser-form-automation --agent '*' -g -y
```

查看仓库中可安装的 Skill：

```bash
npx skills add . --list
```

当前仓库尚未配置 Git remote，因此现在使用本地路径最可靠。发布到 GitHub 后，可把 `.` 替换为 `<owner>/akira-skills` 或完整 GitHub URL。

## Status

仓库当前处于初始化阶段。许可证、自动校验、Changesets 和正式远程发布仍将在需求明确后分别决策；本地 `npx skills` 安装已经可用。
