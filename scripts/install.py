from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
HOME = Path.home()
HUB = HOME / ".agents"
BACKUP_ROOT = REPO_ROOT / "backup"
LEGACY_ROOT = REPO_ROOT / "context"
LEGACY_DOC = REPO_ROOT / "docs" / "context-management.md"
LEGACY_ADR = REPO_ROOT / ".agents" / "adr" / "0001-agent-context-source-and-runtime.md"
AKIRA_SKILLS_ROOT = REPO_ROOT / "skills" / "akira"
MATT_SKILLS_ROOT = REPO_ROOT / "skills" / "matt"
MATT_SKILLS_UPSTREAM = "git@github.com:mattpocock/skills.git"


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def backup_destination(path: Path, stamp: str) -> Path:
    try:
        relative = path.absolute().relative_to(HOME.absolute())
    except ValueError as exc:
        raise RuntimeError(f"仅允许备份 Home 目录下的运行时文件：{path}") from exc

    backup = BACKUP_ROOT / relative.parent / f"{relative.name}.backup.{stamp}"
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists() or backup.is_symlink():
        raise RuntimeError(f"备份目标已存在，拒绝覆盖：{backup}")
    return backup


def backup_path(path: Path, stamp: str) -> Path:
    backup = backup_destination(path, stamp)
    shutil.move(str(path), str(backup))
    return backup


def move_legacy_backup(path: Path) -> None:
    try:
        relative = path.absolute().relative_to(HOME.absolute())
    except ValueError:
        return
    target = BACKUP_ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        print(f"WARN   旧备份目标已存在，保留原文件：{path}", file=sys.stderr)
        return
    shutil.move(str(path), str(target))
    print(f"MOVE   {path} -> {target}")


def migrate_legacy_backups() -> None:
    candidates = list(HUB.glob("*.backup.*"))
    candidates.extend(HUB.glob("*.bak.*"))
    for prompt in (
        HOME / ".codex" / "AGENTS.md",
        HOME / ".claude" / "CLAUDE.md",
        HOME / ".config" / "opencode" / "AGENTS.md",
    ):
        candidates.extend(prompt.parent.glob(f"{prompt.name}.backup.*"))
        candidates.extend(prompt.parent.glob(f"{prompt.name}.bak.*"))

    for path in sorted(set(candidates)):
        move_legacy_backup(path)


def same_file_content(source: Path, target: Path) -> bool:
    return source.is_file() and target.is_file() and filecmp.cmp(source, target, shallow=False)


def direct_link_target(path: Path) -> Path:
    raw_target = Path(os.readlink(path))
    if raw_target.is_absolute():
        return Path(os.path.abspath(raw_target))
    return Path(os.path.abspath(path.parent / raw_target))


def ensure_link(source: Path, target: Path, stamp: str) -> None:
    link_source = source.expanduser().absolute()
    resolved_source = link_source.resolve(strict=True)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.is_symlink():
        try:
            if direct_link_target(target) == link_source:
                return
        except OSError:
            pass
        target.unlink()
    elif target.exists():
        if same_file_content(resolved_source, target):
            remove_path(target)
        else:
            backup = backup_path(target, stamp)
            print(f"BACKUP {target} -> {backup}")

    try:
        target.symlink_to(link_source, target_is_directory=resolved_source.is_dir())
    except OSError as exc:
        raise RuntimeError(
            f"无法创建软链接 {target} -> {link_source}: {exc}. "
            "Windows 上可能需要启用 Developer Mode 或管理员权限。"
        ) from exc

    print(f"LINK   {target} -> {link_source}")


def find_npx() -> str | None:
    return shutil.which("npx") or shutil.which("npx.cmd")


def ensure_skill_submodules() -> None:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "submodule",
            "update",
            "--init",
            "--recursive",
            "skills/akira",
            "skills/matt",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError("无法初始化 skills/akira 或 skills/matt Git submodule")

    required_akira_skills = (
        "devspace-orchestration",
        "akira-guard",
    )
    for skill in required_akira_skills:
        path = AKIRA_SKILLS_ROOT / "engineering" / skill / "SKILL.md"
        if not path.is_file():
            raise RuntimeError(f"skills/akira 已初始化，但缺少 {skill}")

    required_matt_skill = MATT_SKILLS_ROOT / "skills" / "engineering" / "ask-matt" / "SKILL.md"
    if not required_matt_skill.is_file():
        raise RuntimeError("skills/matt 已初始化，但缺少 ask-matt")

    upstream = subprocess.run(
        ["git", "-C", str(MATT_SKILLS_ROOT), "remote", "get-url", "upstream"],
        capture_output=True,
        text=True,
    )
    if upstream.returncode != 0:
        subprocess.run(
            [
                "git",
                "-C",
                str(MATT_SKILLS_ROOT),
                "remote",
                "add",
                "upstream",
                MATT_SKILLS_UPSTREAM,
            ],
            check=True,
        )
    else:
        subprocess.run(
            [
                "git",
                "-C",
                str(MATT_SKILLS_ROOT),
                "remote",
                "set-url",
                "upstream",
                MATT_SKILLS_UPSTREAM,
            ],
            check=True,
        )
    subprocess.run(
        [
            "git",
            "-C",
            str(MATT_SKILLS_ROOT),
            "remote",
            "set-url",
            "--push",
            "upstream",
            "DISABLED",
        ],
        check=True,
    )


