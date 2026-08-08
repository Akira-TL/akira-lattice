# Matt Skills fork 与上游同步

仅在处理 Matt skills 的来源、定制、安装或上游同步时读取本文。

## 所有权

- 我们维护的 canonical fork：`git@github.com:Akira-TL/matt-skills.git`。
- Akira Lattice 通过 `skills/matt` Git submodule 固定并管理该 fork 的具体 commit；`.gitmodules` 必须指向我们的 fork，而不是 Matt 原仓库。
- `skills/matt` 内的 `origin` 指向我们的 fork，可正常 fetch/push；`upstream` 指向 `git@github.com:mattpocock/skills.git`，只用于 fetch/merge，push URL 必须保持禁用。
- 我们对 Matt skills 的定制直接提交并 push 到 `Akira-TL/matt-skills`；父仓库只记录更新后的 submodule commit pointer，不复制 Matt skills 正文进自己的 Git 历史。
- 运行时通过 skills CLI 从本地 `skills/matt` 安装，因此实际部署内容与父仓库锁定的 fork commit 一致。

## 合并上游

优先使用 Lattice Guard 的受控入口：

```bash
uv run scripts/guard.py upstream matt
```

该命令要求 Lattice 与 Matt submodule 工作区干净，随后 fetch `origin` 与 `upstream`，把本地 `main` 先对齐我们的 fork `origin/main`，再比较 `upstream/main`。可以 fast-forward 时直接前进；若我们的 fork 已有定制并与 upstream 分叉，则使用 `--no-commit --no-ff` 生成合并结果，并通过 Guard 以 `CHORE: (upstream) 合并 Matt skills 上游更新` 创建 merge commit。发生冲突时保留现场并停止，不自动覆盖任何一侧。

默认命令只更新本地，不 push。确认合并结果后可执行：

```bash
uv run scripts/guard.py upstream matt --push
```

`--push` 明确授权 Guard 把 `skills/matt` 的 `main` push 到我们的 `Akira-TL/matt-skills` fork；push 成功后，Guard 只暂存父仓库的 `skills/matt` gitlink，并以 `CHORE: (matt) 更新 Matt skills 子模块版本` 提交新的 submodule pointer。若前一次未带 `--push` 已完成本地同步，随后带 `--push` 重跑即可完成发布和父仓库提交。

不要用强制同步覆盖 fork 自有提交，也不要直接把 Matt 原仓库配置成 submodule origin。若 Guard 因复杂分叉或冲突停止，再进入 `skills/matt` 人工处理；处理完仍遵守全局 Guard commit 规范。

同步完成后重新运行 `scripts/install.py`，把父仓库锁定的 fork commit 部署到各 Agent 运行时。
