from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

CommitCallback = Callable[[Path, str], int]


def ok(message: str) -> None:
    print(f"OK    {message}")


def fail(message: str) -> None:
    print(f"FAIL  {message}")


def run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
    )


def require_clean(root: Path, label: str) -> bool:
    result = run_git(["status", "--porcelain=v1"], root)
    if result.returncode != 0:
        fail(f"无法检查 {label} 工作区状态")
        return False
    dirty = result.stdout.strip()
    if dirty:
        fail(f"{label} 工作区不干净，先处理现有修改：")
        print(dirty)
        return False
    return True


def require_parent_clean(parent: Path, *, allow_matt_pointer: bool) -> bool:
    result = run_git(["status", "--porcelain=v1", "--untracked-files=all"], parent)
    if result.returncode != 0:
        fail("无法检查 Lattice 工作区状态")
        return False
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return True
    if allow_matt_pointer and all(line[3:] == "skills/matt" for line in lines):
        cached = run_git(["diff", "--cached", "--quiet"], parent)
        if cached.returncode == 0:
            return True
    fail("Lattice 存在与 Matt pointer 无关或已暂存的修改，拒绝执行 upstream 同步：")
    for line in lines:
        print(line)
    return False


def ahead_behind(root: Path, left: str, right: str) -> tuple[int, int] | None:
    result = run_git(["rev-list", "--left-right", "--count", f"{left}...{right}"], root)
    if result.returncode != 0:
        fail(f"无法比较 {left} 与 {right}: {result.stderr.strip()}")
        return None
    try:
        ahead_text, behind_text = result.stdout.strip().split()
        return int(ahead_text), int(behind_text)
    except ValueError:
        fail(f"无法解析 {left} 与 {right} 的 ahead/behind")
        return None


def ensure_main(root: Path) -> int:
    branch = run_git(["branch", "--show-current"], root)
    if branch.returncode != 0:
        fail("无法读取 Matt submodule 当前分支")
        return 1
    if branch.stdout.strip() == "main":
        return 0

    head = run_git(["rev-parse", "HEAD"], root)
    local_main = run_git(["rev-parse", "--verify", "refs/heads/main"], root)
    head_sha = head.stdout.strip()

    if local_main.returncode == 0:
        local_main_sha = local_main.stdout.strip()
        if local_main_sha != head_sha:
            origin_main = run_git(["rev-parse", "origin/main"], root)
            ancestor = run_git(["merge-base", "--is-ancestor", "HEAD", "refs/heads/main"], root)
            if (
                origin_main.returncode != 0
                or local_main_sha != origin_main.stdout.strip()
                or ancestor.returncode != 0
            ):
                fail(
                    "Matt submodule detached HEAD 与本地 main 不同，且无法确认 main 是 origin/main 的安全前进版本"
                )
                return 1
        command = ["git", "-C", str(root), "switch", "main"]
    else:
        origin_main = run_git(["rev-parse", "origin/main"], root)
        if origin_main.returncode != 0 or origin_main.stdout.strip() != head_sha:
            fail("Matt submodule detached HEAD 与 origin/main 不一致；拒绝自动创建 main")
            return 1
        command = ["git", "-C", str(root), "switch", "-c", "main", "--track", "origin/main"]

    return subprocess.run(command).returncode


def sync_matt(
    *,
    parent: Path,
    matt: Path,
    origin_url: str,
    upstream_url: str,
    push: bool,
    guarded_commit: CommitCallback,
) -> int:
    if not matt.is_dir():
        fail("skills/matt 未初始化；先运行 scripts/install.py")
        return 1

    pointer_dirty = run_git(["diff", "--quiet", "--", "skills/matt"], parent).returncode != 0
    if not require_parent_clean(parent, allow_matt_pointer=push):
        return 1
    if not require_clean(matt, "Matt"):
        return 1

    for remote, expected in (("origin", origin_url), ("upstream", upstream_url)):
        actual = run_git(["remote", "get-url", remote], matt)
        if actual.returncode != 0 or actual.stdout.strip() != expected:
            fail(f"Matt {remote}={actual.stdout.strip()!r}，预期 {expected}")
            return 1
        print(f"INFO  fetch Matt {remote}")
        fetched = subprocess.run(["git", "-C", str(matt), "fetch", remote])
        if fetched.returncode != 0:
            fail(f"Matt {remote} fetch 失败")
            return fetched.returncode

    if ensure_main(matt) != 0:
        return 1

    origin_state = ahead_behind(matt, "HEAD", "origin/main")
    if origin_state is None:
        return 1
    origin_ahead, origin_behind = origin_state
    print(f"INFO  Matt vs origin/main: ahead={origin_ahead}, behind={origin_behind}")
    if origin_ahead and origin_behind:
        fail("Matt 本地 main 与 origin/main 已分叉；先人工处理 fork 自身分叉")
        return 1
    if origin_behind:
        result = subprocess.run(["git", "-C", str(matt), "merge", "--ff-only", "origin/main"])
        if result.returncode != 0:
            return result.returncode
    elif origin_ahead and not push:
        fail("Matt 本地 main 有尚未推送到 origin 的提交；确认后使用 --push 发布并更新父仓库")
        return 1

    upstream_state = ahead_behind(matt, "HEAD", "upstream/main")
    if upstream_state is None:
        return 1
    upstream_ahead, upstream_behind = upstream_state
    print(f"INFO  Matt vs upstream/main: ahead={upstream_ahead}, behind={upstream_behind}")

    changed = pointer_dirty or origin_ahead > 0 or origin_behind > 0
    if upstream_behind:
        if upstream_ahead == 0:
            result = subprocess.run(["git", "-C", str(matt), "merge", "--ff-only", "upstream/main"])
        else:
            result = subprocess.run(
                ["git", "-C", str(matt), "merge", "--no-commit", "--no-ff", "upstream/main"]
            )
        if result.returncode != 0:
            fail("Matt upstream merge 出现冲突；保留冲突现场供人工处理")
            return result.returncode
        if upstream_ahead:
            commit_result = guarded_commit(matt, "CHORE: (upstream) 合并 Matt skills 上游更新")
            if commit_result != 0:
                return commit_result
        changed = True

    if not changed:
        ok("Matt fork 已包含当前 upstream/main，无需更新")
        return 0

    if not push:
        ok("Matt 本地 fork 已同步到可提交状态")
        print("INFO  尚未修改远端；确认后重新运行 `uv run scripts/guard.py upstream matt --push`")
        return 0

    pushed = subprocess.run(["git", "-C", str(matt), "push", "origin", "main"])
    if pushed.returncode != 0:
        fail("Matt fork push 失败；父仓库 pointer 未提交")
        return pushed.returncode

    staged = subprocess.run(["git", "-C", str(parent), "add", "--", "skills/matt"])
    if staged.returncode != 0:
        return staged.returncode
    if run_git(["diff", "--cached", "--quiet", "--", "skills/matt"], parent).returncode == 0:
        ok("Matt fork 已推送，Lattice submodule pointer 无变化")
        return 0

    return guarded_commit(parent, "CHORE: (matt) 更新 Matt skills 子模块版本")
