from __future__ import annotations

import argparse
from pathlib import Path

from skill_manager import (
    SkillInstallError,
    doctor,
    install_from_source,
    inspect_source,
    list_installed,
    remove_installed,
    update_installed,
)


def _scope_arguments(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--global", dest="global_scope", action="store_true")
    group.add_argument("--project", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Akira Git + symlink Skill installer. No third-party Skill package manager required."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="只读取 GitHub source 中可用 Skill，不安装")
    inspect.add_argument("source", help="GitHub repository URL")
    inspect.add_argument("--ref", default="main")

    install = sub.add_parser("install", help="从 GitHub source 安装 Skill 软链接")
    install.add_argument("source", help="GitHub repository URL")
    install.add_argument("--skill", action="append", default=[])
    install.add_argument("--all", dest="install_all", action="store_true")
    install.add_argument(
        "--root",
        action="append",
        default=[],
        help="与 --all 一起使用，只安装 source 中该相对目录下的 Skill；可重复",
    )
    install.add_argument("--ref", default="main")
    install.add_argument(
        "--forgerelay",
        action="store_true",
        help="仅全局安装时，把 ~/.forgerelay/skills 链接到 ~/.agents/skills",
    )
    _scope_arguments(install)

    update = sub.add_parser("update", help="更新当前 scope 已安装 Skill 的 Git source")
    update.add_argument("--source", help="只更新该 GitHub source")
    _scope_arguments(update)

    remove = sub.add_parser("remove", help="删除受管 Skill 软链接，不删除 source checkout")
    remove.add_argument("skills", nargs="*")
    remove.add_argument("--source", help="删除该 GitHub source 在当前 scope 的全部 Skill")
    _scope_arguments(remove)

    list_cmd = sub.add_parser("list", help="列出当前 scope 的 Akira-managed Skill")
    _scope_arguments(list_cmd)

    doctor_cmd = sub.add_parser("doctor", help="检查 source 与软链接是否一致")
    _scope_arguments(doctor_cmd)
    return parser


def _project(args: argparse.Namespace) -> Path | None:
    return args.project.resolve() if getattr(args, "project", None) else None


def main() -> int:
    args = build_parser().parse_args()
    global_scope = bool(getattr(args, "global_scope", False))
    project = _project(args)

    if args.command == "inspect":
        for name, path in inspect_source(args.source, args.ref):
            print(f"{name}\t{path}")
        return 0

    if args.command == "install":
        installed = install_from_source(
            args.source,
            skill_names=args.skill,
            install_all=args.install_all,
            include_roots=args.root,
            ref=args.ref,
            global_scope=global_scope,
            project=project,
            forgerelay=args.forgerelay,
        )
        print("INSTALLED " + ", ".join(installed))
        return 0

    if args.command == "update":
        updated = update_installed(
            global_scope=global_scope,
            project=project,
            repository=args.source,
        )
        print("UPDATED " + (", ".join(updated) if updated else "none"))
        return 0

    if args.command == "remove":
        if not args.skills and not args.source:
            raise SkillInstallError("remove 需要 Skill 名称或 --source")
        removed = remove_installed(
            args.skills,
            repository=args.source,
            global_scope=global_scope,
            project=project,
        )
        print("REMOVED " + (", ".join(removed) if removed else "none"))
        return 0

    if args.command == "list":
        for name, repository, commit in list_installed(
            global_scope=global_scope,
            project=project,
        ):
            print(f"{name}\t{repository}\t{commit}")
        return 0

    if args.command == "doctor":
        checked = doctor(global_scope=global_scope, project=project)
        print("OK " + (", ".join(checked) if checked else "no managed skills"))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SkillInstallError as exc:
        raise SystemExit(f"ERROR {exc}") from exc
