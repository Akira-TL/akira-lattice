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
                install.install_skill_source(
                    "npx", source, "fixture", ("akira", "browser-access")
                )

            command = run.call_args.args[0]
            self.assertEqual(command[:3], ["npx", "skills", "add"])
            skill_index = command.index("--skill")
            self.assertEqual(command[skill_index + 1 : skill_index + 3], ["akira", "browser-access"])
            self.assertNotIn("remove", command)
            self.assertIn("--agent", command)
            agent_index = command.index("--agent")
            self.assertEqual(
                command[agent_index + 1 : agent_index + 3], ["universal", "openclaw"]
            )
            self.assertNotIn("--copy", command)
            self.assertNotIn("--global", command)
            self.assertNotIn("-g", command)
            self.assertEqual(run.call_args.kwargs["cwd"], install.FORGERELAY_HOME)

    def test_default_runtime_skills_are_minimal_common_baseline(self) -> None:
        self.assertEqual(install.DEFAULT_RUNTIME_SKILLS, ("akira", "browser-access"))
        self.assertEqual(
            install.FORGERELAY_CANONICAL_SKILLS,
            Path.home() / ".forgerelay" / ".agents" / "skills",
        )
        self.assertEqual(install.FORGERELAY_SKILLS, Path.home() / ".forgerelay" / "skills")
        source = (SCRIPTS_ROOT / "install.py").read_text(encoding="utf-8")
        self.assertNotIn("install_skill_source(npx, MATT_SKILLS_ROOT", source)
        self.assertNotIn("install_skill_source(npx, RESEARCH_SKILLS_ROOT", source)

    def test_runtime_requires_symlink_to_npx_canonical_store(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            canonical = root / ".agents" / "skills"
            runtime = root / "skills"
            for name in install.DEFAULT_RUNTIME_SKILLS:
                source = canonical / name
                source.mkdir(parents=True, exist_ok=True)
                (source / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")
                runtime.mkdir(parents=True, exist_ok=True)
                (runtime / name).symlink_to(Path("..") / ".agents" / "skills" / name)

            with (
                mock.patch.object(install, "FORGERELAY_CANONICAL_SKILLS", canonical),
                mock.patch.object(install, "FORGERELAY_SKILLS", runtime),
                mock.patch.object(install, "find_npx", return_value="npx"),
                mock.patch.object(install, "discover_skill_names", return_value=list(install.DEFAULT_RUNTIME_SKILLS)),
                mock.patch.object(install, "install_skill_source"),
            ):
                self.assertEqual(
                    install.install_runtime_skills(), sorted(install.DEFAULT_RUNTIME_SKILLS)
                )

    def test_installer_contains_no_cleanup_or_uninstall_route(self) -> None:
        source = (SCRIPTS_ROOT / "install.py").read_text(encoding="utf-8")
        for forbidden in (
            "skills remove",
            "visible-browser-form-automation",
            "cleanup_legacy",
            "migrate_legacy_backups",
            "remote\", \"set-url",
            "openai-plugins",
            "external/ngs-analysis",
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
                mock.patch.object(uninstall, "FORGERELAY_SKILLS", root / "skills"),
            ):
                self.assertEqual(uninstall.installed_project_skills(), [])

    def test_manifest_hash_must_match_current_runtime_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills = root / "skills"
            skill_file = skills / "example" / "SKILL.md"
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
                mock.patch.object(uninstall, "FORGERELAY_SKILLS", skills),
            ):
                self.assertEqual(uninstall.installed_project_skills(), [])

    def test_matching_manifest_hash_is_owned(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            skills = root / "skills"
            content = b"installed\n"
            skill_file = skills / "example" / "SKILL.md"
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
                mock.patch.object(uninstall, "FORGERELAY_SKILLS", skills),
            ):
                self.assertEqual(uninstall.installed_project_skills(), ["example"])


if __name__ == "__main__":
    unittest.main()
