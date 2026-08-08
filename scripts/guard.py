from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parent
CORE_ROOT = REPO_ROOT / "core"
HUB = Path.home() / ".agents"

DYNAMIC_LIMIT = 800
STATIC_LIMIT = 1000
DIRECT_FILE_LIMIT = 8
CORE_LINE_LIMIT = 200

DYNAMIC_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx"}
STATIC_EXTENSIONS = {".java", ".go", ".rs"}
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "target",
    "vendor",
    "__pycache__",
}
COMMIT_RE = re.compile(
    r"^(FIX|FEAT|REFACTOR|TEST|DOCS|CHORE): "
    r"\(([a-z0-9][a-z0-9-]*)\) (\S.*\S|\S)$"
)
VAGUE_DETAILS = {"更新代码", "修复问题", "调整逻辑"}


def ok(message: str) -> None:
    print(f"OK    {message}")


def warn(message: str) -> None:
    print(f"WARN  {message}")


def fail(message: str) -> None:
    print(f"FAIL  {message}")


def run_git(
    args: list[str],
    cwd: Path,
    *,
    check: bool = False,
    text: bool = True,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=check,
        capture_output=True,
        text=text,
    )


def git_root(path: Path) -> Path | None:
    result = run_git(["rev-parse", "--show-toplevel"], path)
    if result.returncode != 0:
        return None
    return Path(str(result.stdout).strip()).resolve()


def line_count_bytes(data: bytes) -> int:
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def line_limit(path: Path) -> int | None:
    suffix = path.suffix.lower()
    if suffix in DYNAMIC_EXTENSIONS:
        return DYNAMIC_LIMIT
    if suffix in STATIC_EXTENSIONS:
        return STATIC_LIMIT
    return None


