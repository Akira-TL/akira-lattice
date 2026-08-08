# DevSpace 与 worktree 参考

仅在需要确认 DevSpace workspace 或 Git worktree 边界时读取本文。多 Agent 的具体执行流程由 `devspace-orchestration` Skill 负责。

## workspace

- `workspaceId` 只是当前 DevSpace 工具会话的句柄，不是持久项目 ID。
- 普通任务使用 `checkout` 打开实际项目目录或已有 worktree。
- 同一个实际目录再次以 `checkout` 打开仍是磁盘上的同一份代码，即使新会话获得不同 `workspaceId`。

## Git 与 MCP 宿主

- DevSpace 的 shell 能力应允许标准 Git 操作，包括 `git status`、`git diff`、`git add -- <paths...>`、分支和 worktree 管理等；Agent 在暂存前仍必须先检查 diff ownership，只加入当前原子修改。
- 某些 GPT / MCP 宿主会在工具描述中额外限制 shell 为 “git inspection only”。这是宿主提示词或 MCP 工具契约施加的模型侧限制，不代表 DevSpace 或本机 Git 本身缺少写能力；遇到此情况不得把限制误判为仓库权限问题，也不得偷偷绕过，应调整对应 DevSpace/MCP 工具契约后再执行。
- DevSpace 技术上可以执行 `git commit`，但日常不建议直接使用。全局 Core 规定正式提交统一走 `uv run ~/.agents/scripts/guard.py commit -m '<message>'`，以确保提交格式和 staged architecture 经过同一机械入口检查。

## worktree

- 需要隔离或并行开发时，可用 `mode="worktree"` 在 `~/.devspace/worktrees/` 创建 DevSpace 托管的 Git worktree。
- 对同一主仓库再次使用 `mode="worktree"` 可能创建新的隔离 worktree；继续已有任务时，应以 `checkout` 直接打开已有 worktree 的实际路径。
- DevSpace worktree 是标准 Git linked worktree：与主仓库共享对象数据库、分支和提交，但工作目录不会自动同步、合并、cherry-pick 或推送。
- 不得把 worktree 嵌套在主项目 checkout 内。

## 移动与删除

移动主仓库或 worktree 后，如路径引用失效，应从仍可访问的仓库执行：

```bash
git worktree repair <worktree-path>
git worktree list
```

删除主仓库与移动主仓库不同。主仓库的 `.git` 对象数据库被删除后，linked worktree 不能作为完整独立仓库继续使用。移动或删除项目前，应先检查全部 worktree，并处理未提交修改、推送、移除或修复工作树。
