from __future__ import annotations

import sys
import subprocess
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


class RootInstallBoundaryTests(unittest.TestCase):
    def test_root_runtime_scripts_do_not_own_skill_lifecycle(self) -> None:
        for name in ("install.py", "uninstall.py", "guard.py"):
            source = (SCRIPTS_ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("skill_manager", source)
            self.assertNotIn("akira-skills.json", source)
            self.assertNotIn("~/.agents/sources", source)
            self.assertNotIn("~/.agents/skills", source)

        guard_source = (SCRIPTS_ROOT / "guard.py").read_text(encoding="utf-8")
        self.assertNotIn('HUB / "skills"', guard_source)
        self.assertNotIn("运行时 Skill", guard_source)

    def test_shell_entrypoints_use_uv(self) -> None:
        install_entry = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")
        uninstall_entry = (REPO_ROOT / "uninstall.sh").read_text(encoding="utf-8")
        self.assertIn("exec uv run python scripts/install.py", install_entry)
        self.assertIn("exec uv run python scripts/uninstall.py", uninstall_entry)

    def test_baseline_bootstrap_uses_remote_akira_installer(self) -> None:
        calls: list[list[str]] = []

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if command[:2] == ["git", "clone"]:
                checkout = Path(command[-1])
                installer = checkout / "routing" / "akira" / "scripts" / "skills.py"
                installer.parent.mkdir(parents=True, exist_ok=True)
                installer.write_text("# bootstrap fixture\n", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "", "")

        with mock.patch.object(install.subprocess, "run", side_effect=fake_run):
            install.bootstrap_baseline_skills()

        self.assertEqual(install.BASELINE_SKILLS, ("akira", "browser-access"))
        self.assertEqual(install.AKIRA_SKILLS_SOURCE, "https://github.com/Akira-TL/skills.git")
        self.assertEqual(calls[0][0:2], ["git", "clone"])
        self.assertIn(install.AKIRA_SKILLS_SOURCE, calls[0])
        self.assertNotIn(str(REPO_ROOT / "skills" / "akira"), " ".join(calls[0]))

        install_call = calls[1]
        self.assertEqual(install_call[0], install.sys.executable)
        self.assertEqual(install_call[2:4], ["install", install.AKIRA_SKILLS_SOURCE])
        self.assertEqual(
            install_call[4:],
            ["--skill", "akira", "--skill", "browser-access"],
        )


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


if __name__ == "__main__":
    unittest.main()
