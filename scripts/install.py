from __future__ import annotations

import filecmp
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
HOME = Path.home()
HUB = HOME / ".agents"
FORGERELAY_HOME = HOME / ".forgerelay"
FORGERELAY_SKILLS = FORGERELAY_HOME / "skills"
BACKUP_ROOT = REPO_ROOT / "backup"
AKIRA_SKILLS_ROOT = REPO_ROOT / "skills" / "akira"
RESEARCH_SKILLS_ROOT = REPO_ROOT / "skills" / "research"
MATT_SKILLS_ROOT = REPO_ROOT / "skills" / "matt"
DEFAULT_RUNTIME_SKILLS = ("akira", "browser-access")
INSTALL_MANIFEST = FORGERELAY_HOME / ".akira-skills-install.json"
NAME_PATTERN = re.compile(r"^name:\s*([^\s#]+)\s*$")


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


def find_npx() -> str:
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx is None:
        raise RuntimeError("npx 不可用，无法安装运行时 Skill")
    return npx


def ensure_source_submodules() -> None:
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
            "skills/research",
            "skills/matt",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError("无法初始化 Akira、Research 或 Matt Git submodule")

    if not (AKIRA_SKILLS_ROOT / "AGENTS.md").is_file():
        raise RuntimeError("skills/akira 未正确初始化")
    if not (RESEARCH_SKILLS_ROOT / "README.md").is_file():
        raise RuntimeError("skills/research 未正确初始化")
    if not MATT_SKILLS_ROOT.is_dir():
        raise RuntimeError("skills/matt 未正确初始化")


def skill_name(skill_file: Path) -> str | None:
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()[:40]
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = NAME_PATTERN.match(line.strip())
        if match:
            return match.group(1)
    return None


def discover_skill_names(root: Path) -> list[str]:
    names: set[str] = set()
    for skill_file in root.rglob("SKILL.md"):
        relative = skill_file.relative_to(root)
        if "deprecated" in relative.parts:
            continue
        name = skill_name(skill_file)
        if name:
            names.add(name)
    return sorted(names)


def install_skill_source(
    npx: str,
    source: Path,
    label: str,
    skill_names: tuple[str, ...],
) -> None:
    # npx skills currently has no arbitrary target-directory flag. Its project-level
    # openclaw profile writes to <cwd>/skills, so using ~/.forgerelay as cwd lets the
    # CLI own ~/.forgerelay/skills without involving ~/.agents/skills.
    command = [
        npx,
        "skills",
        "add",
        str(source),
        "--skill",
        *skill_names,
        "--agent",
        "openclaw",
        "-y",
    ]
    FORGERELAY_HOME.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=FORGERELAY_HOME)
    if result.returncode != 0:
        print(
            f"WARN   {label} 安装失败；请检查上方 skills CLI 输出。",
            file=sys.stderr,
        )


def install_runtime_skills() -> list[str]:
    npx = find_npx()
    available = set(discover_skill_names(AKIRA_SKILLS_ROOT))
    missing_source = sorted(set(DEFAULT_RUNTIME_SKILLS).difference(available))
    if missing_source:
        raise RuntimeError(
            "默认 ForgeRelay 运行时 Skill 未出现在 Akira 通用仓："
            + ", ".join(missing_source)
        )

    install_skill_source(
        npx,
        AKIRA_SKILLS_ROOT,
        "Akira baseline Skills",
        DEFAULT_RUNTIME_SKILLS,
    )

    expected = set(DEFAULT_RUNTIME_SKILLS)
    installed = sorted(
        name
        for name in expected
        if (FORGERELAY_SKILLS / name).exists()
        or (FORGERELAY_SKILLS / name).is_symlink()
    )
    missing = sorted(expected.difference(installed))
    if missing:
        raise RuntimeError(
            "以下项目 Skill 未出现在 ForgeRelay 运行时：" + ", ".join(missing)
        )
    return installed


def skill_runtime_hash(name: str) -> str:
    skill_file = FORGERELAY_SKILLS / name / "SKILL.md"
    if not skill_file.is_file():
        raise RuntimeError(f"运行时 Skill 缺少 SKILL.md：{name}")
    return hashlib.sha256(skill_file.read_bytes()).hexdigest()


def write_install_manifest(skill_names: list[str]) -> None:
    payload = {
        "version": 1,
        "repo_root": str(REPO_ROOT),
        "skills": {
            name: {"skill_md_sha256": skill_runtime_hash(name)} for name in skill_names
        },
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    INSTALL_MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"STATE  {INSTALL_MANIFEST}")


def deploy() -> None:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ensure_source_submodules()
    for path in (
        HUB,
        FORGERELAY_HOME,
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

    installed_skills = install_runtime_skills()
    write_install_manifest(installed_skills)

    print(f"Core source:    {CORE_ROOT}")
    print(f"Scripts source: {SCRIPT_ROOT}")
    print(f"Runtime hub:    {HUB}")
    print(f"ForgeRelay:     {FORGERELAY_HOME}")
    print(f"Skills state:   {FORGERELAY_SKILLS} (skills CLI owned)")
    print(f"Skill lock:     {FORGERELAY_HOME / 'skills-lock.json'} (skills CLI owned)")


def main() -> int:
    deploy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
