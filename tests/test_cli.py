from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from lockpeek.cli import main
from lockpeek.core import Holder, Probe


class CliTests(unittest.TestCase):
    def test_json_reports_holder_without_extra_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "report.docx"
            target.write_text("placeholder", encoding="utf-8")
            stdout = io.StringIO()
            probe = Probe(
                path=str(target),
                status="locked",
                holders=(Holder(pid=123, name="Code", source="test"),),
                backend="test",
                message=None,
            )
            with patch("lockpeek.cli.probe_path", return_value=probe):
                with redirect_stdout(stdout):
                    exit_code = main(["--json", str(target)])

        self.assertEqual(0, exit_code)
        payload = json.loads(stdout.getvalue())
        self.assertEqual("locked", payload[0]["status"])
        self.assertEqual(123, payload[0]["holders"][0]["pid"])

    def test_strict_returns_one_for_a_locked_target(self) -> None:
        target = Path("report.docx")
        probe = Probe(
            path=str(target),
            status="locked",
            holders=(Holder(pid=123, name="Code", source="test"),),
            backend="test",
            message=None,
        )
        with patch("lockpeek.cli.probe_path", return_value=probe):
            with redirect_stdout(io.StringIO()):
                exit_code = main(["--strict", str(target)])

        self.assertEqual(1, exit_code)

    def test_missing_path_is_a_reported_error(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["does-not-exist.lockpeek"])

        self.assertEqual(2, exit_code)
        self.assertIn("does not exist", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
