from __future__ import annotations

import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from lockpeek.core import (
    Holder,
    Probe,
    _probe_lsof,
    parse_lsof_output,
    probe_from_holders,
)


class CoreTests(unittest.TestCase):
    def test_parse_lsof_machine_output_groups_process_fields(self) -> None:
        output = (
            "p4012\nccpython\nf3\nn/tmp/report.docx\np9981\ncCode\nn/tmp/report.docx\n"
        )

        holders = parse_lsof_output(output)

        self.assertEqual(
            [
                Holder(pid=4012, name="cpython", source="lsof"),
                Holder(pid=9981, name="Code", source="lsof"),
            ],
            holders,
        )

    def test_parse_lsof_ignores_records_without_a_pid(self) -> None:
        self.assertEqual([], parse_lsof_output("n/tmp/report.docx\ncghost\n"))

    def test_probe_status_is_derived_from_holders(self) -> None:
        locked = probe_from_holders(
            "/tmp/report.docx",
            [Holder(pid=7, name="editor", source="lsof")],
            backend="lsof",
        )
        free = probe_from_holders("/tmp/report.docx", [], backend="lsof")

        self.assertEqual("locked", locked.status)
        self.assertEqual("unlocked", free.status)
        self.assertEqual("editor", locked.holders[0].name)

    def test_probe_dict_is_stable_for_json_output(self) -> None:
        probe = Probe(
            path="report.docx",
            status="unavailable",
            holders=(),
            backend="lsof",
            message="lsof was not found",
        )

        self.assertEqual(
            {
                "path": "report.docx",
                "status": "unavailable",
                "backend": "lsof",
                "message": "lsof was not found",
                "holders": [],
            },
            probe.to_dict(),
        )

    def test_lsof_permission_error_is_not_reported_as_unlocked(self) -> None:
        completed = CompletedProcess(
            args=["lsof"], returncode=1, stdout="", stderr="permission denied"
        )
        with patch("lockpeek.core.shutil.which", return_value="lsof"):
            with patch("lockpeek.core.subprocess.run", return_value=completed):
                result = _probe_lsof(Path("/tmp/report.docx"))

        self.assertEqual("error", result.status)
        self.assertIn("permission denied", result.message or "")


if __name__ == "__main__":
    unittest.main()
