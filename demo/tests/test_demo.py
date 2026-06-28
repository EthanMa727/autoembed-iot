import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

DEMO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO_DIR))

import extract
import llm_client
import mvp
import report


SKETCH = "void setup() {}\nvoid loop() {}\n"
API_TABLE = {
    "component": "sensor",
    "library_include": "#include <Sensor.h>",
    "init": "Sensor.begin()",
    "apis": [],
}


class DemoTests(unittest.TestCase):
    def test_extracts_first_fenced_sketch_without_prose(self):
        reply = "Here is the sketch:\n```cpp\n" + SKETCH + "```"

        self.assertEqual(extract.extract_sketch(reply), SKETCH)

    def test_retry_cap_preserves_last_error_and_sketch_path(self):
        client = mock.Mock()
        client.generate.return_value = SKETCH

        with tempfile.TemporaryDirectory() as directory:
            with (
                mock.patch.object(mvp, "HERE", Path(directory)),
                mock.patch.object(mvp, "compile_sketch", return_value=(False, "compile exploded")),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                record = mvp.run_task(client, "task", "read sensor", API_TABLE, 2)

        self.assertEqual(client.generate.call_count, 2)
        self.assertEqual(record["attempts"], 2)
        self.assertEqual(record["last_error"], "compile exploded")
        self.assertTrue(record["sketch_path"].endswith("task.ino"))

    def test_failure_report_includes_last_error(self):
        record = {
            "id": "task",
            "task": "read sensor",
            "attempts": 2,
            "compiled": False,
            "last_error": "compile exploded",
            "sketch_path": "sketches/task/task.ino",
        }

        rendered = report.render_table([record])

        self.assertIn("## Failure details", rendered)
        self.assertIn("compile exploded", rendered)
        self.assertIn("sketches/task/task.ino", rendered)

    def test_blank_single_task_stops_before_client_creation(self):
        fake_stdin = SimpleNamespace(isatty=lambda: False)

        with (
            mock.patch.object(mvp, "make_client") as make_client,
            mock.patch.object(mvp.sys, "stdin", fake_stdin),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = mvp.main(["--single", "   "])

        self.assertEqual(result, 2)
        make_client.assert_not_called()

    def test_interactive_single_task_asks_again(self):
        fake_stdin = SimpleNamespace(isatty=lambda: True)

        with (
            mock.patch.object(mvp.sys, "stdin", fake_stdin),
            mock.patch("builtins.input", return_value="read sensor"),
        ):
            task_text = mvp.prompt_for_single_task("   ")

        self.assertEqual(task_text, "read sensor")

    def test_skipped_batch_task_is_noted_in_results(self):
        with contextlib.redirect_stderr(io.StringIO()):
            accepted, skipped = mvp.valid_tasks([{"id": "blank", "task": "!!!"}])

        self.assertEqual(accepted, [])
        self.assertIn("SKIPPED (invalid task)", report.render_table(skipped))

    def test_invalid_credentials_are_rejected(self):
        class APIError(Exception):
            pass

        class AuthenticationError(APIError):
            pass

        class PermissionDeniedError(APIError):
            pass

        class Models:
            def list(self, **kwargs):
                raise AuthenticationError()

        client = llm_client.AnthropicClient.__new__(llm_client.AnthropicClient)
        client._anthropic = SimpleNamespace(
            APIError=APIError,
            AuthenticationError=AuthenticationError,
            PermissionDeniedError=PermissionDeniedError,
        )
        client.client = SimpleNamespace(models=Models())

        with self.assertRaisesRegex(llm_client.LLMError, "was rejected"):
            client.validate_credentials()

    def test_main_prints_generated_sketch_path(self):
        client = mock.Mock()
        client.validate_credentials.return_value = "credentials accepted"
        record = {
            "id": "adhoc",
            "task": "read sensor",
            "attempts": 1,
            "compiled": True,
            "last_error": "",
            "sketch_path": "sketches/adhoc/adhoc.ino",
        }

        with (
            mock.patch.object(mvp, "preflight", return_value=(True, "toolchain OK")),
            mock.patch.object(mvp, "make_client", return_value=client),
            mock.patch.object(mvp, "run_task", return_value=record),
            mock.patch.object(mvp, "write_report"),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            result = mvp.main(["--single", "read sensor"])

        self.assertEqual(result, 0)
        self.assertIn("sketch: sketches/adhoc/adhoc.ino", output.getvalue())

    def test_max_attempts_must_be_positive(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                mvp.main(["--max-attempts", "0"])


if __name__ == "__main__":
    unittest.main()
