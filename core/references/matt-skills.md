# Matt Skills 所有权与上游参考

仅在处理 Matt Skills 的来源、定制或上游参考时读取本文。

## 所有权

- canonical repository：`git@github.com:Akira-TL/matt-skills.git`。
- Akira Lattice 通过 `skills/matt` Git submodule 固定开发 revision；`.gitmodules` 必须指向我们的仓库。
- `skills/matt` 的 `origin` 指向 `Akira-TL/matt-skills`，是唯一发布远端。
- `upstream` 指向 `git@github.com:mattpocock/skills.git`，只用于获取参考变化，push URL 必须保持禁用。
- 运行时通过 `akira` Router 从远端 `Akira-TL/matt-skills` 安装，不从本地 submodule checkout 安装。

## 上游参考

Matt 系列现在由我们独立维护，不再整体同步 `upstream/main`。需要吸收上游内容时：

```bash
git -C skills/matt fetch upstream
git -C skills/matt log --oneline HEAD..upstream/main
git -C skills/matt show <upstream-commit>
```

只选择当前 Akira Matt 工程流真实需要的变化。优先人工适配或选择性 cherry-pick 单个上游提交；不要 merge 整个 `upstream/main`，也不要以“与上游保持同步”为目标。

引入前必须检查它与当前 `ask-matt`、`ask-akira`、Parallel 协作以及 Akira Core 规则是否兼容。引入后该内容由我们继续维护，并按普通原子提交、测试和文档规则处理。

上游来源必须可追溯。不得 force push 我们的 `main`，不得把 upstream 配成可推送远端。
