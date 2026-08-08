# Akira Skills

Akira 的个人 Agent 能力与静态配置仓库。这里维护可组合、可检查、可迭代的 Skill，以及跨项目长期生效的全局工程默认；本地 Agent 目录只作为运行时入口，不再维护第二份正文。

仓库保持单一 canonical source：短小稳定规则常驻 Core，大型流程进入 Skill，低频事实进入 Reference，可机械判断的约束进入 Python Guard。项目知识由 Matt flow 管理，动态上下文与 Memory 不在本仓库处理。

## Repository layout

```text
akira-skills/
├── core/                   # 个人全局静态 Agent 配置 canonical source
│   ├── AGENTS.md           # 每次会话加载的 Core
│   └── references/         # 低频事实与工具边界
├── scripts/                # Python Guard 与运行时安装
├── skills/                 # Agent 实际读取的 Skill 源码
│   ├── productivity/       # 通用生产力与文档工作流
│   ├── in-progress/        # 尚未稳定、不可作为正式能力发布
│   └── deprecated/         # 已弃用但暂时保留迁移说明的 Skill
├── docs/                   # 面向使用者的说明
├── .agents/adr/            # 影响仓库长期维护的架构决策
├── AGENTS.md               # Agent 在本仓库中的维护规则
├── CONTEXT.md              # 仓库术语与边界
└── CHANGELOG.md            # 面向使用者的变更记录
```

## Global static configuration

`core/AGENTS.md` 是全局提示词唯一源码。运行：

```bash
uv run scripts/install.py
```

会将 `~/.agents/AGENTS.md`、Claude、Codex、OpenCode 等入口软链接回该源码，并保留 `~/.agents/skills/`、`.skill-lock.json` 等由外部工具管理的状态；Core 直接引用的仓库自有 Skill 会通过 `npx skills` 安装，不绕过 skills CLI。使用统一 Python Guard 检查配置：

```bash
uv run scripts/guard.py config
```

日常项目也可直接调用 `uv run ~/.agents/scripts/guard.py architecture`、`commit` 或 `check`，无需为每个项目单独安装 Git hook。完整设计见 `docs/agent-config.md`。

## Current skills

### Engineering

`devspace-orchestration`：在 DevSpace 中按任务长度、依赖关系和写入范围选择 Claude 原生 Agent、tmux 与 Git worktree，并由父 Agent 统一验收与清理。Core 会引用该 Skill，因此部署后应通过 skills CLI 安装到运行时。

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