def install_runtime_skills() -> None:
    npx = find_npx()
    if npx is None:
        print("WARN   npx 不可用，跳过运行时 Skill 安装", file=sys.stderr)
        return

    ensure_skill_submodules()

    installs = (
        (str(AKIRA_SKILLS_ROOT), "devspace-orchestration", "devspace-orchestration"),
        (str(AKIRA_SKILLS_ROOT), "akira-guard", "akira-guard"),
        (str(MATT_SKILLS_ROOT), "*", "ask-matt"),
    )
    for source, selector, required_skill in installs:
        command = [
            npx,
            "skills",
            "add",
            source,
            "--skill",
            selector,
            "--agent",
            "*",
            "-g",
            "-y",
        ]
        result = subprocess.run(command, cwd=REPO_ROOT)
        runtime_skill = HUB / "skills" / required_skill / "SKILL.md"
        if not runtime_skill.is_file():
            raise RuntimeError(
                f"{required_skill} 未安装到 ~/.agents/skills；请检查上方 npx skills 输出"
            )
        if result.returncode != 0:
            print(
                f"WARN   {source} 安装时部分 Agent 不支持全局 Skill；"
                f"运行时 {required_skill} 已存在，继续部署。",
                file=sys.stderr,
            )


def cleanup_runtime_hub() -> None:
    git_dir = HUB / ".git"
    gitignore = HUB / ".gitignore"
    if git_dir.exists():
        shutil.rmtree(git_dir)
    if gitignore.exists() or gitignore.is_symlink():
        remove_path(gitignore)


def cleanup_legacy_source() -> None:
    if LEGACY_ROOT.exists():
        shutil.rmtree(LEGACY_ROOT)
        print(f"REMOVE {LEGACY_ROOT}")
    if LEGACY_DOC.exists():
        LEGACY_DOC.unlink()
        print(f"REMOVE {LEGACY_DOC}")
    if LEGACY_ADR.exists():
        LEGACY_ADR.unlink()
        print(f"REMOVE {LEGACY_ADR}")


def deploy(*, cleanup_legacy: bool) -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path in (
        HUB,
        Path.home() / ".codex",
        Path.home() / ".claude",
        Path.home() / ".config" / "opencode",
    ):
        path.mkdir(parents=True, exist_ok=True)

    migrate_legacy_backups()
    cleanup_runtime_hub()

    ensure_link(CORE_ROOT / "AGENTS.md", HUB / "AGENTS.md", stamp)
    ensure_link(CORE_ROOT / "references", HUB / "references", stamp)
    ensure_link(SCRIPT_ROOT, HUB / "scripts", stamp)
    ensure_link(DOC_PATH, HUB / "README.md", stamp)

    ensure_link(CORE_ROOT / "AGENTS.md", Path.home() / ".codex" / "AGENTS.md", stamp)
    ensure_link(CORE_ROOT / "AGENTS.md", Path.home() / ".claude" / "CLAUDE.md", stamp)
    ensure_link(
        CORE_ROOT / "AGENTS.md",
        Path.home() / ".config" / "opencode" / "AGENTS.md",
        stamp,
    )

    install_runtime_skills()

    if cleanup_legacy:
        cleanup_legacy_source()

    print(f"Core source:    {CORE_ROOT}")
    print(f"Scripts source: {SCRIPT_ROOT}")
    print(f"Runtime hub:    {HUB}")
    print(f"Skills state:   {HUB / 'skills'} (skills CLI owned)")
    print(f"Skill lock:     {HUB / '.skill-lock.json'} (skills CLI owned)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="部署 Akira 的静态 Agent 配置与仓库自有运行时 Skill。"
    )
    parser.add_argument(
        "--cleanup-legacy",
        action="store_true",
        help="部署成功后删除旧的仓库 context/ 迁移目录",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    deploy(cleanup_legacy=args.cleanup_legacy)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
