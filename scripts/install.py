from __future__ import annotations

import filecmp
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
DOC_PATH = REPO_ROOT / "docs" / "agent-config.md"
HOME = Path.home()
HUB = HOME / ".agents"
BACKUP_ROOT = REPO_ROOT / "backup"

SKILOOM_MIN_VERSION = (0, 8, 15)
SKILOOM_GIT_REF = "main"
BASELINE_PACKAGES = (
    "akira-tl/skiloom/skiloom",
    "akira-tl/skills/akira",
    "akira-tl/skills/browser-access",
    "akira-tl/skills/akira-guard",
)


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


def _parse_skiloom_version(output: str) -> tuple[int, int, int]:
    match = re.search(r"skiloom\s+(\d+)\.(\d+)\.(\d+)", output)
    if match is None:
        raise RuntimeError(f"无法解析 Skiloom 版本：{output.strip() or '<empty>'}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def require_skiloom() -> str:
    executable = shutil.which("skiloom")
    if executable is None:
        raise RuntimeError(
            "缺少 Skiloom CLI。Akira Skill 生命周期已统一交给 Skiloom；"
            "请先安装受支持的 Skiloom，再重新运行 ./install.sh。"
        )

    result = subprocess.run(
        [executable, "--version"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "skiloom --version failed"
        raise RuntimeError(f"无法执行 Skiloom CLI：{detail}")

    version = _parse_skiloom_version(result.stdout or result.stderr)
    if version < SKILOOM_MIN_VERSION:
        required = ".".join(str(part) for part in SKILOOM_MIN_VERSION)
        actual = ".".join(str(part) for part in version)
        raise RuntimeError(f"Skiloom 版本过旧：{actual}；至少需要 {required}")
    return executable


def _skiloom_error(output: str) -> str:
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        return output.strip() or "unknown Skiloom error"
    error = payload.get("error")
    if isinstance(error, dict):
        code = error.get("code", "SkiloomError")
        facts = error.get("facts")
        return f"{code}: {facts}" if facts else str(code)
    return output.strip() or "unknown Skiloom error"


def bootstrap_baseline_skills(skiloom: str | None = None) -> None:
    skiloom = skiloom or require_skiloom()
    for coordinate in BASELINE_PACKAGES:
        command = [
            skiloom,
            "install",
            coordinate,
            "--git",
            SKILOOM_GIT_REF,
            "--scope",
            "user",
            "--yes",
            "--non-interactive",
            "--json",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            detail = _skiloom_error(result.stdout or result.stderr)
            raise RuntimeError(f"Skiloom 基础 Package bootstrap 失败（{coordinate}）：{detail}")

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Skiloom 返回非 JSON 输出（{coordinate}）") from exc
        if payload.get("schema") != "SKILOOM-CLI-V1" or payload.get("ok") is not True:
            raise RuntimeError(f"Skiloom bootstrap 返回异常结果（{coordinate}）：{payload}")
        print(f"SKILOOM {coordinate}")


def deploy() -> None:
    skiloom = require_skiloom()
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

    bootstrap_baseline_skills(skiloom)

    print(f"Core source:      {CORE_ROOT}")
    print(f"Scripts source:   {SCRIPT_ROOT}")
    print(f"Runtime hub:      {HUB}")
    print(f"Skiloom:          {skiloom}")
    print(f"Baseline Packages: {', '.join(BASELINE_PACKAGES)}")


def main() -> int:
    deploy()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR  {exc}")
        raise SystemExit(1) from exc
