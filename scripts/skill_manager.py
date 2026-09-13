from __future__ import annotations

import json
import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HOME = Path.home()
AGENTS_HOME = HOME / ".agents"
SOURCES_ROOT = AGENTS_HOME / "sources"
GLOBAL_SKILLS = AGENTS_HOME / "skills"
GLOBAL_MANIFEST = AGENTS_HOME / "akira-skills.json"
FORGERELAY_SKILLS = HOME / ".forgerelay" / "skills"
NAME_PATTERN = re.compile(r"^name:\s*([^\s#]+)\s*$")
MANIFEST_VERSION = 1


class SkillInstallError(RuntimeError):
    pass


def _run_git(args: list[str], cwd: Path | None = None, capture: bool = False) -> str:
    command = ["git", *args]
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if result.returncode != 0:
        detail = ""
        if capture:
            detail = (result.stderr or result.stdout or "").strip()
        suffix = f"：{detail}" if detail else ""
        raise SkillInstallError(f"Git 命令失败：{' '.join(command)}{suffix}")
    return result.stdout.strip() if capture else ""


def normalize_github_source(source: str) -> tuple[str, str, str]:
    value = source.strip()
    if value.startswith("git@github.com:"):
        repo_path = value.removeprefix("git@github.com:")
    else:
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
            raise SkillInstallError(
                "当前 Akira 安装器只接受 GitHub HTTPS 或 git@github.com SSH source"
            )
        repo_path = parsed.path.lstrip("/")

    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    parts = [part for part in repo_path.split("/") if part]
    if len(parts) != 2:
        raise SkillInstallError(f"GitHub source 必须是 OWNER/REPO：{source}")
    owner, repo = parts
    canonical = f"https://github.com/{owner}/{repo}.git"
    return owner, repo, canonical


def source_checkout_path(source: str) -> Path:
    owner, repo, _ = normalize_github_source(source)
    return SOURCES_ROOT / owner / repo


def _normalize_remote_url(url: str) -> str:
    try:
        return normalize_github_source(url)[2]
    except SkillInstallError:
        return url.rstrip("/")


def ensure_source_checkout(source: str, ref: str = "main") -> tuple[Path, str, str]:
    owner, repo, canonical = normalize_github_source(source)
    checkout = SOURCES_ROOT / owner / repo
    checkout.parent.mkdir(parents=True, exist_ok=True)

    if not checkout.exists():
        _run_git(["clone", "--origin", "origin", canonical, str(checkout)])
    elif not (checkout / ".git").exists():
        raise SkillInstallError(f"Source 目标已存在但不是 Git repository：{checkout}")

    actual_remote = _run_git(["remote", "get-url", "origin"], cwd=checkout, capture=True)
    if _normalize_remote_url(actual_remote) != canonical:
        raise SkillInstallError(
            f"Source checkout origin 不匹配：{checkout}\n"
            f"当前：{actual_remote}\n预期：{canonical}"
        )

    dirty = _run_git(["status", "--porcelain"], cwd=checkout, capture=True)
    if dirty:
        raise SkillInstallError(
            f"Source checkout 存在本地修改，拒绝覆盖：{checkout}\n{dirty}"
        )

    _run_git(["fetch", "--prune", "origin"], cwd=checkout)
    remote_ref = f"refs/remotes/origin/{ref}"
    remote_branch_exists = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", remote_ref],
        cwd=checkout,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    if remote_branch_exists:
        _run_git(["checkout", "-B", ref, f"origin/{ref}"], cwd=checkout)
    else:
        _run_git(["checkout", "--detach", ref], cwd=checkout)

    commit = _run_git(["rev-parse", "HEAD"], cwd=checkout, capture=True)
    return checkout, commit, canonical


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


