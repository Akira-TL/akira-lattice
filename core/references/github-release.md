# GitHub 推送、CI 与发布

仅在涉及 GitHub push、云端 CI、tag、release 或包发布时读取本文。

## 基本顺序

- 日常开发与正式发布分开处理。普通 commit / push 只执行仓库日常规则要求的最低限度语法检查、Guard 或与当前原子修改直接相关的验证，不自动运行完整 release gate，也不得触发云端 CI。
- 完整本地 CI / release gate 只在准备正式版本 tag 时运行。顺序固定为：准备版本元数据 → 完整本地验收通过 → push 已验收的 release-ready 提交 → 创建并 push `vX.Y.Z` tag → 由 tag 启动云端 CI / 发布 workflow。
- 不得为了“让 CI 帮忙看看”而触发云端流水线。普通 branch push、PR 更新、手动 dispatch 都不应成为默认 CI 入口；仓库若允许这些入口，除非用户明确要求保留，否则应收紧到正式发布 tag 流程。

## Push 与云端 CI

- 日常 `git push` 只推送归属明确、已完成日常最低限度本地检查的提交；它本身不应启动云端 CI。
- 不主动运行 `gh workflow run`、Actions 手动 dispatch 或其他独立云端 CI 入口。正式发布时由 `vX.Y.Z` tag push 自动进入仓库定义的 CI / release 流程。
- 云端 CI 失败时先读取失败日志并在本地复现、修复；修复后重新完成发布所需的本地 release gate，再准备可发布状态。是否必须更换版本号取决于该版本是否已经产生不可撤回的正式发布产物，而不是取决于版本 tag 是否曾经推送。不要靠连续 push 或反复 dispatch 猜测修复。

## Release 与发布 tag

- 创建或推送发布 tag 属于正式发布动作，不属于普通开发 push。只有用户明确要求发布，并且目标版本已经确定时才执行。
- 自动发布只允许由稳定版本 tag `vX.Y.Z` 触发，其中 `X`、`Y`、`Z` 均为非负整数；普通 branch push、PR、非版本 tag 不得触发 npm/GitHub Release 等发布动作。
- 推送 `vX.Y.Z` 前必须同时满足：本地 release gate 全部通过、release metadata 与 tag 一致、目标提交已 push、工作区无未归属修改。
- `vX.Y.Z` tag push 后，云端 workflow 必须先完成 CI 验证，只有 CI 全部通过才允许继续 npm / GitHub Release 发布。云端校验是最终防线，不替代 tag 前的完整本地验收。
- 发布 tag 是否不可变，以对应版本是否已经产生不可撤回的正式发布产物为界，而不是以 tag 是否已经推送为界。
- 若 `vX.Y.Z` 只存在于本地或远端 Git，尚未产生 GitHub Release、包仓库已发布版本或其他不可撤回的正式发布产物，则它仍属于可重试的失败 / 预发布 tag。修复原因并重新通过完整本地 release gate 后，可以删除并重新创建同名 tag，使其指向修复后的 release-ready 提交，并继续使用同一版本号。该例外只允许修正尚未正式发布的 tag ref，不允许借此 force push 分支或覆盖其他已发布历史。
- 一旦该版本已经产生 GitHub Release、npm / PyPI 等包仓库版本，或其他已对外发布且不能可靠撤回、不能安全复用同一版本号的产物，则对应 tag 与版本内容视为不可变：不得删除、移动或重用该发布 tag；修复原因后准备新的版本号并按完整发布流程重新发布。