def is_ignored_relative(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def architecture_scan_tree(root: Path) -> list[str]:
    violations: list[str] = []

    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        current = Path(current_root)
        relative_dir = current.relative_to(root)

        direct_files = [name for name in filenames if name != ".DS_Store"]
        if len(direct_files) > DIRECT_FILE_LIMIT:
            violations.append(
                f"{relative_dir if relative_dir.parts else Path('.')} 直接文件 "
                f"{len(direct_files)} 个，超过 {DIRECT_FILE_LIMIT} 个"
            )

        for filename in filenames:
            path = current / filename
            relative = path.relative_to(root)
            if is_ignored_relative(relative):
                continue
            limit = line_limit(path)
            if limit is None or not path.is_file():
                continue
            try:
                count = line_count_bytes(path.read_bytes())
            except OSError as exc:
                warn(f"无法读取 {relative}: {exc}")
                continue
            if count > limit:
                violations.append(f"{relative} 为 {count} 行，超过 {limit} 行阈值")

    return violations


def git_bytes(root: Path, spec: str) -> bytes | None:
    result = run_git(["show", spec], root, text=False)
    if result.returncode != 0:
        return None
    return bytes(result.stdout)


def git_paths(root: Path, args: list[str]) -> list[Path]:
    result = run_git(args, root, text=False)
    if result.returncode != 0:
        return []
    raw = bytes(result.stdout)
    return [Path(os.fsdecode(item)) for item in raw.split(b"\0") if item]


def directory_counts(paths: Iterable[Path]) -> Counter[Path]:
    counter: Counter[Path] = Counter()
    for path in paths:
        if not is_ignored_relative(path):
            counter[path.parent] += 1
    return counter


def architecture_scan_staged(root: Path) -> list[str]:
    changed = git_paths(
        root,
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
    )
    violations: list[str] = []

    for relative in changed:
        if is_ignored_relative(relative):
            continue
        limit = line_limit(relative)
        if limit is None:
            continue
        staged = git_bytes(root, f":{relative.as_posix()}")
        if staged is None:
            continue
        current_count = line_count_bytes(staged)
        if current_count <= limit:
            continue

        baseline = git_bytes(root, f"HEAD:{relative.as_posix()}")
        baseline_count = line_count_bytes(baseline) if baseline is not None else 0
        if baseline is None or baseline_count <= limit or current_count > baseline_count:
            violations.append(
                f"{relative} 暂存版本为 {current_count} 行，超过 {limit} 行阈值"
            )

    current_files = git_paths(root, ["ls-files", "-z"])
    baseline_files = git_paths(root, ["ls-tree", "-r", "--name-only", "-z", "HEAD"])
    current_counts = directory_counts(current_files)
    baseline_counts = directory_counts(baseline_files)
    changed_parents = {path.parent for path in changed}

    for directory in sorted(changed_parents, key=str):
        current = current_counts[directory]
        baseline = baseline_counts[directory]
        if current > DIRECT_FILE_LIMIT and current > baseline:
            violations.append(
                f"{directory if directory.parts else Path('.')} 暂存后直接文件 "
                f"{current} 个，超过 {DIRECT_FILE_LIMIT} 个"
            )

    return violations


def report_architecture(violations: list[str]) -> int:
    if not violations:
        ok("未发现代码规模阈值问题")
        return 0
    for message in violations:
        warn(message)
    return 1


def validate_commit_message(message: str) -> list[str]:
    lines = message.splitlines()
    if not lines or any(not line.strip() for line in lines):
        return ["提交信息不得包含空行"]

    errors: list[str] = []
    for index, line in enumerate(lines, start=1):
        match = COMMIT_RE.fullmatch(line)
        if match is None:
            errors.append(f"第 {index} 行必须符合 <TYPE>: (<SCOPE>) <DETAIL>")
            continue
        detail = match.group(3).strip()
        if detail in VAGUE_DETAILS:
            errors.append(f"第 {index} 行 DETAIL 过于模糊：{detail}")
    return errors


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


def cmd_config(_: argparse.Namespace) -> int:
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

    core_lines = len((CORE_ROOT / "AGENTS.md").read_text(encoding="utf-8").splitlines())
    if core_lines <= CORE_LINE_LIMIT:
        ok(f"Core 长度 {core_lines} 行")
    else:
        fail(f"Core 已增长到 {core_lines} 行，应重新分层")
        failed = True

    for skill in ("ask-matt", "devspace-orchestration"):
        path = HUB / "skills" / skill / "SKILL.md"
        if path.is_file():
            ok(f"运行时 Skill: {skill}")
        else:
            fail(f"缺少运行时 Skill: {skill}")
            failed = True

    if (HUB / ".skill-lock.json").is_file():
        print("INFO  .skill-lock.json 继续由 skills CLI 管理")
    return 1 if failed else 0


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    try:
        _, block, _ = text.split("---", 2)
    except ValueError:
        return {}
    result: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def cmd_skills(_: argparse.Namespace) -> int:
    failed = False
    names: Counter[str] = Counter()

    for skill_file in sorted((REPO_ROOT / "skills").glob("*/*/SKILL.md")):
        relative = skill_file.relative_to(REPO_ROOT)
        category = relative.parts[1]
        directory_name = skill_file.parent.name
        frontmatter = parse_frontmatter(skill_file)
        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", directory_name):
            fail(f"{relative}: 目录名不是 lowercase kebab-case")
            failed = True
        if name != directory_name:
            fail(f"{relative}: frontmatter name={name!r} 与目录名不一致")
            failed = True
        if not description:
            fail(f"{relative}: 缺少 description")
            failed = True
        if name:
            names[name] += 1

        if category not in {"in-progress", "deprecated"}:
            doc = REPO_ROOT / "docs" / category / f"{directory_name}.md"
            if not doc.is_file():
                fail(f"{relative}: 稳定 Skill 缺少 {doc.relative_to(REPO_ROOT)}")
                failed = True

    for name, count in names.items():
        if count > 1:
            fail(f"Skill name 重复：{name} × {count}")
            failed = True

    if not failed:
        ok("Skill 结构与文档映射正常")
    return 1 if failed else 0


def cmd_architecture(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser().resolve()
    if args.staged:
        root = git_root(target)
        if root is None:
            fail(f"{target} 不是 Git 仓库")
            return 1
        return report_architecture(architecture_scan_staged(root))
    return report_architecture(architecture_scan_tree(target))


def cmd_commit(args: argparse.Namespace) -> int:
    message_errors = validate_commit_message(args.message)
    if message_errors:
        for error in message_errors:
            fail(error)
        return 1

    root = git_root(Path.cwd())
    if root is None:
        fail("当前目录不在 Git 仓库中")
        return 1

    staged = run_git(["diff", "--cached", "--quiet"], root)
    if staged.returncode == 0:
        fail("没有暂存修改；先检查 diff ownership 并选择性暂存当前原子修改")
        return 1

    violations = architecture_scan_staged(root)
    if violations:
        report_architecture(violations)
        if not args.allow_architecture_warnings:
            fail("架构阈值检查未通过；处理后重试，或确认合理后显式使用 --allow-architecture-warnings")
            return 2

    staged_paths = git_paths(
        root,
        ["diff", "--cached", "--name-only", "--diff-filter=ACMRD", "-z"],
    )
    print("INFO  即将提交暂存修改：")
    for path in staged_paths:
        print(f"      {path}")

    result = subprocess.run(["git", "-C", str(root), "commit", "-m", args.message])
    return result.returncode


def report_git_structure(target: Path) -> None:
    root = git_root(target)
    if root is None:
        print("INFO  当前路径不是 Git 仓库，跳过分支/worktree 概览")
        return

    branches = run_git(["branch", "-vv"], root)
    worktrees = run_git(["worktree", "list"], root)

    print("INFO  本地分支：")
    branch_text = str(branches.stdout).rstrip()
    print(branch_text if branch_text else "      (无)")

    print("INFO  worktree：")
    worktree_text = str(worktrees.stdout).rstrip()
    print(worktree_text if worktree_text else "      (无)")


def cmd_check(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser().resolve()
    results = [cmd_architecture(argparse.Namespace(path=str(target), staged=False))]
    report_git_structure(target)

    if target == REPO_ROOT.resolve():
        results.append(cmd_config(argparse.Namespace()))
        results.append(cmd_skills(argparse.Namespace()))

    return 1 if any(results) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Akira Agent 配置与工程约束的统一机械检查入口。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config", help="检查全局 Agent 静态配置部署")
    config_parser.set_defaults(func=cmd_config)

    architecture_parser = subparsers.add_parser("architecture", help="检查代码规模与目录规模")
    architecture_parser.add_argument("path", nargs="?", default=".")
    architecture_parser.add_argument(
        "--staged",
        action="store_true",
        help="只检查当前 Git 暂存修改是否新引入或加重规模问题",
    )
    architecture_parser.set_defaults(func=cmd_architecture)

    skills_parser = subparsers.add_parser("skills", help="检查 akira-skills 的 Skill 结构")
    skills_parser.set_defaults(func=cmd_skills)

    commit_parser = subparsers.add_parser("commit", help="验证提交信息和暂存架构后执行 Git commit")
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.add_argument(
        "--allow-architecture-warnings",
        action="store_true",
        help="明确接受已审查的代码规模阈值告警后继续提交",
    )
    commit_parser.set_defaults(func=cmd_commit)

    check_parser = subparsers.add_parser("check", help="运行当前项目适用的机械检查")
    check_parser.add_argument("path", nargs="?", default=".")
    check_parser.set_defaults(func=cmd_check)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
