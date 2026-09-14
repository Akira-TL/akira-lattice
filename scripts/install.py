from __future__ import annotations

import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
HOME = Path.home()
HUB = HOME / ".agents"
BACKUP_ROOT = REPO_ROOT / "backup"
AKIRA_SKILLS_SOURCE = "https://github.com/Akira-TL/skills.git"
BASELINE_SKILLS = ("akira", "browser-access", "akira-guard")

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
        if direct_link_target(target) == link_source:
            return
        backup = backup_path(target, stamp)
        print(f"BACKUP {target} -> {backup}")
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


def bootstrap_baseline_skills() -> None:
    with tempfile.TemporaryDirectory(prefix="akira-skill-bootstrap-") as tempdir:
        checkout = Path(tempdir) / "skills"
        clone = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                "main",
                "--",
                AKIRA_SKILLS_SOURCE,
                str(checkout),
            ],
            capture_output=True,
            text=True,
        )
        if clone.returncode != 0:
            detail = clone.stderr.strip() or clone.stdout.strip() or "git clone failed"
            raise RuntimeError(f"无法从远端获取 Akira Skill bootstrap：{detail}")

        installer = checkout / "routing" / "akira" / "scripts" / "skills.py"
        if not installer.is_file():
            raise RuntimeError(f"远端 Akira Skill 缺少安装入口：{installer}")

        command = [sys.executable, str(installer), "install", AKIRA_SKILLS_SOURCE]
        for skill in BASELINE_SKILLS:
            command.extend(["--skill", skill])
        installed = subprocess.run(command)
        if installed.returncode != 0:
            raise RuntimeError("Akira 基础 Skill 云端安装失败")


def deploy() -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path in (
        HUB,
        HOME / ".codex",
        HOME / ".claude",
        HOME / ".config" / "opencode",
    ):
        path.mkdir(parents=True, exist_ok=True)

    ensure_link(CORE_ROOT / "AGENTS.md", HUB / "AGENTS.md", stamp)
    ensure_link(CORE_ROOT / "references", HUB / "references", stamp)
    ensure_link(SCRIPT_ROOT, HUB / "scripts", stamp)
    ensure_link(DOC_PATH, HUB / "README.md", stamp)
    ensure_link(CORE_ROOT / "AGENTS.md", HOME / ".codex" / "AGENTS.md", stamp)
    ensure_link(CORE_ROOT / "AGENTS.md", HOME / ".claude" / "CLAUDE.md", stamp)
    ensure_link(
        CORE_ROOT / "AGENTS.md",
        HOME / ".config" / "opencode" / "AGENTS.md",
        stamp,
    )

    bootstrap_baseline_skills()

    print(f"Core source:      {CORE_ROOT}")
    print(f"Scripts source:   {SCRIPT_ROOT}")
    print(f"Runtime hub:      {HUB}")
    print(f"Baseline Skills:  {', '.join(BASELINE_SKILLS)}")
    print(f"Skill source:     {AKIRA_SKILLS_SOURCE}")


def main() -> int:
    deploy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
