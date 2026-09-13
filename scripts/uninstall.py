from __future__ import annotations

import os
from pathlib import Path

from skill_manager import SkillInstallError, remove_installed

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
HOME = Path.home()
HUB = HOME / ".agents"
DEFAULT_RUNTIME_SKILLS = ("akira", "browser-access")


def direct_link_target(path: Path) -> Path:
    raw_target = Path(os.readlink(path))
    if raw_target.is_absolute():
        return Path(os.path.abspath(raw_target))
    return Path(os.path.abspath(path.parent / raw_target))


def remove_owned_link(source: Path, target: Path) -> None:
    if not target.is_symlink():
        if target.exists():
            print(f"KEEP   {target}（不是本项目创建的软链接）")
        return

    expected = source.expanduser().absolute()
    if direct_link_target(target) != expected:
        print(f"KEEP   {target}（指向其他来源）")
        return

    target.unlink()
    print(f"REMOVE {target}")


def uninstall_runtime_skills() -> None:
    try:
        removed = remove_installed(DEFAULT_RUNTIME_SKILLS, global_scope=True)
    except SkillInstallError as exc:
        raise RuntimeError(str(exc)) from exc
    if not removed:
        print("SKILLS 当前没有检测到 Akira Lattice 全局基线")


def uninstall_runtime_links() -> None:
    owned_links = (
        (CORE_ROOT / "AGENTS.md", HUB / "AGENTS.md"),
        (CORE_ROOT / "references", HUB / "references"),
        (SCRIPT_ROOT, HUB / "scripts"),
        (DOC_PATH, HUB / "README.md"),
        (CORE_ROOT / "AGENTS.md", HOME / ".codex" / "AGENTS.md"),
        (CORE_ROOT / "AGENTS.md", HOME / ".claude" / "CLAUDE.md"),
        (CORE_ROOT / "AGENTS.md", HOME / ".config" / "opencode" / "AGENTS.md"),
    )
    for source, target in owned_links:
        remove_owned_link(source, target)


def main() -> int:
    uninstall_runtime_skills()
    uninstall_runtime_links()
    print("卸载完成；Git source cache 与其他软件状态均未清理。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR  {exc}")
        raise SystemExit(1) from exc
