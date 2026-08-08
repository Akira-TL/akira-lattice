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
HUB = Path.home() / ".agents"
LEGACY_ROOT = REPO_ROOT / "context"
LEGACY_DOC = REPO_ROOT / "docs" / "context-management.md"
LEGACY_ADR = REPO_ROOT / ".agents" / "adr" / "0001-agent-context-source-and-runtime.md"


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def backup_path(path: Path, stamp: str) -> Path:
    backup = path.with_name(f"{path.name}.backup.{stamp}")
    path.rename(backup)
    return backup


def same_file_content(source: Path, target: Path) -> bool:
    return source.is_file() and target.is_file() and filecmp.cmp(source, target, shallow=False)


def ensure_link(source: Path, target: Path, stamp: str) -> None:
    link_source = source.expanduser().absolute()
    resolved_source = link_source.resolve(strict=True)
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.is_symlink():
        try:
            if target.resolve(strict=True) == resolved_source:
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


def install_owned_skills() -> None:
    npx = find_npx()
    if npx is None:
        print("WARN   npx 不可用，跳过 devspace-orchestration 安装", file=sys.stderr)
        return

    command = [
        npx,
        "skills",
        "add",
        str(REPO_ROOT),
        "--skill",
        "devspace-orchestration",
        "--agent",
        "*",
        "-g",
        "-y",
    ]
    result = subprocess.run(command, cwd=REPO_ROOT)
    runtime_skill = HUB / "skills" / "devspace-orchestration" / "SKILL.md"
    if not runtime_skill.is_file():
        raise RuntimeError(
            "devspace-orchestration 未安装到 ~/.agents/skills；请检查上方 npx skills 输出"
        )
    if result.returncode != 0:
        print(
            "WARN   skills CLI 对部分不支持全局 Skill 的 Agent 返回失败；"
            "通用运行时 Skill 已存在，继续部署。",
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

    cleanup_runtime_hub()

    ensure_link(CORE_ROOT / "AGENTS.md", HUB / "AGENTS.md", stamp)
    ensure_link(CORE_ROOT / "references", HUB / "references", stamp)
    ensure_link(SCRIPT_ROOT, HUB / "scripts", stamp)
    ensure_link(DOC_PATH, HUB / "README.md", stamp)

    ensure_link(HUB / "AGENTS.md", Path.home() / ".codex" / "AGENTS.md", stamp)
    ensure_link(HUB / "AGENTS.md", Path.home() / ".claude" / "CLAUDE.md", stamp)
    ensure_link(
        HUB / "AGENTS.md",
        Path.home() / ".config" / "opencode" / "AGENTS.md",
        stamp,
    )

    install_owned_skills()

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
