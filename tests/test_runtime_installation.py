from __future__ import annotations

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


class InstallBoundaryTests(unittest.TestCase):
    def test_runtime_baseline_uses_remote_github_source(self) -> None:
        with mock.patch.object(install, "install_from_source", return_value=["akira", "browser-access"]) as fn:
            installed = install.install_machine_skills()

        self.assertEqual(installed, ["akira", "browser-access"])
        fn.assert_called_once_with(
            "https://github.com/Akira-TL/skills.git",
            skill_names=("akira", "browser-access"),
        )

    def test_default_runtime_skills_are_minimal_baseline(self) -> None:
        self.assertEqual(install.DEFAULT_MACHINE_SKILLS, ("akira", "browser-access"))
        self.assertEqual(install.AKIRA_SKILLS_SOURCE, "https://github.com/Akira-TL/skills.git")

    def test_installer_no_longer_depends_on_third_party_skill_manager(self) -> None:
        install_source = (SCRIPTS_ROOT / "install.py").read_text(encoding="utf-8")
        manager_source = (SCRIPTS_ROOT / "skill_manager.py").read_text(encoding="utf-8")
        cli_source = (SCRIPTS_ROOT / "skills.py").read_text(encoding="utf-8")
        for source in (install_source, manager_source, cli_source):
            self.assertNotIn("npx skills", source)
            self.assertNotIn("openclaw", source)
            self.assertNotIn("--copy", source)

        for source in (manager_source, cli_source):
            self.assertNotIn("forgerelay", source.lower())
            self.assertNotIn("--project", source)
            self.assertNotIn("claude", source.lower())
            self.assertNotIn("codex", source.lower())


class StaticLinkOwnershipTests(unittest.TestCase):
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

    def test_uninstall_requests_only_baseline_from_skill_manager(self) -> None:
        with mock.patch.object(uninstall, "remove_installed", return_value=["akira", "browser-access"]) as fn:
            uninstall.uninstall_machine_skills()

        fn.assert_called_once_with(("akira", "browser-access"))


if __name__ == "__main__":
    unittest.main()
