from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

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

    def test_shell_entrypoints_use_uv(self) -> None:
        install_entry = (REPO_ROOT / "install.sh").read_text(encoding="utf-8")
        uninstall_entry = (REPO_ROOT / "uninstall.sh").read_text(encoding="utf-8")
        self.assertIn("exec uv run python scripts/install.py", install_entry)
        self.assertIn("exec uv run python scripts/uninstall.py", uninstall_entry)


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
