from __future__ import annotations

import json
import subprocess
import unittest
from unittest import mock

import install


class SkiloomBootstrapTests(unittest.TestCase):
    def test_require_skiloom_accepts_supported_version(self) -> None:
        completed = subprocess.CompletedProcess(
            ["/usr/bin/skiloom", "--version"],
            0,
            stdout="skiloom 0.8.15\n",
            stderr="",
        )
        with (
            mock.patch.object(install.shutil, "which", return_value="/usr/bin/skiloom"),
            mock.patch.object(install.subprocess, "run", return_value=completed),
        ):
            self.assertEqual(install.require_skiloom(), "/usr/bin/skiloom")

    def test_require_skiloom_rejects_missing_cli(self) -> None:
        with mock.patch.object(install.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "缺少 Skiloom CLI"):
                install.require_skiloom()

    def test_require_skiloom_rejects_old_version(self) -> None:
        completed = subprocess.CompletedProcess(
            ["/usr/bin/skiloom", "--version"],
            0,
            stdout="skiloom 0.8.14\n",
            stderr="",
        )
        with (
            mock.patch.object(install.shutil, "which", return_value="/usr/bin/skiloom"),
            mock.patch.object(install.subprocess, "run", return_value=completed),
        ):
            with self.assertRaisesRegex(RuntimeError, "至少需要 0.8.15"):
                install.require_skiloom()

    def test_bootstrap_installs_only_baseline_direct_requirements(self) -> None:
        payload = json.dumps(
            {
                "schema": "SKILOOM-CLI-V1",
                "ok": True,
                "command": "install",
                "result": {"status": "committed"},
                "warnings": [],
            }
        )
        completed = subprocess.CompletedProcess(
            ["skiloom"],
            0,
            stdout=payload,
            stderr="",
        )
        with (
            mock.patch.object(install, "require_skiloom", return_value="/usr/bin/skiloom"),
            mock.patch.object(install.subprocess, "run", return_value=completed) as run,
        ):
            install.bootstrap_baseline_skills()

        self.assertEqual(run.call_count, 1 + len(install.BASELINE_PACKAGES))
        expected = [
            mock.call(
                [
                    "/usr/bin/skiloom",
                    "install",
                    "akira-tl/skiloom/skiloom",
                    "--git",
                    "main",
                    "--scope",
                    "user",
                    "--yes",
                    "--non-interactive",
                    "--json",
                ],
                capture_output=True,
                text=True,
            ),
            *[
                mock.call(
                    [
                        "/usr/bin/skiloom",
                        "install",
                        coordinate,
                        "--git",
                        "main",
                        "--scope",
                        "user",
                        "--yes",
                        "--non-interactive",
                        "--json",
                    ],
                    capture_output=True,
                    text=True,
                )
                for coordinate in install.BASELINE_PACKAGES
            ],
        ]
        self.assertEqual(run.call_args_list, expected)

    def test_bootstrap_surfaces_structured_skiloom_error(self) -> None:
        payload = json.dumps(
            {
                "schema": "SKILOOM-CLI-V1",
                "ok": False,
                "command": "install",
                "error": {"code": "TargetOccupied", "facts": {"name": "akira"}},
                "warnings": [],
            }
        )
        completed = subprocess.CompletedProcess(
            ["skiloom"],
            1,
            stdout=payload,
            stderr="",
        )
        with (
            mock.patch.object(install, "require_skiloom", return_value="/usr/bin/skiloom"),
            mock.patch.object(install.subprocess, "run", return_value=completed),
        ):
            with self.assertRaisesRegex(RuntimeError, "TargetOccupied"):
                install.bootstrap_baseline_skills()


if __name__ == "__main__":
    unittest.main()
