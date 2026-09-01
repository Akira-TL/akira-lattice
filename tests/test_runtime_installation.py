from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

import install
import uninstall


class SkillDiscoveryTests(unittest.TestCase):
    def test_discovery_skips_deprecated_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            active = root / "productivity" / "browser-access" / "SKILL.md"
            active.parent.mkdir(parents=True)
            active.write_text("---\nname: browser-access\n---\n", encoding="utf-8")

            deprecated = root / "deprecated" / "old-browser" / "SKILL.md"
            deprecated.parent.mkdir(parents=True)
            deprecated.write_text("---\nname: old-browser\n---\n", encoding="utf-8")

            self.assertEqual(install.discover_skill_names(root), ["browser-access"])


class InstallBoundaryTests(unittest.TestCase):
    def test_skill_installation_uses_add_command(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            source = Path(tempdir)
            with mock.patch.object(install.subprocess, "run") as run:
                run.return_value.returncode = 0
                install.install_skill_source("npx", source, "fixture")

            command = run.call_args.args[0]
            self.assertEqual(command[:3], ["npx", "skills", "add"])
            self.assertNotIn("remove", command)

    def test_installer_contains_no_cleanup_or_uninstall_route(self) -> None:
        source = (SCRIPTS_ROOT / "install.py").read_text(encoding="utf-8")
        for forbidden in (
            "skills remove",
            "visible-browser-form-automation",
            "cleanup_legacy",
            "migrate_legacy_backups",
            "remote\", \"set-url",
        ):
            self.assertNotIn(forbidden, source)


class UninstallOwnershipTests(unittest.TestCase):
    def test_foreign_symlink_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            owned = root / "owned"
            foreign = root / "foreign"
            target = root / "target"
            owned.write_text("owned\n", encoding="utf-8")
            foreign.write_text("foreign\n", encoding="utf-8")
            target.symlink_to(foreign)

            uninstall.remove_owned_link(owned, target)

            self.assertTrue(target.is_symlink())
            self.assertEqual(uninstall.direct_link_target(target), foreign.absolute())

    def test_no_manifest_means_no_skill_removal_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            with (
                mock.patch.object(uninstall, "INSTALL_MANIFEST", root / "missing.json"),
                mock.patch.object(uninstall, "HUB", root / "hub"),
            ):
                self.assertEqual(uninstall.installed_project_skills(), [])

    def test_manifest_hash_must_match_current_runtime_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            hub = root / "hub"
            skill_file = hub / "skills" / "example" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text("current\n", encoding="utf-8")

            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "skills": {
                            "example": {
                                "skill_md_sha256": hashlib.sha256(b"installed\n").hexdigest()
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch.object(uninstall, "INSTALL_MANIFEST", manifest),
                mock.patch.object(uninstall, "HUB", hub),
            ):
                self.assertEqual(uninstall.installed_project_skills(), [])

    def test_matching_manifest_hash_is_owned(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            hub = root / "hub"
            content = b"installed\n"
            skill_file = hub / "skills" / "example" / "SKILL.md"
            skill_file.parent.mkdir(parents=True)
            skill_file.write_bytes(content)

            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "skills": {
                            "example": {
                                "skill_md_sha256": hashlib.sha256(content).hexdigest()
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            with (
                mock.patch.object(uninstall, "INSTALL_MANIFEST", manifest),
                mock.patch.object(uninstall, "HUB", hub),
            ):
                self.assertEqual(uninstall.installed_project_skills(), ["example"])


if __name__ == "__main__":
    unittest.main()
