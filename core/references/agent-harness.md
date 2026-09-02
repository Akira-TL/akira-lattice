# Agent harness 与 worktree 参考

仅在需要确认当前 Agent harness 的执行能力、Git worktree 边界或跨进程隔离语义时读取本文。多 Agent 协作协议本身不得依赖某个固定产品、CLI、模型名称或执行器存在。

## harness 能力

- Codex、Claude Code 或其他 Agent harness 都只是实际执行载体，不是项目协议的一部分。
- 先读取当前会话真实暴露的工具契约，再判断是否支持子 Agent、后台进程、终端会话、远程执行、worktree 管理或其他隔离能力；不得根据产品名称猜测。
- 当前 harness 不具备某项能力时，保持串行或使用其他已确认可用的原语；不要通过 Prompt 假造不存在的执行器。
- 不同 harness 的模型名称、权限参数、进程生命周期和结果收集方式可以不同。只有当前 harness 或项目规则明确要求时才显式设置对应参数，不建立跨产品别名映射。
- 工具契约施加的限制属于当前 harness 边界。不得把模型侧或工具侧限制误判为 Git 仓库本身的权限，也不得绕过明确的工具安全约束。

## Git

- 只要当前执行环境确实提供 Git 写能力，仍遵守全局 diff ownership、选择性暂存与 Guard 提交规则。
- Parallel 的确定性 claim 与 Tracker 状态不依赖具体 harness；任务专属 branch/worktree 或其他项目写入必须发生在 claim 成功之后。
- 当前 harness 是否能直接创建 worktree 是实现细节，不是 Parallel Task 的合法性条件。无法创建独立 worktree 时，应根据实际 Ownership 决定是否可以在现有工作树安全执行；不能安全隔离就保持串行。

## worktree

Git worktree 使用标准 Git linked worktree 语义：

- linked worktree 与主仓库共享对象数据库、refs 与 commits，但工作目录彼此独立。
- 创建 worktree 不等于自动合并、cherry-pick、同步或推送代码。
- 不得把 worktree 嵌套在主项目 checkout 内。
- 同一 repository 的 worktree 可通过 `git rev-parse --git-common-dir` 解析共同 Git 目录；Parallel 的同机确定性 claim 正是利用这一标准 Git 事实共享互斥状态。

移动 worktree 后如路径引用失效，可从仍可访问的仓库执行：

```bash
git worktree repair <worktree-path>
git worktree list
```

删除主仓库与移动主仓库不同。主仓库的 Git 对象数据库被删除后，linked worktree 不能作为完整独立仓库继续使用。移动或删除项目前，应先检查全部 worktree，并处理未提交修改、推送、移除或修复工作树。
