from __future__ import annotations

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

import skill_manager


class SourceIdentityTests(unittest.TestCase):
    def test_normalize_github_https_and_ssh(self) -> None:
        expected = ("Akira-TL", "skills", "https://github.com/Akira-TL/skills.git")
        self.assertEqual(
            skill_manager.normalize_github_source("https://github.com/Akira-TL/skills.git"),
            expected,
        )
        self.assertEqual(
            skill_manager.normalize_github_source("git@github.com:Akira-TL/skills.git"),
            expected,
        )

    def test_non_github_source_is_rejected(self) -> None:
        with self.assertRaises(skill_manager.SkillInstallError):
            skill_manager.normalize_github_source("https://example.com/org/repo.git")


class DiscoveryTests(unittest.TestCase):
    def test_discovery_skips_deprecated(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            active = root / "skills" / "active" / "SKILL.md"
            active.parent.mkdir(parents=True)
            active.write_text("---\nname: active\n---\n", encoding="utf-8")
            deprecated = root / "deprecated" / "old" / "SKILL.md"
            deprecated.parent.mkdir(parents=True)
            deprecated.write_text("---\nname: old\n---\n", encoding="utf-8")

            self.assertEqual(skill_manager.discover_skills(root), {"active": active.parent})


class InstallTests(unittest.TestCase):
    def _fixture_checkout(self, root: Path) -> Path:
        checkout = root / "checkout"
        fixtures = {
            "alpha": checkout / "skills" / "engineering" / "alpha",
            "beta": checkout / "skills" / "productivity" / "beta",
            "ask-akira": checkout / "skills" / "in-progress" / "ask-akira",
            "misc-one": checkout / "skills" / "misc" / "misc-one",
        }
        for name, directory in fixtures.items():
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
        return checkout

    def test_project_install_creates_only_symlink_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            checkout = self._fixture_checkout(root)
            project = root / "project"
            project.mkdir()
            source = "https://github.com/Akira-TL/example.git"
            with mock.patch.object(
                skill_manager,
                "ensure_source_checkout",
                return_value=(checkout, "abc123", source),
            ):
                installed = skill_manager.install_from_source(
                    source,
                    skill_names=["alpha"],
                    project=project,
                )

            self.assertEqual(installed, ["alpha"])
            link = project / ".agents" / "skills" / "alpha"
            self.assertTrue(link.is_symlink())
            self.assertEqual(
                skill_manager.direct_link_target(link),
                (checkout / "skills" / "engineering" / "alpha").absolute(),
            )
            manifest = json.loads(
                (project / ".agents" / "akira-skills.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["skills"]["alpha"]["commit"], "abc123")
            self.assertFalse(manifest["skills"]["alpha"]["forgerelay"])

    def test_global_forgerelay_view_links_to_global_skill_view(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            checkout = self._fixture_checkout(root)
            global_skills = root / ".agents" / "skills"
            global_manifest = root / ".agents" / "akira-skills.json"
            relay_skills = root / ".forgerelay" / "skills"
            source = "https://github.com/Akira-TL/example.git"
            with (
                mock.patch.object(
                    skill_manager,
                    "ensure_source_checkout",
                    return_value=(checkout, "abc123", source),
                ),
                mock.patch.object(skill_manager, "GLOBAL_SKILLS", global_skills),
                mock.patch.object(skill_manager, "GLOBAL_MANIFEST", global_manifest),
                mock.patch.object(skill_manager, "FORGERELAY_SKILLS", relay_skills),
            ):
                skill_manager.install_from_source(
                    source,
                    skill_names=["alpha"],
                    global_scope=True,
                    forgerelay=True,
                )

            canonical = global_skills / "alpha"
            relay = relay_skills / "alpha"
            self.assertTrue(canonical.is_symlink())
            self.assertEqual(
                skill_manager.direct_link_target(canonical),
                (checkout / "skills" / "engineering" / "alpha").absolute(),
            )
            self.assertTrue(relay.is_symlink())
            self.assertEqual(skill_manager.direct_link_target(relay), canonical.absolute())

    def test_all_can_be_limited_by_roots_and_extended_by_explicit_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            checkout = self._fixture_checkout(root)
            project = root / "project"
            project.mkdir()
            source = "https://github.com/Akira-TL/example.git"
            with mock.patch.object(
                skill_manager,
                "ensure_source_checkout",
                return_value=(checkout, "abc123", source),
            ):
                installed = skill_manager.install_from_source(
                    source,
                    skill_names=["ask-akira"],
                    install_all=True,
                    include_roots=["skills/engineering", "skills/productivity"],
                    project=project,
                )

            self.assertEqual(installed, ["alpha", "ask-akira", "beta"])
            self.assertFalse((project / ".agents" / "skills" / "misc-one").exists())

    def test_existing_non_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            source = root / "source"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            with self.assertRaises(skill_manager.SkillInstallError):
                skill_manager.ensure_symlink(source, target)


if __name__ == "__main__":
    unittest.main()
