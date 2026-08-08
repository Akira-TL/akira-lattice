# Matt Skills fork 与上游同步

仅在处理 Matt skills 的来源、定制、安装或上游同步时读取本文。

## 所有权

- 我们维护的 canonical fork：`git@github.com:Akira-TL/matt-skills.git`。
- Akira Lattice 通过 `skills/matt` Git submodule 固定并管理该 fork 的具体 commit；`.gitmodules` 必须指向我们的 fork，而不是 Matt 原仓库。
- `skills/matt` 内的 `origin` 指向我们的 fork，可正常 fetch/push；`upstream` 指向 `git@github.com:mattpocock/skills.git`，只用于 fetch/merge，push URL 必须保持禁用。
- 我们对 Matt skills 的定制直接提交并 push 到 `Akira-TL/matt-skills`；父仓库只记录更新后的 submodule commit pointer，不复制 Matt skills 正文进自己的 Git 历史。
- 运行时通过 skills CLI 从本地 `skills/matt` 安装，因此实际部署内容与父仓库锁定的 fork commit 一致。

## 合并上游

先确认 submodule 工作区干净并检查分支结构：

```bash
cd ~/Projects/akira-skills/skills/matt
git status --short
git branch -vv
git worktree list
git fetch upstream
```

若我们的 `main` 没有独立提交且可以快进：

```bash
git merge --ff-only upstream/main
git push origin main
```

若我们的 `main` 已有定制并与上游分叉：

```bash
git merge --no-commit upstream/main
# 解决冲突后，只暂存已确认的合并结果
git add -- <paths...>
uv run ~/.agents/scripts/guard.py commit -m 'CHORE: (upstream) 合并 Matt skills 上游更新'
git push origin main
```

不要用会覆盖 fork 自有提交的强制同步。合并并 push fork 后，回到父仓库提交新的 submodule pointer：

```bash
cd ~/Projects/akira-skills
git add -- skills/matt
uv run ~/.agents/scripts/guard.py commit -m 'CHORE: (matt) 更新 Matt skills 子模块版本'
```

随后重新运行 `scripts/install.py`，把父仓库锁定的 fork commit 部署到各 Agent 运行时。