def discover_skills(checkout: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for skill_file in sorted(checkout.rglob("SKILL.md")):
        relative = skill_file.relative_to(checkout)
        if ".git" in relative.parts or "deprecated" in relative.parts:
            continue
        name = skill_name(skill_file)
        if not name:
            continue
        skill_dir = skill_file.parent
        if name in found and found[name] != skill_dir:
            raise SkillInstallError(
                f"同一 source 中发现重复 Skill name `{name}`："
                f"{found[name]} 与 {skill_dir}"
            )
        found[name] = skill_dir
    return found


def direct_link_target(path: Path) -> Path:
    raw_target = Path(os.readlink(path))
    if raw_target.is_absolute():
        return Path(os.path.abspath(raw_target))
    return Path(os.path.abspath(path.parent / raw_target))


def ensure_symlink(source: Path, target: Path) -> None:
    source = source.expanduser().absolute()
    if not source.exists():
        raise SkillInstallError(f"软链接 source 不存在：{source}")
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.is_symlink():
        if direct_link_target(target) == source:
            return
        raise SkillInstallError(
            f"目标已是指向其他位置的软链接：{target} -> {direct_link_target(target)}"
        )
    if target.exists():
        raise SkillInstallError(
            f"目标已存在且不是软链接，拒绝覆盖：{target}\n"
            "请先确认其来源后手工迁移或删除。"
        )

    target.symlink_to(source, target_is_directory=True)
    print(f"LINK   {target} -> {source}")


def _scope_paths(global_scope: bool, project: Path | None) -> tuple[Path, Path]:
    if global_scope:
        return GLOBAL_SKILLS, GLOBAL_MANIFEST
    project_root = (project or Path.cwd()).expanduser().resolve()
    return project_root / ".agents" / "skills", project_root / ".agents" / "akira-skills.json"


def _empty_manifest(scope: str) -> dict[str, object]:
    return {
        "version": MANIFEST_VERSION,
        "scope": scope,
        "skills": {},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def load_manifest(path: Path, scope: str) -> dict[str, object]:
    if not path.is_file():
        return _empty_manifest(scope)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillInstallError(f"无法读取 Akira Skill manifest：{path}: {exc}") from exc
    if payload.get("version") != MANIFEST_VERSION or not isinstance(payload.get("skills"), dict):
        raise SkillInstallError(f"Akira Skill manifest 格式不受支持：{path}")
    return payload


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    print(f"STATE  {path}")


def install_from_source(
    source: str,
    *,
    skill_names: list[str] | tuple[str, ...] | None = None,
    install_all: bool = False,
    include_roots: list[str] | tuple[str, ...] | None = None,
    ref: str = "main",
    global_scope: bool = False,
    project: Path | None = None,
    forgerelay: bool = False,
) -> list[str]:
    if not install_all and not skill_names:
        raise SkillInstallError("必须指定至少一个 `--skill`，或使用 `--all`")
    if include_roots and not install_all:
        raise SkillInstallError("`--root` 只与 `--all` 一起使用")
    if forgerelay and not global_scope:
        raise SkillInstallError("ForgeRelay 全局视图只能链接全局 ~/.agents/skills")

    checkout, commit, canonical = ensure_source_checkout(source, ref)
    available = discover_skills(checkout)
    selected_set = set(skill_names or [])
    if install_all:
        roots = [Path(root) for root in (include_roots or [])]
        for name, skill_dir in available.items():
            relative = skill_dir.relative_to(checkout)
            if not roots or any(relative == root or root in relative.parents for root in roots):
                selected_set.add(name)
    selected = sorted(selected_set)
    missing = [name for name in selected if name not in available]
    if missing:
        raise SkillInstallError(
            f"Source 中不存在以下 Skill：{', '.join(missing)}\nSource: {canonical}"
        )

    skill_root, manifest_path = _scope_paths(global_scope, project)
    scope_name = "global" if global_scope else str((project or Path.cwd()).expanduser().resolve())
    manifest = load_manifest(manifest_path, scope_name)
    entries = manifest["skills"]
    assert isinstance(entries, dict)

    for name in selected:
        source_dir = available[name].absolute()
        target = skill_root / name
        ensure_symlink(source_dir, target)
        if forgerelay:
            ensure_symlink(target.absolute(), FORGERELAY_SKILLS / name)
        entries[name] = {
            "repository": canonical,
            "ref": ref,
            "commit": commit,
            "source_path": source_dir.relative_to(checkout).as_posix(),
            "forgerelay": bool(forgerelay),
        }

    write_manifest(manifest_path, manifest)
    return selected


def _selected_manifest_path(global_scope: bool, project: Path | None) -> tuple[Path, Path, str]:
    skill_root, manifest_path = _scope_paths(global_scope, project)
    scope_name = "global" if global_scope else str((project or Path.cwd()).expanduser().resolve())
    return skill_root, manifest_path, scope_name


def update_installed(
    *,
    global_scope: bool = False,
    project: Path | None = None,
    repository: str | None = None,
) -> list[str]:
    skill_root, manifest_path, scope_name = _selected_manifest_path(global_scope, project)
    manifest = load_manifest(manifest_path, scope_name)
    entries = manifest["skills"]
    assert isinstance(entries, dict)
    if not entries:
        return []

    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for name, metadata in entries.items():
        if not isinstance(metadata, dict):
            raise SkillInstallError(f"Manifest Skill metadata 无效：{name}")
        repo = metadata.get("repository")
        ref = metadata.get("ref", "main")
        if not isinstance(repo, str) or not isinstance(ref, str):
            raise SkillInstallError(f"Manifest Skill source 无效：{name}")
        if repository and _normalize_remote_url(repo) != _normalize_remote_url(repository):
            continue
        grouped[(repo, ref)].append(name)

    updated: list[str] = []
    for (repo, ref), names in grouped.items():
        checkout, commit, canonical = ensure_source_checkout(repo, ref)
        available = discover_skills(checkout)
        for name in names:
            metadata = entries[name]
            assert isinstance(metadata, dict)
            if name not in available:
                raise SkillInstallError(f"更新后 source 已不存在 Skill `{name}`：{canonical}")
            source_dir = available[name].absolute()
            target = skill_root / name
            if not target.is_symlink() or direct_link_target(target) != source_dir:
                raise SkillInstallError(f"已安装 Skill 软链接漂移：{target}")
            if bool(metadata.get("forgerelay")):
                relay = FORGERELAY_SKILLS / name
                if not relay.is_symlink() or direct_link_target(relay) != target.absolute():
                    raise SkillInstallError(f"ForgeRelay Skill 软链接漂移：{relay}")
            metadata["repository"] = canonical
            metadata["commit"] = commit
            metadata["source_path"] = source_dir.relative_to(checkout).as_posix()
            updated.append(name)

    write_manifest(manifest_path, manifest)
    return sorted(updated)


def remove_installed(
    names: list[str] | tuple[str, ...] | None = None,
    *,
    repository: str | None = None,
    global_scope: bool = False,
    project: Path | None = None,
) -> list[str]:
    skill_root, manifest_path, scope_name = _selected_manifest_path(global_scope, project)
    manifest = load_manifest(manifest_path, scope_name)
    entries = manifest["skills"]
    assert isinstance(entries, dict)

    requested = set(names or [])
    selected: list[str] = []
    for name, metadata in entries.items():
        if not isinstance(metadata, dict):
            continue
        if requested and name not in requested:
            continue
        if repository:
            repo = metadata.get("repository")
            if not isinstance(repo, str) or _normalize_remote_url(repo) != _normalize_remote_url(repository):
                continue
        selected.append(name)

    if requested:
        missing = sorted(requested.difference(entries))
        if missing:
            raise SkillInstallError(f"Manifest 中未安装：{', '.join(missing)}")

    for name in selected:
        metadata = entries[name]
        assert isinstance(metadata, dict)
        repo = metadata.get("repository")
        source_path = metadata.get("source_path")
        if not isinstance(repo, str) or not isinstance(source_path, str):
            raise SkillInstallError(f"Manifest Skill metadata 无效：{name}")
        expected_source = source_checkout_path(repo) / source_path
        target = skill_root / name
        if target.is_symlink():
            if direct_link_target(target) != expected_source.absolute():
                raise SkillInstallError(f"拒绝删除指向其他来源的 Skill：{target}")
            target.unlink()
            print(f"REMOVE {target}")
        elif target.exists():
            raise SkillInstallError(f"拒绝删除非软链接 Skill：{target}")

        if bool(metadata.get("forgerelay")):
            relay = FORGERELAY_SKILLS / name
            if relay.is_symlink():
                if direct_link_target(relay) != target.absolute():
                    raise SkillInstallError(f"拒绝删除指向其他来源的 ForgeRelay link：{relay}")
                relay.unlink()
                print(f"REMOVE {relay}")
            elif relay.exists():
                raise SkillInstallError(f"拒绝删除非软链接 ForgeRelay Skill：{relay}")
        del entries[name]

    write_manifest(manifest_path, manifest)
    return sorted(selected)


def doctor(
    *,
    global_scope: bool = False,
    project: Path | None = None,
) -> list[str]:
    skill_root, manifest_path, scope_name = _selected_manifest_path(global_scope, project)
    manifest = load_manifest(manifest_path, scope_name)
    entries = manifest["skills"]
    assert isinstance(entries, dict)
    checked: list[str] = []

    for name, metadata in sorted(entries.items()):
        if not isinstance(metadata, dict):
            raise SkillInstallError(f"Manifest Skill metadata 无效：{name}")
        repo = metadata.get("repository")
        source_path = metadata.get("source_path")
        if not isinstance(repo, str) or not isinstance(source_path, str):
            raise SkillInstallError(f"Manifest Skill source 无效：{name}")
        checkout = source_checkout_path(repo)
        source_dir = checkout / source_path
        if not (source_dir / "SKILL.md").is_file():
            raise SkillInstallError(f"Source Skill 缺失：{source_dir}")
        link = skill_root / name
        if not link.is_symlink() or direct_link_target(link) != source_dir.absolute():
            raise SkillInstallError(f"Skill 软链接无效：{link}")
        if bool(metadata.get("forgerelay")):
            relay = FORGERELAY_SKILLS / name
            if not relay.is_symlink() or direct_link_target(relay) != link.absolute():
                raise SkillInstallError(f"ForgeRelay 软链接无效：{relay}")
        checked.append(name)

    return checked


def inspect_source(source: str, ref: str = "main") -> list[tuple[str, str]]:
    checkout, _, _ = ensure_source_checkout(source, ref)
    rows: list[tuple[str, str]] = []
    for name, skill_dir in sorted(discover_skills(checkout).items()):
        rows.append((name, skill_dir.relative_to(checkout).as_posix()))
    return rows


def list_installed(
    *,
    global_scope: bool = False,
    project: Path | None = None,
) -> list[tuple[str, str, str]]:
    _, manifest_path, scope_name = _selected_manifest_path(global_scope, project)
    manifest = load_manifest(manifest_path, scope_name)
    entries = manifest["skills"]
    assert isinstance(entries, dict)
    rows: list[tuple[str, str, str]] = []
    for name, metadata in sorted(entries.items()):
        if not isinstance(metadata, dict):
            continue
        rows.append(
            (
                name,
                str(metadata.get("repository", "")),
                str(metadata.get("commit", "")),
            )
        )
    return rows
