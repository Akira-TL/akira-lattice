from __future__ import annotations

import os
import subprocess
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
HUB = Path.home() / ".agents"
BACKUP_ROOT = REPO_ROOT / "backup"
AKIRA_SKILLS_ROOT = REPO_ROOT / "skills" / "akira"
AKIRA_SKILLS_ORIGIN = "git@github.com:Akira-TL/skills.git"
RESEARCH_SKILLS_ROOT = REPO_ROOT / "skills" / "research"
RESEARCH_SKILLS_ORIGIN = "git@github.com:Akira-TL/akira-research-skills.git"
MATT_SKILLS_ROOT = REPO_ROOT / "skills" / "matt"
MATT_SKILLS_ORIGIN = "git@github.com:Akira-TL/matt-skills.git"
MATT_SKILLS_UPSTREAM = "git@github.com:mattpocock/skills.git"
KNOWLEDGE_SKILLS_ROOT = REPO_ROOT / "skills" / "knowledge"
KNOWLEDGE_SKILLS_ORIGIN = "git@github.com:Akira-TL/akira-knowledge-skills.git"
CORE_LINE_LIMIT = 200


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


def direct_link_target(path: Path) -> Path:
    raw_target = Path(os.readlink(path))
    if raw_target.is_absolute():
        return Path(os.path.abspath(raw_target))
    return Path(os.path.abspath(path.parent / raw_target))


def check_link(target: Path, expected: Path) -> bool:
    if not target.is_symlink():
        fail(f"{target} 不是软链接")
        return False
    try:
        actual = direct_link_target(target)
        wanted = expected.expanduser().absolute()
        expected.resolve(strict=True)
    except OSError as exc:
        fail(f"{target} 链接无法解析：{exc}")
        return False
    if actual != wanted:
        fail(f"{target} -> {actual}，预期直接链接到 {wanted}")
        return False
    ok(str(target))
    return True


def check_submodule_url(name: str, expected: str) -> bool:
    gitmodules = REPO_ROOT / ".gitmodules"
    configured = run_git(
        ["config", "-f", str(gitmodules), "--get", f"submodule.{name}.url"],
        REPO_ROOT,
    )
    configured_url = configured.stdout.strip()
    if configured.returncode == 0 and configured_url == expected:
        ok(f"{name} submodule URL: {expected}")
        return True
    fail(f"{name} submodule URL={configured_url!r}，预期 {expected}")
    return False


def check_submodule_revision(name: str) -> bool:
    submodule = run_git(["submodule", "status", "--", name], REPO_ROOT)
    status = submodule.stdout.strip()
    if submodule.returncode != 0 or not status or status.startswith("-"):
        fail(f"{name} Git submodule 未初始化")
        return False
    if status.startswith("+"):
        fail(f"{name} 当前 commit 与父仓库记录不一致，应提交 submodule pointer")
        return False
    if status.startswith("U"):
        fail(f"{name} Git submodule 存在合并冲突")
        return False
    ok(f"{name} submodule: {status.split()[0]}")
    return True


def check_remote(root: Path, label: str, remote: str, expected: str) -> bool:
    actual = run_git(["remote", "get-url", remote], root)
    actual_url = actual.stdout.strip()
    if actual.returncode == 0 and actual_url == expected:
        ok(f"{label}: {expected}")
        return True
    fail(f"{label}={actual_url!r}，预期 {expected}")
    return False


def check_config() -> int:
    failed = False

    if (HUB / ".git").exists():
        fail(f"{HUB} 不应是独立 Git 仓库")
        failed = True
    else:
        ok(f"{HUB} 不是独立 Git 仓库")

    links = [
        (HUB / "AGENTS.md", CORE_ROOT / "AGENTS.md"),
        (HUB / "references", CORE_ROOT / "references"),
        (HUB / "scripts", SCRIPT_ROOT),
        (HUB / "README.md", REPO_ROOT / "docs" / "agent-config.md"),
        (Path.home() / ".codex" / "AGENTS.md", CORE_ROOT / "AGENTS.md"),
        (Path.home() / ".claude" / "CLAUDE.md", CORE_ROOT / "AGENTS.md"),
        (Path.home() / ".config" / "opencode" / "AGENTS.md", CORE_ROOT / "AGENTS.md"),
    ]
    for target, expected in links:
        failed = not check_link(target, expected) or failed

    gitignore = REPO_ROOT / ".gitignore"
    gitignore_lines = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if "backup/" in gitignore_lines:
        ok(f"{BACKUP_ROOT} 已由 Git 忽略")
    else:
        fail(f"{BACKUP_ROOT} 必须通过仓库 .gitignore 的 backup/ 规则忽略")
        failed = True

    core_lines = len((CORE_ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines())
    if core_lines <= CORE_LINE_LIMIT:
        ok(f"Core 长度 {core_lines} 行")
    else:
        fail(f"Core 已增长到 {core_lines} 行，应重新分层")
        failed = True

    gitmodules = REPO_ROOT / ".gitmodules"
    if not gitmodules.is_file():
        fail("缺少 .gitmodules，Akira、Research、Matt 与 Knowledge 必须作为 Git submodule 管理")
        failed = True
    else:
        for name, expected in (
            ("skills/akira", AKIRA_SKILLS_ORIGIN),
            ("skills/research", RESEARCH_SKILLS_ORIGIN),
            ("skills/matt", MATT_SKILLS_ORIGIN),
            ("skills/knowledge", KNOWLEDGE_SKILLS_ORIGIN),
        ):
            failed = not check_submodule_url(name, expected) or failed

    for name in ("skills/akira", "skills/research", "skills/matt", "skills/knowledge"):
        failed = not check_submodule_revision(name) or failed

    if AKIRA_SKILLS_ROOT.is_dir():
        failed = not check_remote(
            AKIRA_SKILLS_ROOT, "Akira skills origin", "origin", AKIRA_SKILLS_ORIGIN
        ) or failed

    if RESEARCH_SKILLS_ROOT.is_dir():
        failed = not check_remote(
            RESEARCH_SKILLS_ROOT,
            "Research skills origin",
            "origin",
            RESEARCH_SKILLS_ORIGIN,
        ) or failed

    if MATT_SKILLS_ROOT.is_dir():
        failed = not check_remote(
            MATT_SKILLS_ROOT, "Matt origin", "origin", MATT_SKILLS_ORIGIN
        ) or failed
        failed = not check_remote(
            MATT_SKILLS_ROOT, "Matt upstream", "upstream", MATT_SKILLS_UPSTREAM
        ) or failed
        upstream_push = run_git(["remote", "get-url", "--push", "upstream"], MATT_SKILLS_ROOT)
        if upstream_push.returncode == 0 and upstream_push.stdout.strip() == "DISABLED":
            ok("Matt upstream push 已禁用")
        else:
            fail("Matt upstream push 必须设置为 DISABLED")
            failed = True

    if KNOWLEDGE_SKILLS_ROOT.is_dir():
        failed = not check_remote(
            KNOWLEDGE_SKILLS_ROOT,
            "Knowledge skills origin",
            "origin",
            KNOWLEDGE_SKILLS_ORIGIN,
        ) or failed

    return 1 if failed else 0


def main() -> int:
    return check_config()


if __name__ == "__main__":
    raise SystemExit(main())
