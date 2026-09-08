from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
OPENAI_NGS_ROOT = REPO_ROOT / "skills" / "openai-plugins" / "plugins" / "ngs-analysis"
HOME = Path.home()
HUB = HOME / ".agents"
NGS_RUNTIME_VIEW = HUB / "external" / "ngs-analysis"
INSTALL_MANIFEST = HUB / ".akira-skills-install.json"


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


def manifest_skills() -> dict[str, str]:
    if not INSTALL_MANIFEST.is_file():
        return {}
    try:
        payload = json.loads(INSTALL_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"无法读取安装清单 {INSTALL_MANIFEST}: {exc}") from exc
    skills = payload.get("skills")
    if not isinstance(skills, dict):
        raise RuntimeError(f"安装清单格式无效：{INSTALL_MANIFEST}")

    parsed: dict[str, str] = {}
    for name, metadata in skills.items():
        if not isinstance(name, str) or not isinstance(metadata, dict):
            raise RuntimeError(f"安装清单格式无效：{INSTALL_MANIFEST}")
        digest = metadata.get("skill_md_sha256")
        if not isinstance(digest, str):
            raise RuntimeError(f"安装清单格式无效：{INSTALL_MANIFEST}")
        parsed[name] = digest
    return parsed


def runtime_skill_hash(name: str) -> str | None:
    skill_file = HUB / "skills" / name / "SKILL.md"
    if not skill_file.is_file():
        return None
    return hashlib.sha256(skill_file.read_bytes()).hexdigest()


def installed_project_skills() -> list[str]:
    owned: list[str] = []
    for name, expected_hash in manifest_skills().items():
        current_hash = runtime_skill_hash(name)
        if current_hash is None:
            continue
        if current_hash != expected_hash:
            print(f"KEEP   {HUB / 'skills' / name}（安装后已被其他内容替换）")
            continue
        owned.append(name)
    return sorted(owned)


def uninstall_runtime_skills() -> None:
    names = installed_project_skills()
    if not names:
        print("SKILLS 当前没有检测到由本项目来源提供的已安装 Skill")
        return

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if npx is None:
        raise RuntimeError("npx 不可用，无法通过 skills CLI 卸载运行时 Skill")

    result = subprocess.run(
        [npx, "skills", "remove", *names, "--global", "--yes"],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError("skills CLI 卸载失败；全局提示词入口保持不变，请检查上方输出")


def uninstall_runtime_links() -> None:
    owned_links = (
        (CORE_ROOT / "AGENTS.md", HUB / "AGENTS.md"),
        (CORE_ROOT / "references", HUB / "references"),
        (SCRIPT_ROOT, HUB / "scripts"),
        (DOC_PATH, HUB / "README.md"),
        (OPENAI_NGS_ROOT, NGS_RUNTIME_VIEW),
        (CORE_ROOT / "AGENTS.md", HOME / ".codex" / "AGENTS.md"),
        (CORE_ROOT / "AGENTS.md", HOME / ".claude" / "CLAUDE.md"),
        (CORE_ROOT / "AGENTS.md", HOME / ".config" / "opencode" / "AGENTS.md"),
    )
    for source, target in owned_links:
        remove_owned_link(source, target)


def main() -> int:
    uninstall_runtime_skills()
    uninstall_runtime_links()
    if INSTALL_MANIFEST.exists() or INSTALL_MANIFEST.is_symlink():
        INSTALL_MANIFEST.unlink()
        print(f"REMOVE {INSTALL_MANIFEST}")
    print("卸载完成；backup/、Agent 配置目录及其他软件状态均未清理。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
